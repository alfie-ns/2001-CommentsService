from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Comment, Reply, User
from .serialisers import CommentSerialiser, ReplySerialiser


# Create your views here.

'''
TODO:
- [ ] Make models then views, then necessary serialisers, then urls:
    - [X] Define comment structure in models.py
    - [X] Define user structure in models.py
    - [X] Define replies structure in models.py
    - [X] POST Request to add a new comment to a specific trail's comment section
    - [X] GET Request to get all comments for a specific trail
    - [X] GET Request to get comments for a specific trail
    - [ ] GET Request to get a specific comment by its ID
    - [ ] PUT Request to update a specific comment ONLY by the user who created it
    - [ ] DELETE? Request to archive a specific comment ONLY by the admin
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
        
    POST: Create a new comment
        1. serialise incoming request data
        2. validate the data; raise exception if invalid (triggers a 400 response)
        3. if valid, save the new comment object to the database
        4. return a JSON response with the created comment and HTTP 201 status

    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerialiser # think `serializer_class` needs the z because it's the attribute name Django looks for
    
    def get_queryset(self):
        """- [X] Override to filter comments by trail_id if provided in query params.
           - [ ] Override to filter comments by user_id
        
        This shows Django's ORM filtering capabilities:
        - Checks for 'trail_id' in request query parameters
        - If present, filters the queryset to only show comments for that trail
        - If not present, returns all comments

        Django's DRF calls this method automatically if fetching data
        """
        queryset = super().get_queryset()
        trail_id = self.request.query_params.get('trail_id', None)
        
        if trail_id is not None:
            queryset = queryset.filter(trail_id=trail_id)
            
        return queryset

    def create(self, request, *args, **kwargs):
        """Serialise, validate, and save a new comment to the database.
           
           Django's DRF also calls this automatically so this and get_queryset doesn't need @action
        """
        serialiser = self.get_serializer(data=request.data)
        serialiser.is_valid(raise_exception=True)
        self.perform_create(serialiser)
        headers = self.get_success_headers(serialiser.data)
        return Response(serialiser.data, status=status.HTTP_201_CREATED, headers=headers)
    
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
        
        email = request.data.get('email')
        if not email:
            return Response(
                {"error": "Email is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.get_or_create(
            user_email=email,
            defaults={'is_admin': False}
        )[0]  # only take the user object
        
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
