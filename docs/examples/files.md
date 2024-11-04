# File Operations Examples

For detailed information about file operations, see:

- [RemoteFile Class](../api/types.md#remotefile-class)
- [File Operations Guide](../guides/files.md)

## Basic File Operations
```python
from codeboxapi import CodeBox

codebox = CodeBox()

# Upload text file
codebox.upload("example.txt", b"Hello from CodeBox!")

# Download a file
downloaded = codebox.download("example.txt")
content = downloaded.get_content()
print("Content:", content)

# List files
files = codebox.list_files()
print("\nFiles:", "\n".join(f.__repr__() for f in files))
```
Reference: `getting_started.py` lines 13-24

## URL Downloads
```python
from codeboxapi import CodeBox

def url_upload(codebox: CodeBox, url: str) -> None:
    codebox.exec("""
import requests
import os

def download_file_from_url(url: str) -> None:
    response = requests.get(url, stream=True)
    response.raise_for_status()
    file_name = url.split('/')[-1]
    file_path = './' + file_name
    with open(file_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
    """)
    codebox.exec(f"download_file_from_url('{url}')")
```
Reference: `big_upload_from_url.py` lines 4-19

## File Conversions
```python
from codeboxapi import CodeBox

codebox = CodeBox()

# Upload dataset csv
csv_bytes = httpx.get(
    "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
).content
codebox.upload("iris.csv", csv_bytes)

# Install required packages
codebox.install("pandas")
codebox.install("openpyxl")

# Convert dataset csv to excel
output = codebox.exec(
    "import pandas as pd\n\n"
    "df = pd.read_csv('iris.csv', header=None)\n\n"
    "df.to_excel('iris.xlsx', index=False)\n"
)
```
Reference: `file_conversion.py` lines 7-23

For more details on file handling, see:

- [Data Structures](../concepts/data_structures.md#remotefile)
- [API Methods](../api/codebox.md#file-operations)