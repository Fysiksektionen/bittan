FROM python:3.13

RUN apt-get -y update
RUN apt-get -y upgrade

WORKDIR /bittan
COPY ./requirements.txt ./requirements.txt
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY . /bittan
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
