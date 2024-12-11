from django.shortcuts import render
import json
import threading
from django.http import HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from automatic.scrape import insert_jobs_from_list
from django.utils import timezone
from job.models import Job, Organization, Address

from django.conf import settings

WEBSITE_DOMAIN = settings.WEBSITE_DOMAIN


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
    jobs = Job.objects.filter(validThrough__gt=current_time)
    total_jobs = jobs.count()
    num_sitemaps = (total_jobs // 1000) + 1
    index = []
    for i in range(1, num_sitemaps + 1):
        index.append(f'{request.build_absolute_uri(f"/job-sitemap-{i}.xml/")}')

    for name in ["organizations", "address"]:
        index.append(f'{request.build_absolute_uri(f"/sitemap-{name}.xml/")}')

    response = render(
        request, "sitemap-index.xml", context={"index": index, "mod_date": mod_date}
    )
    response["Content-Type"] = "application/xml"
    return response


def organizations_sitemap_view(request):
    current_time = timezone.now()
    mod_date = current_time.strftime("%Y-%m-%d")
    organizations = Organization.objects.all()
    changefreq = "daily"
    response = render(
        request,
        "sitemap-detail.xml",
        context={"jobs": organizations, "mod_date": mod_date, "changefreq": changefreq},
    )
    response["Content-Type"] = "application/xml"
    return response


def address_sitemap_view(request):
    current_time = timezone.now()
    mod_date = current_time.strftime("%Y-%m-%d")
    address = Address.objects.all()
    changefreq = "daily"
    response = render(
        request,
        "sitemap-detail.xml",
        context={"jobs": address, "mod_date": mod_date, "changefreq": changefreq},
    )
    response["Content-Type"] = "application/xml"
    return response


def job_sitemap_view(request, page):
    current_time = timezone.now()
    start_index = (page - 1) * 1000
    end_index = page * 1000
    jobs = Job.objects.filter(validThrough__gt=current_time).order_by("-created_at")[
        start_index:end_index
    ]
    changefreq = "monthly"
    response = render(
        request,
        "sitemap-detail.xml",
        context={"jobs": jobs, "changefreq": changefreq},
    )
    response["Content-Type"] = "application/xml"
    return response


@csrf_exempt
def post_view(request):
    if request.method == "POST":
        data = request.body.decode("utf-8")
        # print(data)
        if data:
            try:
                json_data = json.loads(data)
                insert_jobs_from_list([json_data], WEBSITE_DOMAIN, True)

            except json.JSONDecodeError as e:
                return HttpResponseNotFound()

    return HttpResponseNotFound()
