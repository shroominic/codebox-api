import asyncio
import os

from codeboxapi import CodeBox


def test_codebox():
    codebox = CodeBox(api_key=os.getenv("CODEBOX_API_KEY"))
    assert run_sync(codebox), "Failed to run sync codebox remotely"
    assert asyncio.run(run_async(codebox)), "Failed to run async codebox remotely"


def test_localbox():
    codebox = CodeBox(api_key="local")
    assert run_sync(codebox), "Failed to run sync codebox locally"
    assert asyncio.run(run_async(codebox)), "Failed to run async codebox locally"


def run_sync(codebox: CodeBox) -> bool:
    try:
        assert codebox.start() == "started"
        print("Started")

        assert codebox.status() == "running"
        print("Running")

        codebox.run("x = 'Hello World!'")
        assert codebox.run("print(x)").content == "Hello World!"
        print("Printed")

        file_name = "test_file.txt"
        assert file_name in str(codebox.upload(file_name, b"Hello World!"))
        print("Uploaded")

        assert file_name in str(
            codebox.run("import os;\nprint(os.listdir(os.getcwd())); ")
        )
        assert file_name in str(codebox.list_files())

        assert codebox.download(file_name).content == b"Hello World!"
        print("Downloaded")

        assert "matplotlib" in str(codebox.install("matplotlib"))

        assert (
            "error"
            != codebox.run("import matplotlib; print(matplotlib.__version__)").type
        )
        print("Installed")

        o = codebox.run(
            "import matplotlib.pyplot as plt;"
            "plt.plot([1, 2, 3, 4], [1, 4, 2, 3]); plt.show()"
        )
        assert o.type == "image/png"
        print("Plotted")

    finally:
        assert codebox.stop() == "stopped"
        print("Stopped")

    return True


async def run_async(codebox: CodeBox) -> bool:
    try:
        assert await codebox.astart() == "started"
        print("Started")

        assert await codebox.astatus() == "running"
        print("Running")

        await codebox.arun("x = 'Hello World!'")
        assert (await codebox.arun("print(x)")).content == "Hello World!"
        print("Printed")

        file_name = "test_file.txt"
        assert file_name in str(await codebox.aupload(file_name, b"Hello World!"))
        print("Uploaded")

        assert file_name in str(
            await codebox.arun("import os;\nprint(os.listdir(os.getcwd())); ")
        )

        assert file_name in str(await codebox.alist_files())

        assert (await codebox.adownload(file_name)).content == b"Hello World!"
        print("Downloaded")

        assert "matplotlib" in str(await codebox.ainstall("matplotlib"))

        assert (
            "error"
            != (
                await codebox.arun("import matplotlib; print(matplotlib.__version__)")
            ).type
        )
        print("Installed")

        o = await codebox.arun(
            "import matplotlib.pyplot as plt;"
            "plt.plot([1, 2, 3, 4], [1, 4, 2, 3]); plt.show()"
        )
        assert o.type == "image/png"
        print("Plotted")

    finally:
        assert await codebox.astop() == "stopped"
        print("Stopped")

    return True


if __name__ == "__main__":
    test_codebox()
    test_localbox()
