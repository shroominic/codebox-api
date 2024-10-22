FROM ghcr.io/astral-sh/uv as uv

FROM --platform=amd64 python:3.11-slim as build

ENV VIRTUAL_ENV=/.venv PATH="/.venv/bin:$PATH"

COPY --from=uv /uv /uv
COPY README.md pyproject.toml src /

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=from=uv,source=/uv,target=/uv \
    /uv venv /.venv && /uv pip install -e .[all] \
    && rm -rf README.md pyproject.toml src

# FROM --platform=amd64 python:3.11-slim as runtime

ENV PORT=8069
EXPOSE $PORT

CMD ["/.venv/bin/python", "-m", "codeboxapi.api"]
