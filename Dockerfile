FROM apache/airflow:2.5.1-python3.8

ENV PYTHONUNBUFFERED 1

EXPOSE 8080
USER root
RUN apt-get update && \
    apt-get install gcc wget unzip -y && \
    apt-get install ffmpeg libsm6 libxext6  -y && \
    apt-get install -y --no-install-recommends netcat && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* .venv

RUN apt-get update && \
    apt-get install python3 python3-pip build-essential cmake pkg-config libx11-dev libatlas-base-dev libgtk-3-dev libboost-python-dev -y
USER airflow
COPY requirements.txt /requirements.txt
RUN pip install --user --upgrade pip
RUN pip install -r /requirements.txt