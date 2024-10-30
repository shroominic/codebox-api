import base64
from io import BytesIO
from pathlib import Path

import httpx
from PIL import Image

from codeboxapi import CodeBox

codebox = CodeBox(api_key="local")

# download the iris dataset
iris_csv_bytes = httpx.get(
    "https://archive.ics.uci.edu/" "ml/machine-learning-databases/iris/iris.data"
).content

# upload the dataset to the codebox
codebox.upload("iris.csv", iris_csv_bytes)

# dataset analysis code
file_path = Path("examples/assets/dataset_code.txt")

# run the code
output = codebox.exec(file_path)

if output.images:
    img_bytes = base64.b64decode(output.images[0])
    img_buffer = BytesIO(img_bytes)

    # Display the image
    img = Image.open(img_buffer)
    img.show()

elif output.errors:
    print("Error:", output.errors)
