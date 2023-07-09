import codeboxapi as cb


def test_create_codebox():
    codebox = cb.CodeBox()
    
    status = codebox.start()
    assert status.status == "started"

    output = codebox.run(
        "print('Hello World!')"
    )
    assert output.content == "Hello World!\n"

    codebox.stop()
