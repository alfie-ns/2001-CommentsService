from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('comments/', views.CommentsAPIView.as_view(), name='comments-api'),
    path('comments/<int:comment_id>/replies/', views.CommentRepliesView.as_view(), name='replies-api')
    
]
