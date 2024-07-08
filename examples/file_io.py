import httpx
from codeboxapi import CodeBox

with CodeBox() as codebox:
    # upload dataset csv
    csv_bytes = httpx.get(
        "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
    ).content
    codebox.upload("iris.csv", csv_bytes)

    # install openpyxl for excel conversion
    codebox.install("pandas")
    codebox.install("openpyxl")

    # convert dataset csv to excel
    output = codebox.run(
        "import pandas as pd\n\n"
        "df = pd.read_csv('iris.csv', header=None)\n\n"
        "df.to_excel('iris.xlsx', index=False)\n"
        "'iris.xlsx'"
    )

    # check output type
    if output.type == "image/png":
        print("This should not happen")
    elif output.type == "error":
        print("Error: ", output.content)
    else:
        # all files inside the codebox
        for file in codebox.list_files():
            print("File: ", file.name)
            print("Content is None: ", file.content is None)
            content = codebox.download(file.name)
            print("Content: ", content)
