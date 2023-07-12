FROM debian:bookworm-slim

LABEL maintainer="Tobias Florek <me@ibotty.net>"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update
RUN apt install -y reprepro gpg python3 python3-git python3-gnupg expect python3-debian zstd

COPY entrypoint.py /entrypoint.py

ENTRYPOINT ["python3", "/entrypoint.py"]
