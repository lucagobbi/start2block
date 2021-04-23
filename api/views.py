from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from .models import Post
from .forms import PostModelForm
from django.views.generic import ListView, CreateView
from django.contrib.auth.models import User
from .mixins import StaffMixing
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from actions.utils import create_action
from django.utils import timezone
from datetime import timedelta

# homepage view
class HomeView(LoginRequiredMixin, ListView):
    queryset = Post.objects.all().order_by('-datetime')
    template_name = "api/homepage.html"
    context_object_name = "posts_list"

def posts(request):
    response = []
    posts = Post.objects.filter().order_by('-datetime')
    for post in posts:
        response.append(
            {
                'datetime': post.datetime,
                'content': post.content,
                'author': f"{post.user.first_name} {post.user.last_name}",
                'hash': post.hash,
                'txId': post.txId,
            }
        )
    return JsonResponse(response, safe=False)

# view for the creation of a new post --- uncomment below to enable blockchain messages
@login_required
def newPost(request):
    form = PostModelForm(request.POST)
    if form.is_valid():
        form.save(commit=False)
        form.instance.user = request.user
        form.save()
        #form.instance.writeOnChain()
        create_action(request.user, 'created a new post')
        return redirect("/")
    context = {
        'form': form
    }
    return render(request, "api/new_post.html", context)

# user profile view
def user_profile_view(request, id):
    user = get_object_or_404(User, id=id)
    context = {"user": user}

    return render(request, "api/profile.html", context)

# staff-only view that renders users activity
class UserPostListView(StaffMixing, ListView):
    queryset = User.objects.all()
    template_name = "api/user_post_list.html"
    context_object_name = "users"

# endpoint to collect JSON info about last hour posts
def posts_json_view(request):
    posts = Post.objects.filter(datetime__gte=timezone.now() - timedelta(hours=1))
    data = {"posts": list(posts.values())}
    response = JsonResponse(data)
    return response


# endpoint that receives a string with GET and return the n of posts that contain the string
def search(request):
    if "q" in request.GET:
        querystring = request.GET.get("q")
        if len(querystring) == 0:
            return redirect("/search/")
        posts = Post.objects.filter(content__icontains=querystring)
        context = {"posts": posts, "querystring": querystring}
        return render(request, "api/search.html", context)
    else:
        return render(request, "api/search.html")
