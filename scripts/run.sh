#!/bin/bash

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo ""
    echo "Virtual environment is not activated... Please follow these steps:"
    echo "1. Create a virtual environment: python3 -m venv venv"
    echo "2. Activate the virtual environment: source venv/bin/activate"
    echo "3. Install requirements: pip3 install -r requirements.txt"
    echo "4. Run this script again."
    echo ""
    exit 1
fi

if python3 CommentsService/manage.py makemigrations && python3 CommentsService/manage.py migrate; then
    echo "Migrated successfully..."
    if python3 CommentsService/manage.py runserver; then
        echo "Server shutting down..."
    else
        echo "Failed to start CommentsService." >&2
        exit 1
    fi

else
    echo "Failed to create migrations." >&2
    exit 1
fi