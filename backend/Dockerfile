FROM python:3

RUN apt-get -y update
RUN apt-get -y upgrade

COPY ./requirements.txt ./requirements.txt
RUN python3 -m pip install -r requirements.txt

CMD ["echo", "Hello"]
