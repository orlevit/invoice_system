LABEL maintainer="Or Levitas"
LABEL version="1.0"
LABEL description="A container with Python 3.12"

FROM ubuntu:24.04

RUN apt update && apt install -y python3.12 python3-pip

RUN ln -sf /usr/bin/python3.12 /usr/bin/python

COPY . /app

WORKDIR /app

RUN git clone https://github.com/your-username/your-repository.git .

CMD ["python", "main.py"]
