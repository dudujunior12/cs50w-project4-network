from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from itertools import chain

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
        follow_other_user_filter = Follow.objects.filter(user=other_user)
        if follow_other_user_filter:
            follow_other_user_obj = Follow.objects.get(user=other_user)

            followers_count = follow_other_user_obj.followers.count()
            following_count = follow_other_user_obj.following.count()

            followers = follow_other_user_obj.followers.all()
            if User.objects.get(username=request.user.username) in followers:
                button = "Unfollow"
            else:
                button = "Follow"
        else:
            followers_count = 0
            following_count = 0


        follow = {
            "followers_count": followers_count,
            "following_count": following_count,
            "button": button
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
        if follow_filter_user and follow_filter_other_user:
            follow_obj_user = Follow.objects.get(user=username)
            follow_obj_user.following.add(other_user)
            follow_obj_user.save()
            
            follow_obj_other_user = Follow.objects.get(user=other_user)
            follow_obj_other_user.followers.add(username)
            follow_obj_other_user.save()

        if not follow_filter_user:
            follow_obj_user = Follow.objects.create(user=username)
            follow_obj_user.following.add(other_user)
            follow_obj_user.save()

        if not follow_filter_other_user:
            follow_obj_other_user = Follow.objects.create(user=other_user)
            follow_obj_other_user.followers.add(username)
            follow_obj_other_user.save()
        

    return redirect('profile', username=other_user)

@login_required
def unfollow(request, id):
    username = get_object_or_404(User, username=request.user.username)
    other_user = get_object_or_404(User, id=id)
    if request.method == "POST":
        follow_filter_user = Follow.objects.filter(user=username)
        follow_filter_other_user = Follow.objects.filter(user=other_user)

        #Check if exist a follow database for the user, if not, it creates one. Then it adds the other user to the following field
        if follow_filter_user and follow_filter_other_user:
            follow_obj_user = Follow.objects.get(user=username)
            follow_obj_user.following.remove(other_user)
            follow_obj_user.save()
            
            follow_obj_other_user = Follow.objects.get(user=other_user)
            follow_obj_other_user.followers.remove(username)
            follow_obj_other_user.save()

        if not follow_filter_user:
            follow_obj_user = Follow.objects.create(user=username)
            follow_obj_user.save()

        if not follow_filter_other_user:
            follow_obj_other_user = Follow.objects.create(user=other_user)
            follow_obj_other_user.save()
        

    return redirect('profile', username=other_user)

def following(request):
    user = User.objects.get(username=request.user.username)
    form = CreatePost()
    
    # Get following users
    followings = Follow.objects.get(user=user).following.all()

    # Get all posts sorted by the following users
    posts = []
    for following in followings:
        posts.append(Post.objects.filter(user=following).order_by('-post_date'))

    # Combine posts of different users
    for i in range(len(posts) - 1):
        combined_posts = posts[i] | posts[i+1]
    

    return render(request, 'network/following.html', {
        "form": form,
        "posts": combined_posts
    })


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
