FROM arm32v7/python:3.7-slim-buster

COPY qemu-arm-static /usr/bin

ENV PYTHONUNBUFFERED=1

RUN mkdir -p /usr/app
COPY . /usr/app
WORKDIR /usr/app

RUN apt-get -y update && \
    apt-get install libatlas3-base libhdf5-103 git

RUN pip install --extra-index-url https://www.piwheels.org/simple -r requirements.txt

CMD ["python", "app.py"]