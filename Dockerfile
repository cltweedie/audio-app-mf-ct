FROM python:3.7-slim-stretch

RUN apt-get update -y && apt-get install -y --no-install-recommends build-essential gcc \
    libsndfile1 

RUN apt-get update && apt-get install -y git python3-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
ADD requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN pip install git+https://github.com/mikful/fastai2_audio.git

COPY app app/

EXPOSE 5000

CMD ["python", "app/server.py", "serve"]
