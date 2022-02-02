FROM python:3.9.7

WORKDIR /usr/src/app

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

COPY requirements.txt ./
# COPY . .
RUN pip install --no-cache-dir -r requirements.txt
# CMD [ "python", "./replay_service.py" ]
