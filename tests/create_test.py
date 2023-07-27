import codeboxapi as cb


def test_create_codebox():
    codebox = cb.CodeBox()
    status = codebox.start()
    assert status.status == "started"

    status = codebox.status()
    assert status.status == "running"
    
    codebox.stop()
    
    # status = codebox.status()
    # assert status.status == "stopped"
    # TODO: Fix this test
