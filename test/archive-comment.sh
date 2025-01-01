#!/bin/bash

echo "---------------------------------------------"
echo "Testing Comment Archive/Delete Functionality"
echo "---------------------------------------------"
echo ""

# Dynamically generate authentication headers
TIM_AUTH="Authorization: Basic $(echo -n 'tim@plymouth.ac.uk:COMP2001!' | base64)"
ADA_AUTH="Authorization: Basic $(echo -n 'ada@plymouth.ac.uk:insecurePassword' | base64)"
GRACE_AUTH="Authorization: Basic $(echo -n 'grace@plymouth.ac.uk:ISAD123!' | base64)"

# 1. Create a comment as Tim (non-admin)
echo ""
echo "1. Creating a new comment as Tim..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/comments/ \
  -H "Content-Type: application/json" \
  -H "$TIM_AUTH" \
  -d '{"trail_id": 2, "comment_text": "Test comment to be archived", "email": "tim@plymouth.ac.uk"}')

# Extract comment_id from response using grep and sed
COMMENT_ID=$(echo $RESPONSE | grep -o '"comment_id":[0-9]*' | sed 's/"comment_id"://')
echo "Created comment with ID: $COMMENT_ID"
echo "Response: $RESPONSE"
echo ""

# 2. Try to archive the comment as Tim (should fail; not admin)
echo ""
echo "2. Attempting to archive comment as Tim (should fail with not admin)..."
curl -X DELETE "http://localhost:8000/api/comments/?comment_id=$COMMENT_ID" \
  -H "Content-Type: application/json" \
  -H "$TIM_AUTH"
echo ""

# 3. Try to archive the comment as Ada (should fail; not admin)
echo ""
echo "3. Attempting to archive comment as Ada (should fail with not admin)..."
curl -X DELETE "http://localhost:8000/api/comments/?comment_id=$COMMENT_ID" \
  -H "Content-Type: application/json" \
  -H "$ADA_AUTH"
echo ""

# 4. Archive the comment as Grace (admin; should succeed)
echo ""
echo "4. Archiving comment as Grace (admin; should succeed)..."
curl -X DELETE "http://localhost:8000/api/comments/?comment_id=$COMMENT_ID" \
  -H "Content-Type: application/json" \
  -H "$GRACE_AUTH"
echo ""

# 5. Try to archive the same comment again (should fail; already archived)
echo ""
echo "5. Attempting to archive already archived comment (should fail)..."
curl -X DELETE "http://localhost:8000/api/comments/?comment_id=$COMMENT_ID" \
  -H "Content-Type: application/json" \
  -H "$GRACE_AUTH"
echo ""

# 6. Try to update the archived comment (should fail)
echo ""
echo "6. Attempting to update archived comment (should fail)..."
curl -X PUT "http://localhost:8000/api/comments/?comment_id=$COMMENT_ID" \
  -H "Content-Type: application/json" \
  -H "$TIM_AUTH" \
  -d '{"comment_text": "Trying to update archived comment"}'
echo ""

# 7. Test archiving without authentication (should fail)
echo ""
echo "7. Testing archive without authentication (should fail)..."
curl -X DELETE "http://localhost:8000/api/comments/?comment_id=$COMMENT_ID" \
  -H "Content-Type: application/json"
echo ""

# 8. Test archiving non-existent comment (should fail)
echo ""
echo "8. Testing archive of non-existent comment (should fail)..."
curl -X DELETE "http://localhost:8000/api/comments/?comment_id=99999" \
  -H "Content-Type: application/json" \
  -H "$GRACE_AUTH"
echo ""

# 9. Test archiving without comment_id (should fail)
echo ""
echo "9. Testing archive without comment_id (should fail)..."
curl -X DELETE "http://localhost:8000/api/comments/" \
  -H "Content-Type: application/json" \
  -H "$GRACE_AUTH"
echo ""

# 10. Verify archived comment is still viewable
echo ""
echo "10. Verifying archived comment can still be fetched for displaying in an archived list in the frontend..."
  echo ""
  echo "First checking default behavior (should be hidden):"
  curl -X GET "http://localhost:8000/api/comments/?comment_id=$COMMENT_ID" \
    -H "Content-Type: application/json"
  echo ""
  echo ""
  echo "Now with show_archived=true flag:"
  curl -X GET "http://localhost:8000/api/comments/?comment_id=$COMMENT_ID&show_archived=true" \
    -H "Content-Type: application/json"
  echo ""

echo "------------------------------------------"
echo "Test Summary:"
echo "- Created and archived comment ID: $COMMENT_ID"
echo "- Tests admin-only archive functionality"
echo "- Tests prevention of re-archiving (archiving a comment that's already archived)"
echo "- Tests that archived comments can't be edited"
echo "- Tests that archived comments are hidden by default but still can be viewable (retrievable) with the `show_archived=true` flag"
echo "------------------------------------------" 

cat <<EOF
The tests verify:
- Only admins can archive comments
- Comments can only be archived once
- Archived comments cannot be edited
- Archived comments remain viewable under certain conditions
- Proper error handling for edge cases
- Authentication via the given API prior to archiving
------------------------------------------
EOF