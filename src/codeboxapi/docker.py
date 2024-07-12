import socket
import subprocess

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
        **_: bool,
    ) -> None:
        self.port = get_free_port(port_or_range)
        subprocess.run(
            ["docker", "run", "-d", "--rm", "-p", f"{self.port}:8069", image],
            check=True,
        )
        self.aclient = httpx.AsyncClient(base_url=f"http://localhost:{self.port}")
