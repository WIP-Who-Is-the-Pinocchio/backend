FROM python:3.11.5

WORKDIR /app

COPY . /app/

ENV PYTHONPATH=${PYTHONPATH}:${PWD}
ENV DB_USER=user
ENV DB_PASSWORD=wip
ENV DB_HOST=wip-mysql
ENV DB_ECHO=False
ENV REDIS_HOST=wip-redis

RUN pip3 install poetry==1.6.1
RUN poetry config virtualenvs.create false
RUN poetry install --no-root