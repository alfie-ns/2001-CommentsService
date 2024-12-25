# COMP2001: CommentsService

[Address Initial Feedback](/docs/initial-feedback.md)

CommentsService is a project I made for **COMP2001** at the University of Plymouth. It is a Django RESTful API that allows users to create, read and update comments on trails. It also includes authentication and authorisation features, as well as a web interface for testing the API.

The Django project is NOT in the root so one needs to navigate to the `CommentsService` folder to run the Django commands. All testing is seamlessly done regardless; if you don't want to use the bash scripts I made please just run the commands in them manually.

### Project Structure:

```
2001-CommentsService/       <-- Repository root
├── requirements.txt        <-- dependencies here in the root
└── CommentsService/        <-- Django Project root (navigate here)
    ├── manage.py           <-- Django management script
    ├── main/               <-- Main folder with settings and urls
    ├── comments/.          <-- Comments app folder with comment-releated code
    ├── .env                <-- Environment variables for the project with database credentials
    ├── .gitignore          <-- Contains files and folders to ignore in git
    └── venv/               <-- Virtual environment folder (not committed to git, git ignored)
├── docs/                  <-- Documentation folder
│   ├── initial-feedback.md <-- Initial feedback from the COMP2001 module
│   └── COMP2001 Coursework.pdf
├── scripts/                <-- Bash scripts for running the project
│   ├── run.sh              <-- Bash script to run the Django server
│   └── example-clone.sh    <-- Example script to show how you'd use the .env file
└── tests/                 <-- Tests folder
    ├── auth.py            <-- Tests for authentication API implementation
    ├── TO BE CONTINUED...
└── README.md               <-- This file is the main read me file for the project
```

In Django, an `app` refers to a folder (i.e. feature) inside the project

### Setup

1. `git clone https://github.com/alfie-ns/2001-CommentsService`
2a. (bash) `cd 2001-CommentsService && ./scripts/run.sh`
2b. (manual) Run the following commands:
   - `cd 2001-CommentsService`
   - `python3 -m venv venv && source venv/bin/activate`
   - `pip3 install -r requirements.txt`
   - `cd CommentsService`
   - `python3 manage.py runserver`
3. Open your browser and go to ...

### My initial Setup

On the starting commits, I ran the following commands to set up the Django project:

1. run `python3 -m venv venv` to create virtual environment
2. run `source venv/bin/activate` (or whatever you named the virtual environment) to enter it
3. run `pip3 install django djangorestframework` to install both of those packages
4. run `pip3 freeze > requirements.txt` to store the dependencies, to reinstall to the venv on new clones by running `pip3 install -r requirements.txt`
5. run `django-admin startproject CommentsService` to create the Django project
6. run `cd CommentsService` then `python3 manage.py migrate` to migrate the database
7. run `pip3 install mssql-django python-dotenv` to install the database driver and dotenv package

`...`
