# TODO: implement error class to handle errors from codebox

class CodeBoxError(Exception):
    def __init__(
        self,
        message=None,
        http_body=None,
        http_status=None,
        json_body=None,
        headers=None,
        code=None,
    ):
        super(CodeBoxError, self).__init__(message)

        if http_body and hasattr(http_body, "decode"):
            try:
                http_body = http_body.decode("utf-8")
            except BaseException:
                http_body = (
                    "<Could not decode body as utf-8. "
                    "Please report to pleurae-berets.0u@icloud.com>"
                )

        self._message = message
        self.http_body = http_body
        self.http_status = http_status
        self.json_body = json_body
        self.headers = headers or {}
        self.code = code
        self.request_id = self.headers.get("request-id", None)
        # self.error = self.construct_error_object() # TODO: implement
        self.user_id = self.headers.get("user_id", None)

    def __str__(self):
        msg = self._message or "<empty message>"
        if self.request_id is not None:
            return "Request {0}: {1}".format(self.request_id, msg)
        else:
            return msg

    def __repr__(self):
        return "%s(message=%r, http_status=%r, request_id=%r)" % (
            self.__class__.__name__,
            self._message,
            self.http_status,
            self.request_id,
        )

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