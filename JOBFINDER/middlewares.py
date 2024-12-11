# middleware.py
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from analytics.views import AnaIpAddress

class NotFoundMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        page_url = request.path
        response = self.get_response(request)
        self.process_request(request, response)
        AnaIpAddress(request)
        if page_url == "/":
            return redirect("/job/")
        
        return response

    def process_request(self, request, response):
        pass

    def process_response(self, request, response):
        session_id = request.session.session_key
        return response
