from rest_framework import serializers
from .models import Comment, User, Reply

'''
The Meta classes configure how this serialiser works with the Comment model.

It defines:
- the model the serialiser is for (Comment)
- the fields to include in the serialised output/input
- the fields are read-only (can't be modified via the API)

The fields list includes three types of fields:
1. model fields that map directly to database columns (comment_id, trail_id, etc)
2. computed fields that don't exist in the model but are calculated (user_email)
3. input-only fields used during creation but not stored (email)

This therefore allows the API to accept an email address when creating comments,
whilst storing and referencing users by their foreign key relationship.
'''


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
            'user_id',  # Foreign key field (the actual FK to User model (read-only))
            'user_email',  # Display field (computed from user.user_email (read-only))
            'email',  # Input field (write-only field for creating comments)
            'comment_text', 
            'datetime_posted', 
            'is_edited',
            'last_edit_datetime',
            'is_archived',
            'archived_by'
        ]
        read_only_fields = [
            'comment_id',  # Auto-generated primary key
            'user',  # Set automatically from email lookup
            'user_email',  # Computed from user relationship
            'datetime_posted',  # Auto-set on creation
            'is_edited',  # Managed by model's save() method
            'last_edit_datetime',  # Updated when edited
            'is_archived',  # Only changeable via admin actions
            'archived_by'  # Set when archived
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