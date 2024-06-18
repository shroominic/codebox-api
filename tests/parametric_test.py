import asyncio
import time
from typing import Callable

import pytest
from codeboxapi import CodeBox
from codeboxapi.schema import CodeBoxFile, CodeBoxOutput

AssertFunctionType = Callable[[CodeBoxOutput, list[CodeBoxFile]], bool]

code_1 = """
import pandas as pd
# Read the CSV file
df = pd.read_csv('iris.csv')

# Save the DataFrame to an Excel file
df.to_excel('iris.xlsx', index=False)
"""


def assert_function_1(_, files):
    return any(".xlsx" in file.name for file in files)


code_2 = """
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# Load the dataset
data = pd.read_csv('advertising.csv')

# Split the data into features (X) and target (y)
X = data[['TV']]
y = data['Sales']

# Split the data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)

# Train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test)

# Calculate Mean Squared Error
mse = mean_squared_error(y_test, y_pred)

mse
"""


def assert_function_2(output, _):
    # np.float64(5.179525402166653)\n
    if "np.float64" in output.content:
        return 4.0 <= float(output.content.split("(")[1].split(")")[0]) <= 7.0
    return 4.0 <= float(output.content) <= 7.0


# Helper function to build parameters with defaults
def param(code, assert_function, files=[], num_samples=2, local=False, packages=[]):
    return (
        code,
        assert_function,
        files,
        num_samples,
        local,
        packages,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "code, assert_function, files, num_samples, local, packages",
    [
        param(
            code_1,
            assert_function_1,
            files=[CodeBoxFile.from_path("examples/assets/iris.csv")],
        ),
        param(
            code_1,
            assert_function_1,
            files=[CodeBoxFile.from_path("examples/assets/iris.csv")],
            num_samples=1,
            local=True,
            packages=["pandas", "openpyxl"],
        ),
        param(
            code_2,
            assert_function_2,
            files=[CodeBoxFile.from_path("examples/assets/advertising.csv")],
        ),
        param(
            code_2,
            assert_function_2,
            files=[CodeBoxFile.from_path("examples/assets/advertising.csv")],
            num_samples=10,
        ),  # For remote CodeBox, the time taken to run 10 samples
        #   should be around the same as 2 samples (the above case).
        param(
            code_2,
            assert_function_2,
            files=[CodeBoxFile.from_path("examples/assets/advertising.csv")],
            num_samples=1,
            local=True,
            packages=["pandas", "scikit-learn"],
        ),
    ],
)
async def test_boxes_async(
    code: str,
    assert_function: AssertFunctionType,
    files: list[CodeBoxFile],
    num_samples: int,
    local: bool,
    packages: list[str],
    capsys: pytest.CaptureFixture,
) -> None:
    codeboxes = [CodeBox(local=local) for _ in range(num_samples)]

    start_time = time.perf_counter()
    tasks = [
        run_async(codebox, code, assert_function, files, packages)
        for codebox in codeboxes
    ]
    results = await asyncio.gather(*tasks)
    end_time = time.perf_counter()
    with capsys.disabled():
        print(f"Time taken: {end_time - start_time:.2f} seconds")

    assert all(results), "Failed to run codeboxes"


async def run_async(
    codebox: CodeBox,
    code: str,
    assert_function: AssertFunctionType,
    files: list[CodeBoxFile],
    packages: list[str],
) -> bool:
    try:
        assert await codebox.astart() == "started"

        assert await codebox.astatus() == "running"

        orginal_files = await codebox.alist_files()
        for file in files:
            assert file.content is not None
            await codebox.aupload(file.name, file.content)

        codebox_files = await codebox.alist_files()
        assert set(
            [file.name for file in files] + [file.name for file in orginal_files]
        ) == set([file.name for file in codebox_files])

        assert all(
            [
                package_name in str(await codebox.ainstall(package_name))
                for package_name in packages
            ]
        )

        output: CodeBoxOutput = await codebox.arun(code)
        codebox_files_output = await codebox.alist_files()
        assert assert_function(output, codebox_files_output)

    finally:
        assert await codebox.astop() == "stopped"

    return True
