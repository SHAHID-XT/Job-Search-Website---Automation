from django.shortcuts import render, redirect
from .models import Job
from django.core.paginator import Paginator
from .utils import *
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from django.core.cache import cache
from html.parser import HTMLParser
from django.shortcuts import render
import json
import threading
from django.http import HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from .scraper import insert_jobs_from_list
from django.utils import timezone
from job.models import Job
import html
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.db.models import Model
from datetime import datetime as default_datetime
import hashlib

WEBSITE_DOMAIN = settings.WEBSITE_DOMAIN
current_time = timezone.now()


def robots_view(request):
    return render(request, "robots.txt")


def BingSiteAuth(request):
    return render(request, "BingSiteAuth.xml")


def ads_text_view(request):
    response = render(request, "ads.txt")
    response["Content-Type"] = "text/plain"
    return response


def index_sitemap_view(request):
    current_time = timezone.now()
    mod_date = current_time.strftime("%Y-%m-%d")
    total_jobs = Job.objects.filter(validThrough__gt=current_time).count()
    num_sitemaps = (total_jobs // 10000) + 1
    index = []
    for i in range(0, num_sitemaps):
        index.append(f"{WEBSITE_DOMAIN}/job-page-{i}.xml/")

    for name in ["organizations", "address"]:
        index.append(f"{WEBSITE_DOMAIN}/sitemap-{name}.xml/")

    response = render(
        request, "sitemap-index.xml", context={"index": index, "mod_date": mod_date}
    )
    response["Content-Type"] = "application/xml"
    return response


def organizations_sitemap_view(request):
    current_time = timezone.now()
    mod_date = current_time.strftime("%Y-%m-%d")
    organizations = Job.objects.values("organization_name").distinct()
    changefreq = "weekly"
    response = render(
        request,
        "sitemap-org.xml",
        context={"jobs": organizations, "mod_date": mod_date, "changefreq": changefreq},
    )
    response["Content-Type"] = "application/xml"
    return response


def address_sitemap_view(request):
    current_time = timezone.now()
    mod_date = current_time.strftime("%Y-%m-%d")
    address = Job.objects.values("address_complete_address").distinct()
    changefreq = "weekly"
    response = render(
        request,
        "sitemap-address.xml",
        context={"jobs": address, "mod_date": mod_date, "changefreq": changefreq},
    )
    response["Content-Type"] = "application/xml"
    return response


def job_sitemap_view_old(request, page):
    current_time = timezone.now()
    start_index = (page - 1) * 10000
    end_index = page * 10000
    jobs = Job.objects.filter(validThrough__gt=current_time)[start_index:end_index]
    changefreq = "weekly"
    response = render(
        request,
        "sitemap-detail.xml",
        context={"jobs": jobs, "changefreq": changefreq},
    )
    response["Content-Type"] = "application/xml"
    return response


def job_sitemap_view(request, page):
    first_video_id = Job.objects.first().id
    las_video_id = Job.objects.last().id
    start_index = first_video_id + (page * 10000)
    end_index = start_index + 10000
    if end_index > las_video_id:
        videos = list(range(start_index, las_video_id + 1))
    else:
        videos = list(range(start_index, end_index + 1))
    changefreq = "weekly"
    get_mod_date = default_datetime.now().strftime("%Y-%m-%d")
    response = render(
        request,
        "sitemap-detail2.xml",
        context={
            "videos": videos,
            "changefreq": changefreq,
            "get_mod_date": get_mod_date,
        },
    )
    response["Content-Type"] = "application/xml"
    return response


@csrf_exempt
def post_view(request):
    if request.method == "POST":
        data = request.body.decode("utf-8")
        if type(data) == str:
            json_data = json.loads(data)
        if data:
            try:
                json_data = json.loads(data)
                # print(json_data)
                if type(json_data) == list:
                    insert_jobs_from_list(json_data, WEBSITE_DOMAIN, True)
                else:
                    insert_jobs_from_list([json_data], WEBSITE_DOMAIN, True)

            except json.JSONDecodeError as e:
                return HttpResponseNotFound()

    return HttpResponseNotFound()


def privacy_view(request):
    return render(request, "privacy.html")


def contact_us_view(request):
    return render(request, "contact-us.html")


def home_view(request):
    return render(request, "index.html")


def logout_view(request):
    logout(request)
    return redirect("/")


@csrf_exempt
def save_job_view(request):
    return
    result = {"success": False, "login": False, "created": False}
    if request.method == "POST" and request.user.is_authenticated:
        result["login"] = True
        job_id = request.GET.get("job_id")
        user = request.user
        job = get_jobs()
        job = job.get(job_id=job_id)
        is_exists = False
        try:
            is_exists = save_job.objects.filter(job_id=job, user=user)
        except:
            pass
        if not is_exists:
            save_job.objects.create(job=job, user=user)
            result["created"] = True
            result["success"] = True
        else:
            result["success"] = True
    return JsonResponse(result)


def job_detail_view(request, job_id, title):
    domain = request.META.get("HTTP_HOST")
    template_name = "job_detail.html"
    is_job_saved = False

    if title == "Job Vacancies":
        job = Job.objects.get(id=job_id)
    else:
        job = Job.objects.get(job_id=job_id)

    if job.related_jobs:
        jobs = Job.objects.filter(id__in=job.related_jobs)
    else:
        jobs = get_jobs(
            job_title=job.title, job_address=job.address_complete_address, only_ids=True
        )
        try:
            jobs = [f.id for f in jobs]
        except:
            pass
        job.related_jobs = jobs
        job.save()
        jobs = Job.objects.filter(id__in=jobs)

    description = job.get_formatted_description()[:150]
    copyright = domain
    author = domain
    ogsite_name = domain
    ogdescription = description
    keywords = generate_keywords(job)

    title = f"Apply for {job.title} at {job.organization_name}, {job.address_complete_address}"

    context = {
        "job": job,
        "title": title,
        "jobs": list(jobs)[0:10],
        "copyright": copyright,
        "author": author,
        "ogsite_name": ogsite_name,
        "ogtitle": title,
        "ogdescription": ogdescription,
        "description": description,
        "keywords": keywords,
        "job_id": job.job_id,
        "is_job_saved": is_job_saved,
    }
    return render(request, template_name, context=context)


def job_view(request):
    is_filter_query = None
    is_location_filter = None
    title = "Jobs - Recruitment - Job Search -  Employment - Job Vacancies - Jobs"
    search_query = request.GET.get("q", None)

    location = request.GET.get("location", None)

    if search_query:
        search_query = search_query.strip()

    organization_query = request.GET.get("organization", None)
    if organization_query:
        organization_query = organization_query.strip()

    jobs = get_jobs(
        search_query=search_query,
        organization_query=organization_query,
        location=location,
    )

    paginator = Paginator(jobs, 20)  # Show 20 jobs per page
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    description = "Access job openings"
    if search_query:
        description += f" matching '{search_query}'"
    if organization_query:
        if search_query:
            description += " and"
        description += f" at {organization_query}"
    if not search_query and not organization_query:
        description += ". More opportunities. Less search."
    else:
        description = "Access the complete list of job openings in all the United Nations and major international organizations. More opportunities. Less search."

    next_query = (
        f"?q={search_query}&organization={organization_query}"
        if search_query and organization_query
        else (
            f"?q={search_query}"
            if search_query
            else f"?organization={organization_query}" if organization_query else ""
        )
    )

    if not next_query and page_number and page_obj.has_next():
        next_query += f"?page={page_obj.next_page_number()}"
    elif next_query and page_number and page_obj.has_next():
        next_query += f"&page={page_obj.next_page_number()}"

    context = {
        "title": title,
        "description": description[:150],
        "ogdescription": description,
        "jobs": page_obj,
        "page_obj": page_obj,
        "search_query": search_query,
        "is_filter_query": is_filter_query,
        "next_query": next_query,
        "is_location_filter": is_location_filter,
    }

    return render(request, "job.html", context)


def job_view_org(request, org):
    is_organization = False
    is_filter_query = None
    search_query = request.GET.get("q", "")
    if search_query:
        search_query = search_query.strip()

    organization_query = org

    if organization_query:
        organization_query
        is_filter_query = organization_query

    jobs = get_jobs(search_query=search_query, organization_query=organization_query)

    paginator = Paginator(jobs, 20)  # Show 20 jobs per page
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    description = f"Discover {jobs.count()} job opportunities at {organization_query}. Explore roles in various industries and apply today."

    next_query = (
        f"?q={search_query}&organization={organization_query}"
        if search_query and organization_query
        else (
            f"?q={search_query}"
            if search_query
            else f"?organization={organization_query}" if organization_query else ""
        )
    )

    if not next_query and page_number and page_obj.has_next():
        next_query += f"?page={page_obj.next_page_number()}"
    elif next_query and page_number and page_obj.has_next():
        next_query += f"&page={page_obj.next_page_number()}"

    title = f"Job Openings at {organization_query}: Apply Today"
    context = {
        "is_organization": is_organization,
        "total_length": jobs.count(),
        "title": title,
        "jobs": page_obj,
        "page_obj": page_obj,
        "search_query": search_query,
        "is_filter_query": is_filter_query,
        "ogdescription": description,
        "description": description,
        "next_query": next_query,
    }

    return render(request, "job.html", context)


def apply_link_view(request, job_id):
    link = Job.objects.get(job_id=job_id)
    return redirect(link.apply_url)


def organizations_view(request):
    description = "Explore job opportunities at various organizations. Find roles that match your skills and interests. Apply now!"
    organizations = Job.objects.values(
        "organization_name", "organization_logo"
    ).distinct()[:300]

    return render(
        request,
        "organizations.html",
        {
            "organizations": organizations,
            "ogdescription": description,
            "description": description,
        },
    )


def redirect_url(request):
    url = request.GET.get("url", None)
    if url:
        return redirect(url)
    return redirect("/")


import html


def test(request):
    t = get_jobs(disable_cache=True)
    return JsonResponse({})
    jobs = Job.objects.all()

    for job in jobs:
        job.description = html.unescape(job.description)
        job.save()

    return JsonResponse({})
