from rest_framework import serializers
from .models import Comment, User, Reply


class CommentSerialiser(serializers.ModelSerializer):
    """Serialiser for Comment model matching updated ERD structure.
    
    Handles the foreign key relationship to User model.
    Shows user email in responses rather than user ID.
    """
    # Read-only field to show user email in responses
    user_email = serializers.CharField(source='user.user_email', read_only=True)
    
    # Write-only field to accept email when creating comments
    email = serializers.EmailField(write_only=True, required=False)
    
    class Meta:
        model = Comment
        fields = [
            'comment_id', 
            'trail_id', 
            'user',  # Foreign key field
            'user_email',  # Display field
            'email',  # Input field
            'comment_text', 
            'datetime_posted', 
            'is_edited',
            'last_edit_datetime',
            'is_archived',
            'archived_by'
        ]
        read_only_fields = [
            'comment_id', 
            'user',  # Set automatically from email
            'user_email',
            'datetime_posted', 
            'is_edited',
            'last_edit_datetime',
            'is_archived',
            'archived_by'
        ]
    
    def create(self, validated_data):
        """Override create to handle user lookup by email."""
        email = validated_data.pop('email', None)
        
        if email:
            # Get or create user based on email
            user, created = User.objects.get_or_create(
                user_email=email,
                defaults={'is_admin': False}  # Default to non-admin
            )
            validated_data['user'] = user
            
        return super().create(validated_data)
    
class ReplySerialiser(serializers.ModelSerializer):
    """Serialiser for Reply model.
    
    Handles the foreign key relationships to Comment and User models.
    Shows user email in responses rather than user ID.
    """
    # Read-only field to show user email in responses
    reply_user_email = serializers.CharField(source='reply_user_id.user_email', read_only=True)
    
    class Meta:
        model = Reply
        fields = [
            'reply_id',
            'comment_id',
            'reply_user_id',
            'reply_user_email',
            'reply_text',
            'reply_datetime'
        ]
        read_only_fields = ['reply_id', 'reply_datetime', 'reply_user_email']