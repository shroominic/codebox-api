"""
CodeBox API
Error Classes
"""


class CodeBoxError(Exception):
    """
    Represents an api error returned from the CodeBox API.
    """

    def __init__(
        self,
        http_status: int = 0,
        content: str = "error",
        headers: dict = {},
        body: dict = {},
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.http_status = http_status
        self.content = content
        self.headers = headers
        self.body = body

    def __str__(self):
        return f"{self.http_status}: {self.content}"

    def __repr__(self):
        return f"<CodeBoxError {self.http_status}: {self.content}>"
