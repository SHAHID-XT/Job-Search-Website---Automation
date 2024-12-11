# myapp/middleware.py

from django.conf import settings
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.utils import timezone
import random
import string
# from analytics.views import *
# myapp/middleware.py

from django.conf import settings
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.shortcuts import render, redirect


class CheckerMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "POST":
            # print(request.POST)
            pass

        response = self.get_response(request)
        return response


class FakeMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = "127.0.0.1"
        # try:
        #     AnaIpAddress(request)
        # except Exception as e:
        #     pass
        if not request.META["HTTP_HOST"] == settings.DOMAIN and not settings.DEBUG:
            user_ip = ip
            current_time = timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            characters = string.hexdigits
            random_string = "".join(random.choice(characters) for _ in range(16))
            return render(
                request,
                "cloudflare.html",
                context={
                    "user_ip": user_ip,
                    "current_time": current_time,
                    "random_string": random_string,
                },
            )
        

        response = self.get_response(request)
        return response


class RequestThrottleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # if not request.META['HTTP_HOST'] ==settings.DOMAIN :
        #     return render(request,"cloudflare.html")

        # Get the client IP address
        ip_address = self.get_client_ip(request)

        # Get the current count of requests for this IP address
        request_count = cache.get(ip_address, 0)

        # Increment the request count
        request_count += 1

        # Check if the request count exceeds the limit
        if request_count > getattr(settings, "REQUESTS_PER_IP_LIMIT", 100):
            return HttpResponseForbidden("You have exceeded the request limit.")

        # Set the new request count in the cache
        cache.set(
            ip_address, request_count, getattr(settings, "REQUEST_THROTTLE_TIMEOUT", 60)
        )

        # Pass the request to the next middleware or view
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
