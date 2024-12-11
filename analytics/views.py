from django.shortcuts import render
from .models import *
from .utils import get_client_ip
import threading



def update_user_visit_count(request):
    page_url = request.path
    exclude = ["media", "admin", ".png", ".jpg", ".js", ".css","boka"]
    for pattern in exclude:
        if pattern in request.path:
            return
    client_ip = get_client_ip(request)
    # Check if the IP address already exists in the database
    request_log, created = RequestLog.objects.get_or_create(
        ip_address=client_ip
    )

    request_log.visit_count += 1
    request_log.save()



def user_visit_log(request):
    page_url = request.path
    
    exclude = ["media", "admin", ".png", ".jpg", ".js", ".css","boka"]
    for pattern in exclude:
        if pattern in page_url:
            return
    ip_address = get_client_ip(request)
    login_record, created= User_Visit_page.objects.get_or_create(ip_address=ip_address,page=page_url)
    login_record.visit_count += 1  # Increment login count if record already exists
    login_record.save()

def AnaIpAddress(request):
    try:
        t2 = threading.Thread(target=update_user_visit_count,args=(request,))

        t.start()
        t2.start()
    except Exception as e: 
        pass
    

