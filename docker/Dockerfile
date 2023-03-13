FROM arm64v8/python:3.8-slim-bullseye 

ENV PYTHONUNBUFFERED=1
ENV HDF5_USE_FILE_LOCKING=FALSE

RUN mkdir -p /usr/app
COPY . /usr/app
WORKDIR /usr/app

RUN apt-get -y update && \
    apt-get -y install --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install wheel
RUN pip install -U -r requirements.txt

CMD ["python", "-u", "app.py"]

