
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new-post", views.new_post, name="new-post"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("profile/follow/<int:id>", views.follow, name="follow"),
    path("profile/unfollow/<int:id>", views.unfollow, name="unfollow")
]
