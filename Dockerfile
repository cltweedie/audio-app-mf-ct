FROM python:3.7-slim-stretch

RUN apt-get update -y && apt-get install -y --no-install-recommends build-essential gcc \
    libsndfile1 

RUN apt-get update && apt-get install -y git python3-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python and pip
RUN apk add --no-cache --update python3 py3-pip bash

# Install dependencies
ADD ./app/requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -q -r /tmp/requirements.txt

RUN pip install git+https://github.com/mikful/fastai2_audio.git

COPY app app/

EXPOSE 5000

CMD ["python", "app/server.py", "serve"]
