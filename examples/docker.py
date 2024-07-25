from codeboxapi.docker import DockerBox

codebox = DockerBox()

assert codebox.healthcheck()

r = codebox.exec("import matplotlib.pyplot as plt; plt.plot([1, 2, 3]); plt.show()")

print(r.text)
