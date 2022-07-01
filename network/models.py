from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_user")
    post_text = models.TextField()
    post_date = models.DateTimeField(auto_now_add=True)
    like_count = models.IntegerField()

    def __str__(self):
        return f"{self.user} posted at {self.post_date}"

class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follow_user")
    followers = models.ManyToManyField(User, related_name="followers", blank=True, null=True)
    following = models.ManyToManyField(User, related_name="following", blank=True, null=True)

    def __str__(self):
        return f"{self.user}"

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="like_user")
    posts = models.ManyToManyField(Post, related_name="liked_posts")

    def __str__(self):
        return f"{self.user}"



