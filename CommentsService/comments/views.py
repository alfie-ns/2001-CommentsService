from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import Comment, Reply, User
from .serialisers import CommentSerialiser, ReplySerialiser
from .auth import get_authenticated_user, authenticate_user


# Create your views here.

'''
TODO:
- [X] Make models then views, then necessary serialisers, then urls:
    - [X] Define comment structure in models.py
    - [X] Define user structure in models.py
    - [X] Define replies structure in models.py
    - [X] POST Request to add a new comment to a specific trail's comment section
    - [X] GET Request to get all comments for a specific trail
    - [X] GET Request to get comments for a specific trail
    - [X] GET Request to get a specific comment by its ID
    - [X] PUT Request to update a specific comment ONLY by the user who created it (as well as replies to comments)
    - [X] DELETE? Request to archive a specific comment ONLY by the admin
    - [X] POST Request to reply to a comment

'''


class CommentsAPIView(generics.ListCreateAPIView):
    """Handle comments for trails: supports:
    - GET 
    - POST 
    - ...
    
    GET: Retrieve all comments for a specific trail
        - filter comments by trail_id from query parameters
        - returns list of comments ordered by newest first
        - if trail_id not provided, returns all comments; otherwise filter by trail_id, user_id, or comment_id
        
    POST: Create a new comment
        1. serialise incoming data
        2. validate the data; raise exception if invalid (triggers a 400 response)
        3. if valid, save the new comment object to the database
        4. return a JSON response with the created comment and HTTP 201 status

    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerialiser # `serializer_class` needs the z because it's the attribute name Django looks for
    
    def get_queryset(self):
        """- [X] Override to filter comments by trail_id if provided in query params.
           - [X] Override to filter comments by user_id
           - [X] Override to filter comments by comment_id
        
        This shows Django's ORM filtering capabilities:
        - Checks for 'trail_id' in request query parameters
        - If present, filters the queryset to only show comments for that trail
        - If not present, returns all comments
        - Excludes archived comments by default unless specifically requested

        Django's DRF calls this method automatically if fetching data
        """
        queryset = super().get_queryset()
        
        # Exclude archived comments by default
        show_archived = self.request.query_params.get('show_archived', 'false').lower() == 'true'
        if not show_archived:
            queryset = queryset.filter(is_archived=False)
        
        trail_id = self.request.query_params.get('trail_id', None)
        user_id = self.request.query_params.get('user_id', None)
        comment_id = self.request.query_params.get('comment_id', None)
        
        if trail_id is not None:
            queryset = queryset.filter(trail_id=trail_id)
        if user_id is not None:
            queryset = queryset.filter(user_id=user_id)
        if comment_id is not None:
            queryset = queryset.filter(comment_id=comment_id)
            
        return queryset

    def create(self, request, *args, **kwargs):
        """Serialise, validate, and save a new comment to the database.
           
           Django's DRF also calls this automatically so this and get_queryset doesn't need @action
        """
        # Get authenticated user
        email, is_admin = get_authenticated_user(request)
        if not email:
            return Response(
                {"error": "Authentication required"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Get or create user in local database
        user, _ = User.objects.get_or_create(
            user_email=email,
            defaults={'is_admin': is_admin}
        )
        
        # Add user to the request data
        data = request.data.copy()
        data['email'] = email
        
        serialiser = self.get_serializer(data=data)
        serialiser.is_valid(raise_exception=True)
        self.perform_create(serialiser)
        headers = self.get_success_headers(serialiser.data)
        return Response(serialiser.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def put(self, request, *args, **kwargs):
        """Update a specific comment only by the user who created it.
        
        Expects comment_id in query params or request data.
        Only allows updating the comment_text field.
        """
        # Get comment_id from query params or request data
        comment_id = request.query_params.get('comment_id') or request.data.get('comment_id')
        
        if not comment_id:
            return Response(
                {"error": "comment_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the comment
        try:
            comment = Comment.objects.get(comment_id=comment_id)
        except Comment.DoesNotExist:
            return Response(
                {"error": "Comment not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get authenticated user
        email, is_admin = get_authenticated_user(request)
        if not email:
            return Response(
                {"error": "Authentication required"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Get or create user in local database
        # It only reaches here if authentication was successful
        user, _ = User.objects.get_or_create(
            user_email=email,
            defaults={'is_admin': is_admin}
        )
        
        # Check if user owns the comment
        if comment.user != user:
            return Response(
                {"error": "You can only edit your own comments"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if comment is archived
        if comment.is_archived:
            return Response(
                {"error": "Cannot edit archived comments"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update the comment text
        new_text = request.data.get('comment_text')
        if not new_text:
            return Response(
                {"error": "comment_text is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update and save (the model's save method will handle is_edited and last_edit_datetime)
        comment.comment_text = new_text
        comment.save()
        
        # Return updated comment
        serialiser = CommentSerialiser(comment)
        return Response(serialiser.data, status=status.HTTP_200_OK)
    
    def delete(self, request, *args, **kwargs):
        """Archive a specific comment - only admins can perform this action.
        
        Expects comment_id in query params or request data.
        Sets is_archived to True and records who archived it.
        """
        # Get comment_id from query params or request data
        comment_id = request.query_params.get('comment_id') or request.data.get('comment_id')
        
        if not comment_id:
            return Response(
                {"error": "comment_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the comment
        try:
            comment = Comment.objects.get(comment_id=comment_id)
        except Comment.DoesNotExist:
            return Response(
                {"error": "Comment not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get authenticated user
        email, is_admin = get_authenticated_user(request)
        if not email:
            return Response(
                {"error": "Authentication required"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if user is admin
        if not is_admin:
            return Response(
                {"error": "Only admins can archive comments"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get or create admin user in local database
        admin_user, _ = User.objects.get_or_create(
            user_email=email,
            defaults={'is_admin': True}
        )
        
        # Check if comment is already archived
        if comment.is_archived:
            return Response(
                {"error": "Comment is already archived"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Archive the comment
        comment.is_archived = True
        comment.archived_by = admin_user
        comment.save()
        
        # Return success message with archived comment details
        return Response(
            {
                "message": "Comment archived successfully",
                "comment_id": comment.comment_id,
                "archived_by": admin_user.user_email,
                "archived_at": timezone.now()
            },
            status=status.HTTP_200_OK
        )
    
class CommentRepliesView(APIView):
    """Handle replies for a specific comment."""
    
    def get(self, request, comment_id):
        """Get all replies for a specific comment."""
        try:
            comment = Comment.objects.get(comment_id=comment_id)
        except Comment.DoesNotExist:
            return Response(
                {"error": "Comment not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        replies = Reply.objects.filter(comment_id=comment_id)
        serialiser = ReplySerialiser(replies, many=True)
        return Response(serialiser.data)
    
    def post(self, request, comment_id):
        """Create a new reply to a comment."""
        try:
            comment = Comment.objects.get(comment_id=comment_id)
        except Comment.DoesNotExist:
            return Response(
                {"error": "Comment not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get authenticated user
        email, is_admin = get_authenticated_user(request)
        if not email:
            return Response(
                {"error": "Authentication required"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Get or create user in local database
        user, _ = User.objects.get_or_create(
            user_email=email,
            defaults={'is_admin': is_admin}
        )
        
        reply_data = {
            'comment_id': comment.comment_id,
            'reply_user_id': user.user_id,
            'reply_text': request.data.get('reply_text', '')
        }
        
        serialiser = ReplySerialiser(data=reply_data)
        if serialiser.is_valid():
            serialiser.save()
            return Response(serialiser.data, status=status.HTTP_201_CREATED)
        return Response(serialiser.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, comment_id):
        """Update a specific reply only by the user who created it.
        
        Same logic as updating a comment, but for replies.
        """
        # Get reply_id from query params or request data
        reply_id = request.query_params.get('reply_id') or request.data.get('reply_id')
        
        if not reply_id:
            return Response(
                {"error": "reply_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the reply
        try:
            reply = Reply.objects.get(reply_id=reply_id)
        except Reply.DoesNotExist:
            return Response(
                {"error": "Reply not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify the reply belongs to this comment
        if reply.comment_id.comment_id != comment_id:
            return Response(
                {"error": "Reply does not belong to this comment"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get authenticated user
        email, is_admin = get_authenticated_user(request)
        if not email:
            return Response(
                {"error": "Authentication required"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Get or create user in local database
        # It only reaches here if authentication was successful
        user, _ = User.objects.get_or_create(
            user_email=email,
            defaults={'is_admin': is_admin}
        )
        
        # Check if user owns the reply
        if reply.reply_user_id != user:
            return Response(
                {"error": "You can only edit your own replies"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Update the reply text
        new_text = request.data.get('reply_text')
        if not new_text:
            return Response(
                {"error": "reply_text is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update and save
        reply.reply_text = new_text
        reply.save()
        
        # Return updated reply
        serialiser = ReplySerialiser(reply)
        return Response(serialiser.data, status=status.HTTP_200_OK)
