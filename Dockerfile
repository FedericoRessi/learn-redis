FROM fedora:35 AS tests

RUN dnf update -y
RUN dnf install -y python3 iputils nmap-ncat

RUN python3 -m ensurepip --upgrade

COPY /tests /tests
RUN python3 -m pip install -r /tests/requirements.txt

ENV REDIS_URL='redis://redis:6379/0'
ENV PYTEST_ADDOPTS: --full-trace

CMD pytest /tests
