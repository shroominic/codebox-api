FROM ghcr.io/astral-sh/uv as uv

FROM --platform=arm64 python:3.12 as build

ENV VIRTUAL_ENV=/.venv PATH="/.venv/bin:$PATH"

COPY --from=uv /uv /uv
COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=from=uv,source=/uv,target=/uv \
    /uv venv /.venv && /uv pip install -r requirements.txt

FROM --platform=arm64 python:3.12-slim-bookworm as runtime

RUN useradd -ms /bin/bash codebox

COPY --chown=codebox:codebox api.py /api.py

COPY --chown=codebox:codebox --from=build /.venv /.venv

USER codebox

ENV PATH="/.venv/bin:$PATH"

CMD fastapi run /api.py --host 0.0.0.0 --port 8069
