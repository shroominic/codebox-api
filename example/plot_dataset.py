import requests
from codeboxapi import CodeBox


with CodeBox() as codebox:
    # download the iris dataset
    csv_bytes = requests.get("https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data").content
    
    print("downloaded dataset")
    
    # upload the dataset to the codebox
    o = codebox.upload("iris.csv", csv_bytes)

    # dataset analysis code
    code = """
    import pandas as pd
    import matplotlib.pyplot as plt

    df = pd.read_csv("iris.csv", header=None)
    df.columns = ["sepal_length", "sepal_width", "petal_length", "petal_width", "class"]

    # Create a color dictionary for each class label
    color_dict = {'Iris-setosa': 0, 'Iris-versicolor': 1, 'Iris-virginica': 2}

    # Map the class labels to numbers
    df['color'] = df['class'].map(color_dict)

    df.plot.scatter(x="sepal_length", y="sepal_width", c="color", colormap="viridis")
    plt.show()
    """

    # run the code
    output = codebox.run(code)
    print(output.type)

    if output.type == "image/png":
        # Convert the image content into an image
        from io import BytesIO
        import base64
        
        try:
            from PIL import Image
        except ImportError:
            print("Please install it with `pip install codeboxapi[image_support]` to display images.")
            exit(1)
        
        # Decode the base64 string into bytes
        img_bytes = base64.b64decode(output.content)

        # Create a BytesIO object
        img_io = BytesIO(img_bytes)
        
        # Use PIL to open the image
        img = Image.open(img_io)
        
        # Display the image
        img.show()

    elif output.type == "error":
        # error output
        print("Error:")
        print(output.content)
        
    else:
        # normal text output
        print("Text Output:")
        print(output.content)
