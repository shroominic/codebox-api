from codeboxapi.box import LocalBox

with LocalBox() as box:
    box.run("print('Hello, world!')")
    box.install("pandas")
    v = box.run("pandas.__version__")
