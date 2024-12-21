# COMP2001: CommentsService

[Address Initial Feedback](/docs/initial-feedback.md)

CommentsService is a project I made for **COMP2001** at the University of Plymouth. It is a Django RESTful API that allows users to create, read and update comments on trails. It also includes authentication and authorisation features, as well as a web interface for testing the API.

In Django, an `app` refers to a folder (i.e. feature) inside the project

## Setup

On the starting commits, I ran the following commands to set up the Django project:

1. run `python3 -m venv venv` to create virtual environment
2. run `source venv/bin/activate` (or whatever you named the virtual environment) to enter it
3. run `pip3 install django djangorestframework` to install both of those packages
4. run `pip3 freeze > requirements.txt` to store the dependencies, to reinstall to the venv on new clones by running `pip3 install -r requirements.txt`
5. run `django-admin startproject CommentsService` to create the Django project
6. run `cd CommentsService` then `python3 manage.py migrate` to migrate the database
7. run `pip3 install mssql-django python-dotenv` to install the database driver and dotenv package

`...`
