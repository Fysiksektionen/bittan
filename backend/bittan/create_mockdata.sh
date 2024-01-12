#!/usr/bin/env bash

echo "Do you want to populate the database with mock data? This will REMOVE ALL CURRENT DATA."

select yn in "Yes" "No"; do
    if [ $yn = "Yes" ]
    then
        python3 manage.py flush --no-input
        python3 manage.py makemigrations bittan
        python3 manage.py migrate
        PYTHONPATH="." scripts/create_mockdata.py
        echo "Added mock data!"
        break;
    elif [ $yn = "No" ]
    then
        echo "Aborted."
        break;
    fi
done