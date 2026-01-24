from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Blog(models.Model):
    banner = models.ImageField(upload_to='blog_banner_pics', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.CharField()
    title = models.CharField(max_length=200)
    views = models.IntegerField(default=0)
    love_react = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    html_field = models.TextField()

    def __str__(self):
        return self.title

    
class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    comment_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    like_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Comment by {self.user} on {self.blog}"

class CommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_likes")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes")
    comment_flag = models.CharField(default="0",max_length=1)

    class Meta:
        unique_together = ('user', 'comment')  # prevent double likes

    def __str__(self):
        return f"{self.user.username} ❤️ {self.comment.id}"

class LoveReactShow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="love_reacts")
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="love_reacts")
    love_react = models.CharField(default=0)

    def __str__(self):
        return self.blog.title
    

class ReadStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="read_status_entries")
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="read_status_entries")
    read_sts = models.CharField(default=0)

    def __str__(self):
        return self.blog.title
    




