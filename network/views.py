from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .forms import *
from .models import *


def index(request):
    form = CreatePost()
    all_posts = Post.objects.all()
    return render(request, "network/index.html", {
        "form": form,
        "all_posts": all_posts,
    })

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
    user = get_object_or_404(User, username=username)
    if user:
        posts = Post.objects.filter(user=user)
        return render(request, "network/profile.html", {
            "user": user, "posts": posts,
        })
    return render(request, "network/profile.html", {})

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
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
