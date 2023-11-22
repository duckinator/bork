FROM python:3.12-slim

ARG VERSION

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y install git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip3 install bork==${VERSION}

CMD ["/usr/local/bin/bork"]
