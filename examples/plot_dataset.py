import base64
from io import BytesIO
from pathlib import Path

import httpx
from PIL import Image

from codeboxapi import CodeBox

codebox = CodeBox(api_key="local")

# download and upload iris dataset silently
iris_csv_bytes = httpx.get(
    "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
).content
codebox.upload("iris.csv", iris_csv_bytes)

# run the analysis
file_path = Path("examples/assets/dataset_code.txt")
output = codebox.exec(file_path)

if output.images:
    img_bytes = base64.b64decode(output.images[0])
    img_buffer = BytesIO(img_bytes)
    
    # Display the image
    img = Image.open(img_buffer)
    img.show()
    print("Image displayed in a new window")

elif output.errors:
    print("Error:", output.errors)
