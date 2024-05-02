import asyncio

from codeboxapi import CodeBox


def test_codebox():
    codebox = CodeBox()
    assert run_sync(codebox), "Failed to run sync codebox remotely"
    assert asyncio.run(run_async(codebox)), "Failed to run async codebox remotely"


def test_localbox():
    codebox = CodeBox(local=True)
    assert run_sync(codebox), "Failed to run sync codebox locally"
    assert asyncio.run(run_async(codebox)), "Failed to run async codebox locally"


def run_sync(codebox: CodeBox) -> bool:
    try:
        assert codebox.start() == "started"
        print(codebox.status())

        assert codebox.status() == "running"
        print(codebox.status())

        codebox.run("x = 'Hello World!'")

        assert codebox.run("print(x)") == "Hello World!\n"

        file_name = "test_file.txt"
        assert file_name in str(codebox.upload(file_name, b"Hello World!"))

        assert codebox.download(file_name).content == b"Hello World!"

        assert "matplotlib" in str(codebox.install("matplotlib"))

        assert (
            "error"
            != codebox.run("import matplotlib; print(matplotlib.__version__)").type
        )

        o = codebox.run(
            "import matplotlib.pyplot as plt;"
            "plt.plot([1, 2, 3, 4], [1, 4, 2, 3]); plt.show()"
        )
        assert o.type == "image/png"

    finally:
        assert codebox.stop() == "stopped"

    return True


async def run_async(codebox: CodeBox) -> bool:
    try:
        assert await codebox.astart() == "started"
        print(await codebox.astatus())

        assert await codebox.astatus() == "running"
        print(await codebox.astatus())

        await codebox.arun("x = 'Hello World!'")
        assert await codebox.arun("print(x)") == "Hello World!\n"

        file_name = "test_file.txt"
        assert file_name in str(await codebox.aupload(file_name, b"Hello World!"))

        assert (await codebox.adownload(file_name)).content == b"Hello World!"

        assert "matplotlib" in str(await codebox.ainstall("matplotlib"))
        assert (
            "error"
            != (
                await codebox.arun("import matplotlib; print(matplotlib.__version__)")
            ).type
        )

        o = await codebox.arun(
            "import matplotlib.pyplot as plt;"
            "plt.plot([1, 2, 3, 4], [1, 4, 2, 3]); plt.show()"
        )
        assert o.type == "image/png"

    finally:
        assert await codebox.astop() == "stopped"

    return True


if __name__ == "__main__":
    test_codebox()
    # test_localbox()
