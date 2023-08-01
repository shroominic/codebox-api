import os

import requests

from codeboxapi import CodeBox


async def main():
    async with CodeBox() as codebox:
        # download the iris dataset
        csv_bytes = requests.get(
            "https://archive.ics.uci.edu/"
            "ml/machine-learning-databases/iris/iris.data"
        ).content

        # upload the dataset to the codebox
        await codebox.aupload("iris.csv", csv_bytes)

        # install the required packages
        await codebox.ainstall("matplotlib")
        await codebox.ainstall("pandas")

        # dataset analysis code
        code = (
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n\n"
            "df = pd.read_csv('iris.csv', header=None)\n"
            "df.columns = ['sepal_length', 'sepal_width',"
            "'petal_length', 'petal_width', 'class']\n\n"
            "color_dict = {'Iris-setosa': 0, 'Iris-versicolor': 1, "
            "'Iris-virginica': 2}\n\n"
            "df['color'] = df['class'].map(color_dict)\n\n"
            "df.plot.scatter(x='sepal_length', y='sepal_width', "
            "c='color', colormap='viridis')\n"
            "plt.show()"
        )

        # run the code
        output = await codebox.arun(code)
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


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
