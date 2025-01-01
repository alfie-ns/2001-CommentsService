#!/bin/bash

# Interactive comment posting script for the CommentsService API

echo "------------------------------------------"
echo "     Interactive Comment POST Script"
echo "------------------------------------------"
echo ""

# Function to display available trails
show_trails() {
    echo "Available trails to comment on:"
    echo ""
    echo "  1. Plymouth Waterfront Walk"
    echo "  2. Plymbridge Circular"
    echo "  3. Dartmoor Way"
    echo "  4. Plymbridge Woods Walk"
    echo "  5. The Lookout and Cesar's Camp"
    echo ""
}

# Function to get user credentials
get_user_credentials() {
    echo "Please select a user account:"
    echo ""
    echo "  1. Tim Berners-Lee (User)"
    echo "  2. Ada Lovelace (User)"
    echo "  3. Grace Hopper (Admin)"
    echo ""
    read -p "Enter your choice (1-3): " user_choice # as specified in the pu.sh, -p means the following string is a prompt for user_choice input
    
    case $user_choice in
        1)
            USER_EMAIL="tim@plymouth.ac.uk"
            USER_PASSWORD="COMP2001!"
            USER_NAME="Tim"
            ;; # double semicolon ends the case statement
        2)
            USER_EMAIL="ada@plymouth.ac.uk"
            USER_PASSWORD="insecurePassword"
            USER_NAME="Ada"
            ;;
        3)
            USER_EMAIL="grace@plymouth.ac.uk"
            USER_PASSWORD="ISAD123!"
            USER_NAME="Grace"
            ;;
        *)
            echo "Invalid choice. Defaulting to Tim."
            USER_EMAIL="tim@plymouth.ac.uk"
            USER_PASSWORD="COMP2001!"
            USER_NAME="Tim"
            ;;
    esac
    
    # Generate auth header for the selected user
    AUTH_HEADER="Authorization: Basic $(echo -n "$USER_EMAIL:$USER_PASSWORD" | base64)" # echo -n means to not output a newline character at the end, so base64 will encode just the relevant string as a single line
    echo ""
    echo "Authenticated as: $USER_NAME ($USER_EMAIL)"
    echo ""
}

# Display trails and get selection
show_trails
read -p "Select a trail to comment on (1-5): " trail_choice

# Validate trail selection
if [[ ! "$trail_choice" =~ ^[1-5]$ ]]; then # if trail_choice does NOT fall within 1-5
    echo "Invalid trail selection. Using trail 1."
    trail_choice=1
fi

TRAIL_ID=$trail_choice
echo ""

# Get user authentication
get_user_credentials

# Prompt for comment text
echo "Enter your comment about this trail:"
echo "(Press Enter when finished)"
read -r COMMENT_TEXT # no prompt this time so just read raw (don't interpret escape sequences)

# Validate comment isn't empty
if [ -z "$COMMENT_TEXT" ]; then
    echo ""
    echo "Error: Comment cannot be empty. Exiting."
    exit 1
fi

echo ""
echo "------------------------------------------"
echo "Posting your comment..."
echo "------------------------------------------"

# Make the API request to post the comment. The backslash jumps the command to thr next line
RESPONSE=$(curl -s -X POST http://localhost:8000/api/comments/ \
    -H "Content-Type: application/json" \
    -H "$AUTH_HEADER" \
    -d "{
        \"trail_id\": $TRAIL_ID,
        \"comment_text\": \"$COMMENT_TEXT\",
        \"email\": \"$USER_EMAIL\"
    }")

# Check if the request was successful by looking for comment_id
if echo "$RESPONSE" | grep -q '"comment_id"'; then
    # Extract the comment ID from response
    COMMENT_ID=$(echo "$RESPONSE" | grep -o '"comment_id":[0-9]*' | sed 's/"comment_id"://')
    
    echo "Comment posted successfully!"
    echo ""
    echo "Comment Details:"
    echo "----------------"
    echo "$RESPONSE" | python3 -m json.tool # -m json.tool formats JSON
    
    echo ""
    echo "------------------------------------------"
    echo "Verifying comment in database..."
    echo "------------------------------------------"
    
    # Fetch the comment to prove it's in the database
    VERIFY_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/comments/?comment_id=$COMMENT_ID") # GET the comment silently by ID (-X for HTTP method)
    
    echo ""
    echo "Database verification:"
    echo "$VERIFY_RESPONSE" | python3 -m json.tool | grep -A 10 "\"comment_id\": $COMMENT_ID" # `grep -A 10` shows 10 lines after finding comment_id, capturing the full comment object to print
    
    echo ""
    echo "-------------------------------------------"
    echo "Summary:"
    echo "- Comment ID: $COMMENT_ID"
    echo "- Posted by: $USER_NAME"
    echo "- Trail ID: $TRAIL_ID"
    echo "- Status: Successfully added to MS SQL database"
    echo "-------------------------------------------"
else
    # Handle error cases
    echo "Failed to post comment"
    echo ""
    echo "Error response:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE" # If json.tool fails, just print raw response, 2>/dev/null suppresses the error output
    echo ""
    echo "Please ensure:"
    echo "1. The API server is running on localhost:8000"
    echo "2. Authentication credentials are correct"
    echo "3. Trail ID is valid"
fi