from uuid import uuid4
from datetime import datetime
from .utils import base_request
from .schema import CodeBoxStatus, CodeBoxOutput


class CodeBox():
    """ 
    Sandboxed Python Interpreter 
    """
    
    def __init__(self) -> None:
        self.id = uuid4().int
        self.last_interaction = datetime.now()

    def _update(self) -> None:
        self.last_interaction = datetime.now()
    
    def start(self) -> CodeBoxStatus:
        # return self.codebox_request(
        #     method="POST",  # TODO: add start endpoint
        #     endpoint=f"/start",
        # )
        return self.status()
    
    def codebox_request(
        self, 
        method, 
        endpoint, 
        body=None, 
        files=None,
        content_type="application/json",
    ) -> dict:
        self._update()
        return base_request(
            method=method,
            endpoint=f"/sandbox/{self.id}" + endpoint,
            body=body,
            files=files,
            content_type=content_type,
        )
    
    def status(self):
        return CodeBoxStatus(
            ** self.codebox_request(
                method="GET",
                endpoint="/",
            )
        )
        
    def run(self, code: str):
        return CodeBoxOutput( 
            ** self.codebox_request(
                method="POST",
                endpoint=f"/run",
                body={"code": code},
            )
        )
        
    def upload_file(self, name: str, content: bytes) -> dict:
        return self.codebox_request(
            method="POST",
            endpoint="/upload",
            files={"file": (name, content)},
            content_type=None
        )
    
    # def upload_files(self, files: dict[str, bytes]) -> dict:
    #     return self.codebox_request(
    #         method="POST",
    #         endpoint="/upload",
    #         files=files,
    #     )
    
    def download_file(self, file_name: str) -> dict:
        return self.codebox_request(
            method="GET",
            endpoint="/download",
            body={"file_name": file_name},
            content_type=None,
        )
        
    def install_package(self, package_name: str) -> dict:
        return self.codebox_request(
            method="POST",
            endpoint="/install",
            body={
                "package_name": package_name,
            },
        )
    
    def get_available_files(self) -> list[str]:
        return self.codebox_request(
            method="GET",
            endpoint="/files",
        )["files"]
    
    def stop(self) -> CodeBoxStatus:
        return self.codebox_request(
            method="POST",
            endpoint="/stop",
        )

    def __enter__(self) -> "CodeBox":
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.stop()
        print("CodeBox stopped ", exc_type, exc_value, traceback)
