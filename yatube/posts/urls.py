from django.urls import path

from . import views


app_name = 'posts'

urlpatterns = [
    path('', views.index, name='main_page'),
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('create/', views.post_create, name='post_create'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'
    ),
    path('follow/', views.followings_posts, name='followings'),
    path('follow/<str:username>/follow', views.author_follow, name='follow'),
    path(
        'follow/<str:username>/unfollow',
        views.author_unfollow,
        name='unfollow'
    ),
]
