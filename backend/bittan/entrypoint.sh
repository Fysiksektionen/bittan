printenv > /etc/environment
service cron start
python3 manage.py runserver 0.0.0.0:8000