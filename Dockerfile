FROM python:3.8-slim

ARG VERSION

RUN pip3 install bork==${VERSION}

CMD ["/usr/local/bin/bork"]
