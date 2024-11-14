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


codebox = CodeBox()

# First download
url_upload(
    codebox,
    "https://codeboxapistorage.blob.core.windows.net/bucket/data-test.arrow",
)

# Second download
url_upload(
    codebox,
    "https://codeboxapistorage.blob.core.windows.net/bucket/data-train.arrow",
)

# List files in sandbox
print(codebox.list_files())

# File verification with sizes
result = codebox.exec("""
try:
    import os
    files = [(f, os.path.getsize(f)) for f in os.listdir('.')]
    print(files)
except Exception as e:
    print(f"Internal error: {str(e)}")
""")
print(result.text)
