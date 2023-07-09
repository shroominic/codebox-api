import requests
from codeboxapi import CodeBox

with CodeBox() as codebox:
    # upload dataset csv
    csv_bytes = requests.get("https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data").content
    codebox.upload_file("iris.csv", csv_bytes)

    # install openpyxl for excel conversion
    codebox.install_package("openpyxl")
    
    # convert dataset csv to excel
    output = codebox.run("""
    import pandas as pd

    df = pd.read_csv("iris.csv", header=None)
    
    df.to_excel("iris.xlsx", index=False)
    "iris.xlsx"
    """)

    if output.type == "image/png":
        print("This should not happen")
    
    elif output.type == "error":
        print("Error: ", output.content)
    
    else:
        files = codebox.get_available_files()
        print("Available files: ", files)
        
        file = files[0]
        content = codebox.download_file(file)
        print("Content: ", content)
