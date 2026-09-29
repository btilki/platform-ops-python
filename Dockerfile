# syntax=docker/dockerfile:1

FROM python:3.12-slim-bookworm AS build
WORKDIR /src
RUN pip install --no-cache-dir --upgrade pip hatchling
COPY pyproject.toml README.md LICENSE /src/
COPY src /src/src
RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.12-slim-bookworm
RUN useradd --uid 65532 --create-home --home-dir /nonexistent --shell /usr/sbin/nologin nonroot
COPY --from=build /install /usr/local
USER 65532:65532
WORKDIR /work
ENTRYPOINT ["promotion-bot"]
