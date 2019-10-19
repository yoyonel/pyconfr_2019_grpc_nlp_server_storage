FROM yoyonel/python:3.7.3-slim-stretch-grpc1.21.1-pandas-spacy

COPY . /app

WORKDIR /app

RUN pip install --upgrade pip && \
    pip install $(find dist -maxdepth 1 -type f -printf "%T@ %p\n" | sort -nr | head -1 | cut -d ' ' -f 2) && \
    rm -rf ~/.cache/pip

EXPOSE 50051 50052
