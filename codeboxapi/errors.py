"""
CodeBox API Error Classes
"""


class CodeBoxError(Exception):
    """
    Represents an api error returned from the CodeBox API.
    """

    def __init__(
        self,
        **kwargs,
    ):
        super().__init__(**kwargs)

        if (http_body := kwargs.get("http_body")) and hasattr(http_body, "decode"):
            try:
                http_body = http_body.decode("utf-8")
            except BaseException:
                http_body = (
                    "<Could not decode body as utf-8. "
                    "Please report to pleurae-berets.0u@icloud.com>"
                )

        self._message = kwargs.get("message")
        self.http_body = http_body
        self.http_status = kwargs.get("http_status")
        self.json_body = kwargs.get("json_body")
        self.headers = kwargs.get("headers", {})
        self.code = kwargs.get("code", None)
        self.request_id = self.headers.get("request-id", None)
        # self.error = self.construct_error_object() # TODO: implement
        self.user_id = self.headers.get("user_id", None)

    def __str__(self):
        msg = self._message or "<empty message>"
        if self.request_id is not None:
            return f"Request {self.request_id}: {msg}"
        return msg

    def __repr__(self):
        return f"<CodeBoxError[{self.code}] {self._message}>"

    # def construct_error_object(self):
    #     if (
    #         self.json_body is None
    #         or "error" not in self.json_body
    #         or not isinstance(self.json_body["error"], dict)
    #     ):
    #         return None

    #     return codebox.api_resources.error_object.ErrorObject.construct_from(
    #         self.json_body["error"]
    #     )  # TODO: implement
