FROM python:3.7-slim-stretch

RUN apt-get update && apt-get install -y git python3-dev gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir SoundFile

RUN apt-get update -y && apt-get install -y --no-install-recommends build-essential gcc \
    libsndfile1 

COPY requirements.txt .

RUN pip install --upgrade -r requirements.txt

RUN pip install --no-cache-dir packaging git+https://github.com/rbracco/fastai2_audio.git

COPY app app/

RUN python app/server.py

EXPOSE 5000

CMD ["python", "app/server.py", "serve"]
