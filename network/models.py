from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_user")
    post_text = models.TextField()
    post_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} posted at {self.post_date}"

class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follow_user")
    follow = models.ManyToManyField(User, related_name="follow")

    def __str__(self):
        return f"{self.user}"

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="like_user")
    post = models.ManyToManyField(Post, related_name="like_post")

    def __str__(self):
        return f"{self.user} at {self.post_date}"



