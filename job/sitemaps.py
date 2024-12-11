# myapp/sitemaps.py
from django.contrib.sitemaps import Sitemap
from .models import Organization, Job, Address, Salary


class OrganizationSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Organization.objects.order_by("id")  # Order by a unique field, like 'id'


class JobSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return Job.objects.order_by("id")  # Order by a unique field, like 'id'


class AddressSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.6

    def items(self):
        return Address.objects.order_by("id")  # Order by a unique field, like 'id'


class SalarySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.6

    def items(self):
        return Salary.objects.order_by("id")  # Order by a unique field, like 'id'
