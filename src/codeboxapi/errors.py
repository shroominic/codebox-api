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
        json_body: dict = {},
        headers: dict = {},
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.http_status = http_status
        self.json_body = json_body
        self.headers = headers

    def __str__(self):
        return f"{self.http_status}: {self.json_body}"

    def __repr__(self):
        return f"<CodeBoxError {self.http_status}: {self.json_body}>"
