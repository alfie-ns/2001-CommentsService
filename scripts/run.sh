#!/bin/bash

cd CommentsService
if python3 manage.py makemigrations && python3 manage.py migrate; then
    echo "Migrated successfully..."
    if python3 manage.py runserver; then
        echo "CommentsService is running."
    else
        echo "Failed to start CommentsService." >&2
        exit 1
    fi

else
    echo "Failed to create migrations." >&2
    exit 1
fi