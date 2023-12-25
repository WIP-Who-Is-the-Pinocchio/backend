FROM python:3.11.5

WORKDIR /app/src

COPY . /app/

RUN pip3 install poetry==1.6.1
RUN poetry config virtualenvs.create false
RUN poetry install --no-root

ENV ENV=PROD

EXPOSE 2312

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "2312"]