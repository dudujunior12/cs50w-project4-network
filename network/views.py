from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .forms import *
from .models import *


def index(request):
    form = CreatePost()
    posts = Post.objects.all().order_by("-post_date")
    return render(request, "network/index.html", {
        "form": form,
        "posts": posts,
    })

@login_required
def new_post(request):
    if request.method == "POST":
        form = CreatePost(request.POST)
        if form.is_valid():
            user = get_object_or_404(User, username=request.user.username)
            post_text = request.POST['post_text']
            p = Post(user=user, post_text=post_text)
            p.save()
        else:
            return JsonResponse({"message_error": "Couldn't create a new post"}, status=404)
        return redirect("index")
    else:
        return JsonResponse({"message_error": "Require POST request method"}, status=404)

def profile(request, username):
    other_user = get_object_or_404(User, username=username)
    
    if other_user:
        posts = Post.objects.filter(user=other_user).order_by("-post_date")

        follow_filter = Follow.objects.filter(user=other_user)
        if follow_filter:
            follow_obj = Follow.objects.get(user=other_user)
            followers_count = follow_obj.followers.count()
            following_count = follow_obj.following.count()
        else:
            followers_count = 0
            following_count = 0

        follow = {
            "followers_count": followers_count,
            "following_count": following_count
        }

        return render(request, "network/profile.html", {
            "other_user": other_user, 
            "posts": posts,
            "follow": follow,
        })
    return render(request, "network/profile.html", {})

@login_required
def follow(request, id):
    username = get_object_or_404(User, username=request.user.username)
    other_user = get_object_or_404(User, id=id)
    if request.method == "POST":
        follow_filter_user = Follow.objects.filter(user=username)
        follow_filter_other_user = Follow.objects.filter(user=other_user)

        #Check if exist a follow database for the user, if not, it creates one. Then it adds the other user to the following field
        if follow_filter_user:
            follow_obj_user = Follow.objects.get(user=username)
            follow_obj_user.following.add(other_user)
            follow_obj_user.save()
        else:
            follow_obj_user = Follow.objects.create(user=username)
            follow_obj_user.following.add(other_user)
            follow_obj_user.save()
        
        #Check if exist a follow database for the other user, if not, it creates one. Then it adds the user to the follower field
        if follow_filter_other_user:
            follow_obj_other_user = Follow.objects.get(user=other_user)
            follow_obj_other_user.followers.add(username)
            follow_obj_other_user.save()
        else:
            follow_obj_other_user = Follow.objects.create(user=other_user)
            follow_obj_other_user.followers.add(username)
            follow_obj_other_user.save()

    return redirect('profile', username=other_user)

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()

            follow = Follow.objects.create(user=user)
            follow.save()

        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
