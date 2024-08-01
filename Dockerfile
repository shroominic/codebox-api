FROM ghcr.io/astral-sh/uv as uv

FROM --platform=amd64 python:3.11 as build

ENV VIRTUAL_ENV=/.venv PATH="/.venv/bin:$PATH"

COPY --from=uv /uv /uv
COPY README.md pyproject.toml src /

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=from=uv,source=/uv,target=/uv \
    /uv venv /.venv && /uv pip install -e .[all] \
    && rm -rf README.md pyproject.toml src

CMD ["/.venv/bin/python", "-m", "codeboxapi.api"]
