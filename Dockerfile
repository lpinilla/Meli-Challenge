FROM python:3.10-alpine

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN \
apk add --no-cache postgresql-libs && \
apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
pip install --no-cache-dir --upgrade -r /code/requirements.txt && \
apk --purge del .build-deps

COPY ./app /code/app

CMD ["uvicorn", "main:app", "--app-dir", "app", "--host", "0.0.0.0", "--port", "8080"]


