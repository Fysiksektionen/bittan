FROM python:3

RUN apt-get -y update
RUN apt-get -y upgrade

WORKDIR /bittan
COPY ./requirements.txt ./requirements.txt
RUN python3 -m pip install -r requirements.txt

COPY . /bittan
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
