# File Operations

For detailed information about file operations, see:

- [RemoteFile Class](../api/types.md#remotefile-class)
- [File Operations Guide](../guides/files.md)

> [!NOTE] Update **main.py** with each example and run it with
>```bash
>python main.py
>```

## Basic File Operations

```python
from codeboxapi import CodeBox

def main():
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

if __name__ == "__main__":
    main()
```

### Result:
```bash
Content: Hello from CodeBox!

Files:
RemoteFile(name='example.txt', size=20)
```

## URL Downloads

```python
from codeboxapi import CodeBox

def main():
    codebox = CodeBox()
    
    def url_upload(url: str) -> None:
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

    # Usage example
    url = "https://example.com/file.txt"
    url_upload(url)
    print("File uploaded successfully")

if __name__ == "__main__":
    main()
```

### Result:
```bash
File uploaded successfully
```

## File Conversions

```python
from codeboxapi import CodeBox
import httpx

def main():
    codebox = CodeBox()

    # Upload csv dataset
    csv_bytes = httpx.get(
        "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
    ).content
    codebox.upload("iris.csv", csv_bytes)

    # Install required packages and verify installation
    codebox.exec("""
    try:
        import pandas
        import openpyxl
        print("Required packages already installed")
    except ImportError:
        print("Installing required packages...")
        !pip install pandas openpyxl
        print("Packages installed successfully")
    """)

    # Convert csv dataset to excel
    result = codebox.exec(
        "import pandas as pd\n"
        "df = pd.read_csv('iris.csv', header=None)\n"
        "df.to_excel('iris.xlsx', index=False)\n"
        "'iris.xlsx'"
    )
    
    if result.errors:
        print("Error:", result.errors[0])
    else:
        # List all files to verify conversion
        for file in codebox.list_files():
            print(f"File: {file.path} (Size: {file.get_size()} bytes)")

if __name__ == "__main__":
    main()
```

### Result:
```bash
File: async_file.txt (Size: 4096 bytes)
File: data.csv (Size: 4096 bytes)
File: example.txt (Size: 4096 bytes)
File: iris.csv (Size: 8192 bytes)
File: iris.xlsx (Size: 12288 bytes)
File: script.py (Size: 4096 bytes)
```

For more details about file handling, see:

- [Data Structures](../concepts/data_structures.md#remotefile)
- [API Methods](../api/codebox.md#file-operations)
- [Quick Start Guide](../quickstart.md)