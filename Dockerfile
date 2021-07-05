FROM arm32v7/python:3.7-alpine3.13

RUN mkdir /app
WORKDIR /app
COPY requirements.txt /requirements.txt

RUN apk add --update --no-cache --virtual .tmp gcc libc-dev linux-headers
RUN apk add --no-cache libffi-dev openblas-dev libgfortran lapack-dev build-base openssl-dev
RUN apk add --no-cache hdf5-dev
RUN pip install -r /requirements.txt
RUN apk --no-cache del build-base

ENV PYTHONUNBUFFERED 1
COPY . /app/

CMD ["python", "app.py"]