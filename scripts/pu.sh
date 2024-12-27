#!/bin/bash
if read -p "Enter commit message: " MSG; then # -p indicates the following string is the prompt for the input
  git add .
  git commit -m "$MSG"
  git push -f origin main
fi