from .base import BaseBox
from .local import LocalBox
from .remote import RemoteBox


def CodeBox(
    session_id: str | None = None,
    api_key: str = "local",
) -> BaseBox:
    if session_id is None:
        if api_key == "local":
            return LocalBox()
        else:
            return RemoteBox()
    else:
        return RemoteBox(session_id)
