FROM shroominic/python-uv:3.10

COPY README.md pyproject.toml src /

RUN uv pip install --no-cache-dir -e .[all] && \
    rm -rf README.md pyproject.toml src

CMD ["/.venv/bin/python", "-m", "codeboxapi.api"]
