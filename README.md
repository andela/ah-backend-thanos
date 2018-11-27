[![Build Status](https://travis-ci.org/andela/ah-backend-thanos.svg?branch=develop)](https://travis-ci.org/andela/ah-backend-thanos)
[![Coverage Status](https://coveralls.io/repos/github/andela/ah-backend-thanos/badge.svg)](https://coveralls.io/github/andela/ah-backend-thanos)
[![Maintainability](https://api.codeclimate.com/v1/badges/2bc2a887886c0fcc355a/maintainability)](https://codeclimate.com/github/andela/ah-backend-thanos/maintainability)

# Authors Haven - A Social platform for the creative at heart.

## Description

The website serves as a blog where persons write and read articles

## Features

- Users can create an account and log in.

## Main requirements include:

> 1. [git](https://git-scm.com/)
> 2. [python](https://docs.python.org/)
> 3. [pip](https://pypi.python.org/pypi/pip)
> 4. [virtualenv](https://virtualenv.pypa.io/en/stable/)
> 5. [postgresql](https://www.postgresql.org/)

## Set up of the App

1. Clone the project

`git clone https://github.com/andela/ah-backend-thanos.git`

2. Navigate to the project directory

`cd ah-backend-thanos`

3. Create a virtual environment using `virtualenv` and activate it.
   `virtualenv env`
   `source env/bin/activate`

4. Install packages using `pip install -r requirements.txt`

5. Set up the Database using `postgresql` and connect to the database using `psycopg2`

#### Instructions on using the .env file for setting up the database

- Create a file in the root directory called .env and enter the data below.

`SECRET_KEY=s3cr3t`

`DB_NAME= db_name`

`DB_USER= db_user`

`DB_PASSWORD= db_password`

`DB_HOST= db_host`

`ALLOWED_HOSTS= .localhost, .herokuapp.com`

`EMAIL_HOST = email_host`

`EMAIL_HOST_USER= email_host_user`

`EMAIL_HOST_PASSWORD = email_host_password`

`EMAIL_PORT = email_port`

- Change the SECRET_KEY to the project secret key.

- Enter the postgres database details on heroku or create a database locally and enter the database details.
- then run `python manage.py makemigrations` to create the migrations
- run `python manage.py migrate` to add the migrations to the app

6. Run the app by running `manage.py`

`python manage.py runserver`

7. Run Tests

`python manage.py test`

The API on Heroku:
https://ah-backend-thanos-staging.herokuapp.com
