from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
import json

from .forms import *
from .models import *


def index(request):
    form = CreatePost()

    # Get liked posts id
    try:
        user = User.objects.get(username=request.user.username)
        like = Like.objects.get(user=user)
        liked_id = []
        for liked_posts in like.posts.all():
            liked_id.append(liked_posts.id)
    except:
        liked_id = []


    # Paginator
    post_list = Post.objects.all().order_by("-post_date")
    paginator = Paginator(post_list, 10)
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, "network/index.html", {
        "form": form,
        "posts": posts,
        "page_range": paginator.page_range,
        "liked_id": liked_id
    })

@login_required
def new_post(request):
    if request.method == "POST":
        # Form to create a new post
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
    
    # Get liked posts id
    try:
        user = User.objects.get(username=request.user.username)
        like = Like.objects.get(user=user)
        liked_id = []
        for liked_posts in like.posts.all():
            liked_id.append(liked_posts.id)
    except:
        liked_id = []

    # Checks if other_user exists, then gets all posts
    if other_user:
        post_list = Post.objects.filter(user=other_user).order_by("-post_date")
        paginator = Paginator(post_list, 10)
        page = request.GET.get('page')
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        # Filter followers and following count
        follow_other_user_filter = Follow.objects.filter(user=other_user)
        if follow_other_user_filter:
            follow_other_user_obj = Follow.objects.get(user=other_user)

            followers_count = follow_other_user_obj.followers.count()
            following_count = follow_other_user_obj.following.count()

            followers = follow_other_user_obj.followers.all()
            # Change button to Follow/Unfollow if current user follows it or not
            try:
                if User.objects.get(username=request.user.username) in followers:
                    button = "Unfollow"
            except:
                button = "Follow"
        else:
            button = "Follow"
            followers_count = 0
            following_count = 0


        follow = {
            "followers_count": followers_count,
            "following_count": following_count,
            "button": button,
            "liked_id": liked_id
        }

        return render(request, "network/profile.html", {
            "other_user": other_user, 
            "posts": posts,
            "follow": follow,
            "page_range": paginator.page_range,
            "liked_id": liked_id
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

@login_required
def following(request):
    user = User.objects.get(username=request.user.username)
    form = CreatePost()
    
    try:
        like = Like.objects.get(user=user)
        liked_id = []
        for liked_posts in like.posts.all():
            liked_id.append(liked_posts.id)
    except:
        liked_id = []

    page = request.GET.get('page')

    # Get following users
    followings = Follow.objects.get(user=user).following.all()

    # Get all posts sorted by the following users
    post_list = []
    for following in followings:
        post_list.append(Post.objects.filter(user=following).order_by('-post_date'))

    combined_post = None
    # Combine posts of different users
    for i in range(len(post_list) - 1):
        combined_post = post_list[i] | post_list[i+1]
    

    if combined_post:
        paginator = Paginator(combined_post, 10)
        page = request.GET.get('page')
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        
        return render(request, 'network/following.html', {
            "form": form,
            "posts": posts,
            "page_range": paginator.page_range,
            "liked_id": liked_id
        })

    posts = []
    for posts_out_list in post_list:
        posts = posts_out_list
    
    return render(request, 'network/following.html', {
        "form": form,
        "posts": posts,
        "liked_id": liked_id
    })

@csrf_exempt
@login_required
def edit_post(request, id):
    if request.method == "POST":
        # Get data from fetch, then updates the post
        user = User.objects.get(username=request.user.username)
        post = Post.objects.get(id=id, user=user)
        data = json.loads(request.body)
        if data.get("post_text") is not None:
            post.post_text = data['post_text']
        post.save()
        return JsonResponse({"message": "Post edited successfully.", "post_text": post.post_text}, status=201)
    else:
        return JsonResponse({"message_error": "Require POST request method"}, status=404)

@csrf_exempt
@login_required
def like(request, id):
    if request.method == "POST":
        # Get data from fetch, creates a Like object and add/remove a post to it, if object already exists just add/remove

        user = User.objects.get(username=request.user.username)
        post = Post.objects.get(id=id)
        data = json.loads(request.body)

        if Like.objects.filter(user=user):
            like_obj = Like.objects.get(user=user)
            if data.get("liked") is not False and not None:
                like_obj.posts.add(post)
            if data.get("liked") is False:
                like_obj.posts.remove(post)
            like_obj.save()
        else:
            new_like = Like.objects.create(user=user)
            if data.get("liked") is not False and not None:
                new_like.posts.add(post)
            if data.get("liked") is False:
                new_like.posts.remove(post)
            new_like.save()

        # Filter all liked posts and count
        like_count = Like.objects.filter(posts__in=[post]).count()
        post.like_count = like_count
        post.save()
        
        return JsonResponse({"message": "Like updated", "like_count": like_count}, status=201)

    else:
        return JsonResponse({"message_error": "Require POST request method"}, status=404)


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
