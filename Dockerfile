FROM python:3.7-slim-stretch

RUN pip install --upgrade pip && \
    pip install --no-cache-dir packaging
    pip install --no-cache-dir SoundFile

RUN apt-get update && apt-get install -y git python3-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY app app/

RUN python app/server.py

EXPOSE 5000

CMD ["python", "app/server.py", "serve"]
