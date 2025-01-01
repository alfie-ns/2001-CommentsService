

from django.db import models
from django.utils import timezone

# Create your models here.


class User(models.Model):
    """`User` model from ERD.

    Note the local user email field is for the local user record, linking to external auth API via email.
    The external API handles actual authentication.
    """
    user_id = models.AutoField(primary_key=True) # primary key for User (UserID)
    user_email = models.CharField(max_length=254, unique=True) # email field for holding the user's email (UserEmail)
    is_admin = models.BooleanField(default=False)  # Boolean field for admin status
    
    class Meta:
        db_table = 'CW2.User'
    
    def __str__(self):
        return f"{self.user_email} ({'Admin' if self.is_admin else 'User'})"
    
# ---

class Comment(models.Model):
    """`Comment` model with all fields from ERD but using Django naming conventions."""

    comment_id = models.AutoField(primary_key=True, db_column='CommentID') # primary key for Comment (CommentID)
    trail_id = models.IntegerField(db_column='TrailID') # foreign key to Trail table (TrailID)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='UserID') # foreign key to User table (UserID)
    comment_text = models.TextField(db_column='CommentText') # text field for holding comments' text (CommentText)
    datetime_posted = models.DateTimeField(default=timezone.now, db_column='DatetimePosted') # datetime field for holding the date and time when the comment was posted (DatetimePosted)
    is_edited = models.BooleanField(default=False, db_column='IsEdited') # Boolean field to track if the comment has been edited (IsEdited)
    last_edit_datetime = models.DateTimeField(null=True, blank=True, db_column='LastEditDateTime') # datetime field for holding the date and time when the comment was last edited (LastEditDateTime)
    is_archived = models.BooleanField(default=False, db_column='IsArchived') # Boolean field to track if the comment has been archived (IsArchived)
    archived_by = models.ForeignKey( # this foreign key links to the User who archived the comment
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='archived_comments',
        db_column='ArchivedByID'
    )
    
    class Meta:
        db_table = 'CW2.Comment'
        ordering = ['-datetime_posted']
    
    def save(self, *args, **kwargs):
        """Track when comment is edited."""
        if self.pk and not self._state.adding: # if the comment is not null and not being created
            self.is_edited = True
            self.last_edit_datetime = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Comment {self.comment_id} by {self.user.user_email} on trail {self.trail_id}"
    
# ---
    
class Reply(models.Model):
    """`Reply` model representing a reply to a comment."""

    reply_id = models.AutoField(primary_key=True, db_column='ReplyID') # primary key for Reply (ReplyID)
    comment_id = models.ForeignKey(Comment, on_delete=models.CASCADE, db_column='CommentID') # foreign key to Comment table (CommentID)
    reply_user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='ReplyUserID') # foreign key to User table (ReplyUserID)
    reply_text = models.TextField(db_column='ReplyText') # text field for holding the reply text (ReplyText)
    reply_datetime = models.DateTimeField(default=timezone.now, db_column='ReplyDateTime') # datetime field for holding the reply date and time (ReplyDateTime)

    class Meta:
        db_table = 'CW2.Reply'
        ordering = ['-reply_datetime']

    def __str__(self):
        return f"Reply {self.reply_id} to Comment {self.comment_id.comment_id} by {self.reply_user_id.user_email}"

