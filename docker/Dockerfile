FROM arm64v8/python:3.9-alpine

ENV PYTHONUNBUFFERED=1
ENV HDF5_USE_FILE_LOCKING=FALSE

RUN mkdir -p /usr/app
COPY . /usr/app
WORKDIR /usr/app

RUN pip install wheel
RUN pip install -r requirements.txt

CMD ["python", "-u", "app.py"]