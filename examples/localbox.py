from codeboxapi import CodeBox

with CodeBox() as box:
    v = box.install("pandas")
    print(v)
    r = box.run("import pandas; pandas.__version__")
    print(r)
