from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Comment
from .serialisers import CommentSerialiser

# Create your views here.

'''
TODO:
- [ ] Make models then views, then necessary serialisers, then urls:
    - [X] Define comment structure in models.py
    - [ ] Define user structure in models.py
    - [ ] Define replies structure in models.py
    - [X] POST Request to add a new comment to a specific trail's comment section
    - [X] GET Request to get all comments for a specific trail
    - [X] GET Request to get comments for a specific trail
    - [ ] GET Request to get a specific comment by its ID
    - [ ] PUT Request to update a specific comment ONLY by the user who created it
    - [ ] DELETE? Request to archive a specific comment ONLY by the admin

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
        """
        queryset = super().get_queryset()
        trail_id = self.request.query_params.get('trail_id', None)
        
        if trail_id is not None:
            queryset = queryset.filter(trail_id=trail_id)
            
        return queryset

    def create(self, request, *args, **kwargs):
        """Serialise, validate, and save a new comment to the database."""
        serialiser = self.get_serializer(data=request.data)
        serialiser.is_valid(raise_exception=True)
        self.perform_create(serialiser)
        headers = self.get_success_headers(serialiser.data)
        return Response(serialiser.data, status=status.HTTP_201_CREATED, headers=headers)
