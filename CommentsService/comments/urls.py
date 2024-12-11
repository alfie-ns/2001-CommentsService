from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('comments/', views.CommentsAPIView.as_view(), name='comments-api'),
]
