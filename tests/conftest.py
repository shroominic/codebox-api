import os

import pytest

from codeboxapi import CodeBox

LOCALBOX = CodeBox(api_key="local")


@pytest.fixture(
    scope="session",
    params=["local", "docker", os.getenv("CODEBOX_API_KEY")],
)
def codebox(request: pytest.FixtureRequest) -> CodeBox:
    if request.param == "local":
        return LOCALBOX

    if request.param == "docker" and (
        os.system("docker ps > /dev/null 2>&1") != 0
        or os.getenv("GITHUB_ACTIONS") == "true"
    ):
        pytest.skip("Docker is not running")

    return CodeBox(api_key=request.param)
