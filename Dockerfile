FROM arm32v7/python:alpine

COPY qemu-arm-static /usr/bin

ENV PYTHONUNBUFFERED=1

RUN mkdir -p /usr/app
COPY . /usr/app
WORKDIR /usr/app

RUN apk add --update --no-cache --virtual .tmp gcc libc-dev linux-headers
RUN apk add --no-cache git libffi-dev openblas-dev libgfortran lapack-dev build-base openssl-dev
RUN apk add --no-cache hdf5-dev

RUN pip install -r requirements.txt

RUN apk --no-cache del build-base

CMD ["python", "app.py"]
