FROM python:3.7-slim-stretch

RUN apt-get update && apt-get install -y git python3-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install Pillow==7.0.0 

RUN pip install SoundFile

RUN apt-get update -y && apt-get install -y --no-install-recommends build-essential gcc \
    libsndfile1 

RUN pip install packaging==20.4

RUN !pip install git+https://github.com/rbracco/fastai2_audio.git

RUN pip install --upgrade -r requirements.txt

COPY app app/

RUN python app/server.py

EXPOSE 5000

CMD ["python", "app/server.py", "serve"]
