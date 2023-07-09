import codeboxapi as cb


def test_create_codebox():
    codebox = cb.CodeBox(
        # Config Ideas:
        # name="Test Codebox",
        # python_version="3.8",
        # requirements=["numpy==1.19.5"],
        # storage="persistent",
        # storage_size=100,
        # vector_store=True,
        # timeout=15,  # minutes
        # cpu=1,  # vCPU
        # memory=512,  # MB
        # gpu=0,  # GPU
        # metadata={"key": "value"},
    )
    status = codebox.start()
    assert status.status == "started"

    status = codebox.status()
    assert status.status == "running"
    
    codebox.stop()
    
    # status = codebox.status()
    # assert status.status == "stopped"
    # TODO: Fix this test
