import codeboxapi as cb


def test_codebox():
    codebox = cb.CodeBox()

    try:
        status = codebox.start()
        assert str(status) == "started"

        status = codebox.status()
        assert str(status) == "running"

        output = codebox.run("print('Hello World!')")
        assert str(output) == "Hello World!\n"

    finally:
        codebox.stop()
