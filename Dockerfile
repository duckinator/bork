FROM python:3.8-slim

RUN pip3 install bork

CMD ["/usr/local/bin/bork"]
