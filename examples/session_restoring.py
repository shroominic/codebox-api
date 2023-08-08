from codeboxapi import CodeBox


def session_restoring():
    session = CodeBox()
    session.start()

    session_id = session.session_id
    print(session_id)
    assert session_id is not None

    session.run('hello = "Hello World!"')

    del session

    print(CodeBox.from_id(session_id=session_id).run("print(hello)"))

    CodeBox.from_id(session_id=session_id).stop()


if __name__ == "__main__":
    session_restoring()
