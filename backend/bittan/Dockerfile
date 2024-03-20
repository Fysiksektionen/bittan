FROM python:3

RUN apt-get -y update
RUN apt-get -y upgrade

WORKDIR /bittan
COPY ./requirements.txt ./requirements.txt
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY . /bittan

RUN apt-get install -y cron
RUN crontab crontab

CMD ./entrypoint.sh
