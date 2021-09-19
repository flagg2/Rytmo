FROM python:3.8-slim-buster

RUN apt-get -y update

RUN apt-get -y upgrade

RUN apt-get install -y ffmpeg

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir discord discord-components youtube-dl requests python-dotenv pynacl

RUN pwd

CMD ["test.py"]

ENTRYPOINT ["python3"]