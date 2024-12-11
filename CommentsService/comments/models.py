

from django.db import models
from django.utils import timezone

# Create your models here.


class User(models.Model):
    """User model from ERD.

    Note the local user email is for the local user record, linking to external auth API via email.
    The external API handles actual authentication.
    """
    user_id = models.AutoField(primary_key=True)
    user_email = models.CharField(max_length=254, unique=True)
    is_admin = models.BooleanField(default=False)  # Boolean field for admin status
    class Meta:
        db_table = 'User'
    
    def __str__(self):
        return f"{self.user_email} ({'Admin' if self.is_admin else 'User'})"


class Comment(models.Model):
    """`Comment` model with all fields from ERD but using Django naming conventions."""

    comment_id = models.AutoField(primary_key=True, db_column='CommentID')
    trail_id = models.IntegerField(db_column='TrailID')
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='UserID')
    comment_text = models.TextField(db_column='CommentText')
    datetime_posted = models.DateTimeField(default=timezone.now, db_column='DatetimePosted')
    is_edited = models.BooleanField(default=False, db_column='IsEdited')
    last_edit_datetime = models.DateTimeField(null=True, blank=True, db_column='LastEditDateTime')
    is_archived = models.BooleanField(default=False, db_column='IsArchived')
    archived_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='archived_comments',
        db_column='ArchivedByID'
    )
    
    class Meta:
        db_table = 'Comment'
        ordering = ['-datetime_posted']
    
    def save(self, *args, **kwargs):
        """Track when comment is edited."""
        if self.pk and not self._state.adding:
            self.is_edited = True
            self.last_edit_datetime = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Comment {self.comment_id} by {self.user.user_email} on trail {self.trail_id}"
