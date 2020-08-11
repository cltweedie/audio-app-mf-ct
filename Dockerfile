FROM python:3.7-slim-stretch

RUN apt-get update -y && apt-get install -y --no-install-recommends build-essential gcc \
    libsndfile1 

RUN apt-get update && apt-get install -y git python3-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade -r app/requirements.txt

RUN pip install git+https://github.com/rbracco/fastai2_audio.git

COPY app app/

EXPOSE 5000

CMD ["python", "app/server.py", "serve"]
