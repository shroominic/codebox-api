FROM python:slim-bookworm as build

COPY README.md pyproject.toml src /

RUN pip install -e .[all]

FROM python:slim-bookworm as runtime

RUN useradd -ms /bin/bash codebox-user

COPY --chown=codebox-user:codebox-user --from=build /usr/local/ /usr/local/

USER codebox-user

ENV PATH="/usr/local/bin:$PATH"

CMD codeboxapi-serve
