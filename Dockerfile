# Pull base image
FROM ubuntu:20.04

# Metadata indicating an image maintainer.
LABEL maintainer="paul.kim@honeynaps.com"

RUN apt update
RUN apt install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa

RUN apt update && apt upgrade -y
RUN apt install python3.8 openvpn -y
RUN apt install python3-pip -y
COPY . /app
WORKDIR /app

RUN pip3 install -r requirements.txt

# ENTRYPOINT ["python3", "crawler_google_news.py"]