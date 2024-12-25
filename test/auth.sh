#!/bin/bash

echo "------------------------------------------"
echo "Testing CommentsService with External Auth"
echo "------------------------------------------"
echo ""

# Auth headers - dynamically generated
TIM_AUTH="Authorization: Basic $(echo -n 'tim@plymouth.ac.uk:COMP2001!' | base64)"
ADA_AUTH="Authorization: Basic $(echo -n 'ada@plymouth.ac.uk:insecurePassword' | base64)"
GRACE_AUTH="Authorization: Basic $(echo -n 'grace@plymouth.ac.uk:ISAD123!' | base64)"

# 1. Firstly, create a comment as Tim
echo "1. Creating a new comment as Tim..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/comments/ \
  -H "Content-Type: application/json" \
  -H "$TIM_AUTH" \
  -d '{"trail_id": 1, "comment_text": "This is a test comment for demonstrating the update functionality (Tim)", "email": "tim@plymouth.ac.uk"}')

# Extract comment_id from response using grep and sed
COMMENT_ID=$(echo $RESPONSE | grep -o '"comment_id":[0-9]*' | sed 's/"comment_id"://')
echo "Created comment with ID: $COMMENT_ID"
echo "Response: $RESPONSE"
echo ""

# 2. Update the comment as Tim (should work - same user)
echo "2. Updating the comment as Tim (should succeed)..."
curl -X PUT "http://localhost:8000/api/comments/?comment_id=$COMMENT_ID" \
  -H "Content-Type: application/json" \
  -H "$TIM_AUTH" \
  -d '{"comment_text": "Updated; the comment has been successfully edited by the original author"}'
echo ""

# 3. Try to update Tim's comment as Ada (should fail - different user)
echo "3. Attempting to update Tim's comment as Ada (should fail)..."
curl -X PUT "http://localhost:8000/api/comments/?comment_id=$COMMENT_ID" \
  -H "Content-Type: application/json" \
  -H "$ADA_AUTH" \
  -d '{"comment_text": "Ada trying to edit Tim comment; should fail"}'
echo ""

# 4. Create a reply to the comment as Ada
echo "4. Creating a reply as Ada..."
REPLY_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/comments/$COMMENT_ID/replies/" \
  -H "Content-Type: application/json" \
  -H "$ADA_AUTH" \
  -d '{"email": "ada@plymouth.ac.uk", "reply_text": "Instead, Ada will reply to the comment"}')

# Extract reply_id from response
REPLY_ID=$(echo $REPLY_RESPONSE | grep -o '"reply_id":[0-9]*' | sed 's/"reply_id"://')
echo "Created reply with ID: $REPLY_ID"
echo "Response: $REPLY_RESPONSE"
echo ""

# 5. Update Ada's reply (should work - same user)
echo "5. Updating Ada's reply (should succeed)..."
curl -X PUT "http://localhost:8000/api/comments/$COMMENT_ID/replies/?reply_id=$REPLY_ID" \
  -H "Content-Type: application/json" \
  -H "$ADA_AUTH" \
  -d '{"reply_text": "Updated; Ada has edited her own reply successfully"}'
echo ""

# 6. Try to update Ada's reply as Grace (should fail)
echo "6. Attempting to update Ada's reply as Grace (should fail)..."
curl -X PUT "http://localhost:8000/api/comments/$COMMENT_ID/replies/?reply_id=$REPLY_ID" \
  -H "Content-Type: application/json" \
  -H "$GRACE_AUTH" \
  -d '{"reply_text": "Grace trying to edit Ada reply; should fail"}'
echo ""

# 7. Test without authentication (should fail)
echo "7. Testing update without authentication header (should fail)..."
curl -X PUT "http://localhost:8000/api/comments/?comment_id=$COMMENT_ID" \
  -H "Content-Type: application/json" \
  -d '{"comment_text": "No auth header; should fail"}'
echo ""

# 8. Test with missing comment_text (should fail)
echo "8. Testing update with missing comment_text field (should fail)..."
curl -X PUT "http://localhost:8000/api/comments/?comment_id=$COMMENT_ID" \
  -H "Content-Type: application/json" \
  -H "$TIM_AUTH" \
  -d '{}'
echo ""

# 9. Test with wrong password (should fail)
echo "9. Testing with wrong password (should fail)..."
curl -X PUT "http://localhost:8000/api/comments/?comment_id=$COMMENT_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'tim@plymouth.ac.uk:wrongpassword' | base64)" \
  -d '{"comment_text": "Wrong password; should fail"}'
echo ""

echo "------------------------------------------"
echo "Test Summary:"
echo "- Created comment ID: $COMMENT_ID"
echo "- Created reply ID: $REPLY_ID"
echo "- Tests Basic Auth with external authentication API"
echo "------------------------------------------"

cat <<EOF
The commands test:
- Successful updates by the owner
- Failed updates by non-owners
- Missing authentication
- Wrong password
- Missing required fields
- Both comments and replies
------------------------------------------
EOF