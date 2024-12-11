from django.urls import path, include
from .views import *
from django.utils import timezone

current_time = timezone.now()

urlpatterns = [
    path("", home_view, name="home"),
    path("job/", job_view, name="job"),
    path("organization/<str:org>/", job_view_org, name="job-org"),
    path("job/<str:job_id>/<str:title>/", job_detail_view, name="job-detail"),
    path("apply/<str:job_id>/", apply_link_view, name="apply-link"),
    path("organizations/", organizations_view, name="organization"),
    path("job/save/", save_job_view, name="save-job"),
    path("logout/", logout_view, name="logout"),
    path("privacy/", privacy_view, name="privacy"),
    path("about/", contact_us_view, name="about"),
    path("redirect/", redirect_url, name="redirect"),
    path(
        "sitemap-organizations.xml/",
        organizations_sitemap_view,
        name="organizations_sitemap_view",
    ),
    path(
        "sitemap-address.xml/",
        address_sitemap_view,
        name="address_sitemap_view",
    ),
    path(
        "sitemaps-indexes.xml/",
        index_sitemap_view,
        name="sitemap_index",
    ),
    path(
        "robots.txt/",
        robots_view,
        name="robots_view",
    ),
    path(
        "BingSiteAuth.xml/",
        BingSiteAuth,
        name="BingSiteAuth",
    ),
    path(
        "ads.txt/",
        ads_text_view,
        name="ads_text_view",
    ),
    path(
        "xt/",
        post_view,
        name="post_view",
    ),
    path(
        "job-page-<int:page>.xml/",
        job_sitemap_view,
        name="job_sitemap",
    ),
    path("/admin/bkl/",test,name="bkl")
]
