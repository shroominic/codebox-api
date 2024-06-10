from codeboxapi import CodeBox

with CodeBox() as codebox:
    with open("examples/assets/swedata/train/data-00000-of-00001.arrow", "rb") as file:
        codebox.upload(file.name, file.read(), timeout=900)

    print(codebox.list_files())
