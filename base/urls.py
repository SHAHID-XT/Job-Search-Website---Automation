from django.urls import path, include
from .views import *


urlpatterns = [
    path("login/", login_view, name="login_view"),
    path("register/", register_view, name="register_view"),
]
