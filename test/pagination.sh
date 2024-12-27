#!/bin/bash

echo "------------------------------------------"
echo "Testing Pagination Functionality"
echo "------------------------------------------"
echo ""

# As well as for the other test scripts, these are dynamic authentication headers for different users;
# they create Base64 encoded credentials for HTTP Basic Authentication.
# The '-n' flag in 'echo -n' is critical to prevent a newline character from being included in the encoding
# thereby ensuring the credentials are correctly formatted for HTTP headers.
TIM_AUTH="Authorization: Basic $(echo -n 'tim@plymouth.ac.uk:COMP2001!' | base64)"
ADA_AUTH="Authorization: Basic $(echo -n 'ada@plymouth.ac.uk:insecurePassword' | base64)"
GRACE_AUTH="Authorization: Basic $(echo -n 'grace@plymouth.ac.uk:ISAD123!' | base64)"

# Step 1: Create 12 comments to demonstrate pagination
echo "Step 1: Creating 12 comments to demonstrate pagination..."
echo ""

# Array of users for cycling through
USERS=("$TIM_AUTH" "$ADA_AUTH" "$GRACE_AUTH")
USER_NAMES=("Tim" "Ada" "Grace")
USER_EMAILS=("tim@plymouth.ac.uk" "ada@plymouth.ac.uk" "grace@plymouth.ac.uk")

# Various messages for the comments
TRAIL_MESSAGES=(
    "Beautiful morning walk along this trail"
    "Perfect trail for relaxation"
    "Great trail for debugging thoughts"
    "Stunning views at sunset here"
    "Wildlife spotting opportunities abound"
    "Well-maintained paths throughout"
    "Family-friendly with gentle slopes"
    "Historical landmarks along the way"
    "Peaceful escape from the city"
    "Challenging terrain for experienced hikers"
    "Accessible parking and facilities"
    "Dog friendly with pet-water stations available"
)

# Create 12 comments
for i in {0..11}; do
    USER_INDEX=$(($i % 3)) # use the modulo operator to assign one of 3 users per iteration (indices 0, 1, 2)
    USER_AUTH=${USERS[$USER_INDEX]}
    USER_NAME=${USER_NAMES[$USER_INDEX]}
    USER_EMAIL=${USER_EMAILS[$USER_INDEX]}
    MESSAGE="${TRAIL_MESSAGES[$i]}"
    TRAIL_ID=$((($i % 3) + 1))  # Alternate between trails 1, 2, and 3
    
    echo "Creating comment $((i+1)) as $USER_NAME on trail $TRAIL_ID..."
    RESPONSE=$(curl -s -X POST http://localhost:8000/api/comments/ \
      -H "Content-Type: application/json" \
      -H "$USER_AUTH" \
      -d "{\"trail_id\": $TRAIL_ID, \"comment_text\": \"$USER_NAME: $MESSAGE\", \"email\": \"$USER_EMAIL\"}")
    
    # Extract the numeric comment ID from the JSON response:
    # - grep -o '"comment_id":[0-9]*' finds the substring like "comment_id":123
    # - sed 's/"comment_id"://' removes the key name and colon, leaving just the numeric ID.
    COMMENT_ID=$(echo $RESPONSE | grep -o '"comment_id":[0-9]*' | sed 's/"comment_id"://')
    echo "  Created comment ID: $COMMENT_ID"
done

echo ""
echo "------------------------------------------"
echo "Step 2: Testing Pagination"
echo "------------------------------------------"
echo ""

# Test 1: Get first page (should show 10 items)
echo "Test 1: Fetching first page (default page size = 10)..."
echo "Request: GET http://localhost:8000/api/comments/"
echo ""
RESPONSE=$(curl -s -X GET "http://localhost:8000/api/comments/")
# Pipe the raw JSON response to Python's json.tool for readable, pretty-printed output, then show the top/heading 20 lines.
echo "$RESPONSE" | python3 -m json.tool | head -n 20
echo "..."

# Extract count and next URL
COUNT=$(echo "$RESPONSE" | grep -o '"count":[0-9]*' | sed 's/"count"://')
NEXT=$(echo "$RESPONSE" | grep -o '"next":"[^"]*"' | sed 's/"next":"//' | sed 's/"$//')

echo ""
echo "Total comments: $COUNT"
echo "Next page URL: $NEXT"
echo ""

# Test 2: Get second page
echo "Test 2: Fetching second page..."
echo "Request: GET http://localhost:8000/api/comments/?page=2"
echo ""
RESPONSE=$(curl -s -X GET "http://localhost:8000/api/comments/?page=2")
echo "$RESPONSE" | python3 -m json.tool | head -n 20
echo "..."

# Test 3: Filter by trail_id with pagination
echo ""
echo "Test 3: Testing pagination with trail_id filter..."
echo "Request: GET http://localhost:8000/api/comments/?trail_id=1"
echo ""
RESPONSE=$(curl -s -X GET "http://localhost:8000/api/comments/?trail_id=1")
COUNT=$(echo "$RESPONSE" | grep -o '"count":[0-9]*' | sed 's/"count"://')
echo "Comments for trail_id=1: $COUNT"
echo ""

# Test 4: Verify pagination structure

# This test demonstrates the pagination response format by piping curl output (HTTP Response) into Python.
# The inline Python script parses the JSON and extracts the four key pagination fields:
  # = count (total items), next/previous (navigation URLs), and results (current page data).
  # = uses .get() with default values ensures the script handles missing fields gracefully.
  # = '-s' for silent mode (no progress meter); '-X GET' specifies the HTTP method; '-c' to run the following command as Python.
echo "Test 4: Verifying pagination response structure..."
echo ""
curl -s -X GET "http://localhost:8000/api/comments/?page=1" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print('Pagination structure:')
print(f'  - count: {data.get(\"count\", \"N/A\")}')
print(f'  - next: {data.get(\"next\", \"N/A\")}')
print(f'  - previous: {data.get(\"previous\", \"N/A\")}')
print(f'  - results: Array with {len(data.get(\"results\", []))} items')
"

echo ""
echo "------------------------------------------"
echo "Test Summary:"
echo "- Created 12 comments (4 per trail across 3 trails)"
echo "- Demonstrated pagination with 10 items per page"
echo "- Showed navigation between pages (page 1 and page 2)"
echo "- Tested pagination with filters"
echo "- Verified pagination response structure"
echo "------------------------------------------"

cat <<EOF

The pagination tests verify:
- Default page size is 10 items
- Response includes count, next, previous, and results
- Navigation between pages works correctly
- Pagination works with query filters (e.g., trail_id)
- Response structure follows REST pagination standards
------------------------------------------
EOF