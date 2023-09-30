FROM python:3.11.5-alpine

WORKDIR /app

COPY . /app/

ENV PYTHONPATH=${PYTHONPATH}:${PWD}
ENV DB_USER=user
ENV DB_PASSWORD=wip
ENV DB_HOST=wip-mysql

RUN pip3 install poetry==1.6.1
RUN poetry config virtualenvs.create false
RUN poetry install --no-root