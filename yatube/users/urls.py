from django.urls import path

from . import views


app_name = 'users'

urlpatterns = [
    path(
        'logout/',
        views.Logout.as_view(),
        name='logout'
    ),
    path(
        'signup/',
        views.SignUp.as_view(),
        name='signup'
    ),
    path(
        'login/',
        views.Login.as_view(),
        name='login'
    ),
]
