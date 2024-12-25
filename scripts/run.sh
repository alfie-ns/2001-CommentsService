#!/bin/bash

# Check if virtual environment is activated
# if [ -z "$VIRTUAL_ENV" ]; then
    # echo ""
    # echo "Virtual environment is not activated... Please follow these steps:"
    # echo "1. Create a virtual environment: python3 -m venv venv"
    # echo "2. Activate the virtual environment: source venv/bin/activate"
    # echo "3. Install requirements: pip3 install -r requirements.txt"
    # echo "4. Run this script again."
    # echo ""
    # exit 1
# fi

if [ ! -d "venv" ]; then # if `venv/` does not already exist then create it
    echo "Virtual environment not found; automating the process..."
    python3 -m venv venv # -m means to create a virtual environment
fi

source venv/bin/activate

pip3 install -r requirements.txt # -r means read packages from file and install them

# Firstly, migrate the database
if python3 CommentsService/manage.py makemigrations && python3 CommentsService/manage.py migrate; then
    echo "Migrated successfully..."
    if python3 CommentsService/manage.py runserver; then
        echo "Server shutting down..." # the if statement's following command will run once the server's process is terminated so it can move on
    else
        echo "Failed to start CommentsService." >&2
        exit 1
    fi

else
    echo "Failed to create migrations." >&2
    exit 1
fi