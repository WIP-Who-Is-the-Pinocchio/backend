FROM python:3.11.5

WORKDIR /app

COPY . /app/

RUN pip3 install poetry==1.6.1
RUN poetry config virtualenvs.create false
RUN poetry install --no-root
