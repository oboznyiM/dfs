FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt
RUN mkdir -p /data
COPY . /app

CMD [ "python", "-u", "chunkserver.py" ]
