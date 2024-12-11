from django.http import HttpResponseNotFound


def global_variables(request):
    page_path = request.path
    is_admin = False
    if request.user.is_authenticated and request.user.is_superuser:
        is_admin = True

    website_name = "TalentTrackers"
    website_name_small = "talentTrackers"
    contact_email = "support@talenttrackers.online"
    ads = """
    
    
    
    """
    return {
        "website_name": website_name,
        "request": request,
        "is_admin": is_admin,
        "copyright": website_name,
        "ogsite_name": website_name,
        "contact_email": contact_email,
        "ads":ads,
    }
