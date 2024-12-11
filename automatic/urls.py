from django.urls import path
from django.utils import timezone
from .views import *

current_time = timezone.now()


urlpatterns = [
    # path(
    #     "sitemap-organizations.xml/",
    #     organizations_sitemap_view,
    #     name="organizations_sitemap_view",
    # ),
    # path(
    #     "sitemap-address.xml/",
    #     address_sitemap_view,
    #     name="address_sitemap_view",
    # ),
    # path(
    #     "sitemaps-index.xml/",
    #     index_sitemap_view,
    #     name="sitemap_index",
    # ),
    # path(
    #     "robots.txt",
    #     robots_view,
    #     name="robots_view",
    # ),
    # path(
    #     "BingSiteAuth.xml",
    #     BingSiteAuth,
    #     name="BingSiteAuth",
    # ),
    # path(
    #     "ads.txt/",
    #     ads_text_view,
    #     name="ads_text_view",
    # ),
    # path(
    #     "xt/",
    #     post_view,
    #     name="post_view",
    # ),

]
