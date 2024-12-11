from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from base.models import User
from django.contrib.auth.hashers import make_password


def login_view(request):
    # messages.error(request, "we are not accepting login requests")
    # return render(request, "register.html")
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        # Authenticate using email and password
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return redirect("/")
        else:
            # Return an 'invalid login' error message.
            messages.error(request, "Invalid email or password.")
    return render(request, "login.html")


def register_view(request):
    # messages.error(request, "we are not accepting registration requests")
    # return render(request, "register.html")
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        password_confirmation = request.POST.get("password2")

        if password != password_confirmation:
            messages.error(request, "Passwords do not match.")
            return render(request, "register.html")
        else:
            # Check if the email is already registered
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email is already registered.")
                return render(request, "register.html")
            else:
                # Create the new user
                user = User.objects.create_user(
                    email=email, password=password, username=email
                )
                login(request, user)
                return redirect("/")

    return render(request, "register.html")
