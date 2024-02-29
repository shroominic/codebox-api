import os
from pathlib import Path

import requests
from codeboxapi import CodeBox

with CodeBox() as codebox:
    # download the iris dataset
    csv_bytes = requests.get(
        "https://archive.ics.uci.edu/" "ml/machine-learning-databases/iris/iris.data"
    ).content

    # upload the dataset to the codebox
    o = codebox.upload("iris.csv", csv_bytes)

    # dataset analysis code
    file_path = Path("examples/assets/dataset_code.txt")

    # run the code
    output = codebox.run(code=file_path)
    print(output.type)

    if output.type == "image/png" and os.environ.get("CODEBOX_TEST") == "False":
        try:
            from PIL import Image  # type: ignore
        except ImportError:
            print(
                "Please install it with "
                '`pip install "codeboxapi[image_support]"`'
                " to display images."
            )
            exit(1)

        # Convert the image content ( bytes) into an image
        import base64
        from io import BytesIO

        img_bytes = base64.b64decode(output.content)
        img_buffer = BytesIO(img_bytes)

        # Display the image
        img = Image.open(img_buffer)
        img.show()

    elif output.type == "error":
        # error output
        print("Error:")
        print(output.content)
