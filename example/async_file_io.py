import requests  # type: ignore
from codeboxapi import CodeBox


async def main():
    async with CodeBox() as codebox:
        # upload dataset csv
        csv_bytes = requests.get("https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data").content
        await codebox.aupload("iris.csv", csv_bytes)

        # install openpyxl for excel conversion
        await codebox.ainstall("pandas")
        await codebox.ainstall("openpyxl")
        
        # convert dataset csv to excel
        output = await codebox.arun("""
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
            files = await codebox.alist_files()
            print("Available files: ", files)
            
            file = files[0].name
            content = await codebox.adownload(file)
            print("Content: ", content)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())