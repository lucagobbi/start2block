from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name="homepage"),
    path('user/<int:id>/', views.user_profile_view, name="user_profile"),
    path('user-post-list/', views.UserPostListView.as_view(), name="user_post_list"),
    path('new-post/', views.newPost, name="new_post"),
    path('posts-json/', views.posts_json_view, name="posts-json"),
    path('search', views.search, name="search"),
]