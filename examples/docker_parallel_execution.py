import asyncio
import time
from pathlib import Path

from codeboxapi import CodeBox


async def train_model(codebox: CodeBox, data_split: int) -> dict:
    """Train a model on a subset of data."""

    file = Path("examples/assets/advertising.csv")
    assert file.exists(), "Dataset file does not exist"

    # Upload dataset
    await codebox.aupload(file.name, file.read_bytes())

    # Install required packages
    await codebox.ainstall("pandas")
    await codebox.ainstall("scikit-learn")

    # Training code with different data splits
    code = f"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Load and prepare data
data = pd.read_csv('advertising.csv')
X = data[['TV', 'Radio', 'Newspaper']]
y = data['Sales']

# Split with different random states for different data subsets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state={data_split}
)

# Train model
model = LinearRegression()
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Split {data_split}:")
print(f"MSE: {{mse:.4f}}")
print(f"R2: {{r2:.4f}}")
print(f"Coefficients: {{model.coef_.tolist()}}")
"""
    result = await codebox.aexec(code)
    return {"split": data_split, "output": result.text, "errors": result.errors}


async def main():
    # Create multiple Docker instances
    num_parallel = 4
    codeboxes = [CodeBox(api_key="docker") for _ in range(num_parallel)]

    # Create tasks for different data splits
    tasks = []
    for i, codebox in enumerate(codeboxes):
        task = asyncio.create_task(train_model(codebox, i))
        tasks.append(task)

    # Execute and time the parallel processing
    start_time = time.perf_counter()
    results = await asyncio.gather(*tasks)
    end_time = time.perf_counter()

    # Print results
    print(f"\nParallel execution completed in {end_time - start_time:.2f} seconds\n")
    for result in results:
        if not result["errors"]:
            print(f"Results for {result['split']}:")
            print(result["output"])
            print("-" * 50)
        else:
            print(f"Error in split {result['split']}:", result["errors"])


if __name__ == "__main__":
    asyncio.run(main())
