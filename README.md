# COMP2001: CommentsService

CommentsService is a project I made for **COMP2001** at the University of Plymouth. It is a Django RESTful API that allows users to create, read and update comments on trails. It also includes authentication and authorisation features, as well as a web interface for testing the API.

## Setup

On a starting commit, I run the following commands to set up a virtual environment and install some necessary packages:

1. run `python3 -m venv venv` to create virtual environment
2. run `source venv/bin/activate` (or whatever you named the virtual environment) to enter it
3. run `pip3 install django djangorestframework` to install both of those packages
4. run `pip3 freeze > requirements.txt` to store the dependencies, to reinstall to the venv on new clones by running `pip3 install -r requirements.txt`

`...`
