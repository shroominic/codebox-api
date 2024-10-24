import socket
import subprocess
import time

import httpx

from .remote import RemoteBox


def get_free_port(port_or_range: int | tuple[int, int]) -> int:
    if isinstance(port_or_range, int):
        port = port_or_range
    else:
        start, end = port_or_range
        port = start

    while port <= (end if isinstance(port_or_range, tuple) else port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("localhost", port))
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                return port
            except OSError:
                port += 1

    raise OSError("No free ports available on the specified port or range.")


class DockerBox(RemoteBox):
    def __init__(
        self,
        port_or_range: int | tuple[int, int] = 8069,
        image: str = "shroominic/codebox:latest",
        timeout: float = 3,  # minutes
        start_container: bool = True,
        **_,
    ) -> None:
        if start_container:
            self.port = get_free_port(port_or_range)
            subprocess.run(
                [
                    "docker",
                    "run",
                    "-d",
                    "--rm",
                    "-e",
                    f"CODEBOX_TIMEOUT={timeout}",
                    "-p",
                    f"{self.port}:8069",
                    image,
                ],
                check=True,
            )
        else:
            assert isinstance(port_or_range, int)
            self.port = port_or_range
        self.session_id = str(self.port)
        self.base_url = f"http://localhost:{self.port}"
        self.client = httpx.Client(base_url=self.base_url)
        self.aclient = httpx.AsyncClient(base_url=self.base_url)
        self.api_key = "docker"
        self.factory_id = image
        self.session_id = str(self.port)
        self._wait_for_startup()

    def _wait_for_startup(self) -> None:
        while True:
            try:
                self.client.get("/")
                break
            except httpx.HTTPError:
                time.sleep(1)
