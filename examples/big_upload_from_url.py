from codeboxapi import CodeBox


def url_upload(codebox: CodeBox, url: str) -> None:
    codebox.exec(
        """
import requests

def download_file_from_url(url: str) -> None:
    response = requests.get(url, stream=True)
    response.raise_for_status()
    file_name = url.split('/')[-1]
    with open('./' + file_name, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
        """
    )
    print(codebox.exec(f"download_file_from_url('{url}')"))


codebox = CodeBox()

url_upload(
    codebox,
    "https://codeboxapistorage.blob.core.windows.net/bucket/data-test.arrow",
)
print(codebox.list_files())

url_upload(
    codebox,
    "https://codeboxapistorage.blob.core.windows.net/bucket/data-train.arrow",
)
print(codebox.list_files())

codebox.exec("import os")
print(codebox.exec("print(os.listdir())"))
print(codebox.exec("print([(f, os.path.getsize(f)) for f in os.listdir('.')])"))
