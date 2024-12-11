from django.db import models
from base.models import User
from django.utils import timezone
import json, random
import wget
import os
from django.contrib.auth.models import User
import time
from django.urls import reverse  # Import reverse function from django.urls
from bs4 import BeautifulSoup  # Import BeautifulSoup
import threading
import urllib.parse
from django.conf import settings

WEBSITE_DOMAIN = settings.WEBSITE_DOMAIN
characters_to_replace = [
    "/",
    "#",
    "?",
    "&",
    "=",
    "+",
    "%",
    "\\",
    "|",
    "{",
    "}",
    "[",
    "]",
    "^",
    "`",
    "<",
    ">",
    '"',
    "'",
    ":",
    ";",
    "@",
    "!",
    "$",
    "(",
    ")",
    "*",
    ",",
    ".",
    "~",
]


def get_random_job_id():
    return random.randint(898211, 9834729792314)


class save_job(models.Model):
    job = models.ForeignKey("Job", on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return str(f"{self.job} - {self.user}")


class Organization(models.Model):
    name = models.CharField(max_length=255)
    website = models.CharField(max_length=255, null=True, blank=True)
    logo = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        default="https://talenttrackers.online/public/placeholder.png",
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_keywords(self):
        return [self.name]

    def title(self):
        return self.name + " Jobs"

    def get_absolute_url(self):
        return WEBSITE_DOMAIN + f"/organization/{urllib.parse.quote(self.name)}"

    def get_mod_date(self):
        current_time = timezone.now()
        return current_time.strftime("%Y-%m-%d")


class Address(models.Model):
    locality = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    complete_address = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.complete_address:
            a = ""
            if self.locality:
                a += self.locality

            if self.region and a:
                a += f", {self.region}"
            else:
                a = self.region

            if a:
                a += f", {self.country}"
            else:
                a = self.country

            self.complete_address = a
        super().save(*args, **kwargs)

    def get(self):
        a = ""
        if self.locality:
            a += self.locality

        if self.region and a:
            a += f", {self.region}"
        else:
            a = self.region

        if a:
            a += f", {self.country}"
        else:
            a = self.country
        return a

    def name(self):
        return self.complete_address

    def get_absolute_url(self):
        return (
            WEBSITE_DOMAIN
            + f"/job/?location={urllib.parse.quote(self.complete_address)}"
        )

    def get_mod_date(self):
        return self.updated_at.strftime("%Y-%m-%d")

    def __str__(self):
        return str(self.get())


class Salary(models.Model):

    currency = models.CharField(max_length=10)
    minValue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    maxValue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unitText = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


class cache_job(models.Model):
    jobs = models.JSONField(null=True, blank=True, default=list)
    cache_key = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return self.cache_key

    def get(cache_key):
        try:
            return cache_job.objects.get(cache_key=cache_key).jobs
        except:
            pass

    def set(cache_key, jobs):
        c, _ = cache_job.objects.get_or_create(cache_key=cache_key)
        c.jobs = jobs
        c.save()


class Job(models.Model):

    related_jobs = models.JSONField(null=True, blank=True, default=list)

    job_id = models.CharField(
        max_length=20, null=True, blank=True, default=get_random_job_id
    )
    og_job_id = models.CharField(max_length=20, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="job_organization",
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="address_job",
    )
    salary = models.ForeignKey(
        Salary,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="salary_job",
    )
    datePosted = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    validThrough = models.DateTimeField(null=True, blank=True)
    apply_url = models.TextField(null=True, blank=True)
    schema = models.JSONField(null=True, blank=True)

    address_locality = models.CharField(max_length=255, null=True, blank=True)
    address_region = models.CharField(max_length=255, null=True, blank=True)
    address_country = models.CharField(max_length=255, null=True, blank=True)
    address_complete_address = models.TextField(null=True, blank=True)

    organization_name = models.CharField(max_length=255, null=True, blank=True)
    organization_website = models.URLField(max_length=255, null=True, blank=True)
    organization_logo = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        default="https://talenttrackers.online/public/placeholder.png",
    )

    salary_currency = models.CharField(max_length=255, null=True, blank=True)
    salary_minValue = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, null=True, blank=True
    )
    salary_maxValue = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, null=True, blank=True
    )
    salary_unitText = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("job_id", "id")

    def save(self, *args, **kwargs):
        if not self.address_complete_address:
            a = ""
            if self.address_locality:
                a += self.address_locality

            if self.address_region and a:
                a += f", {self.address_region}"
            else:
                a = self.address_region

            if a:
                a += f", {self.address_country}"
            else:
                a = self.address_country

            self.address_complete_address = a

        super().save(*args, **kwargs)

    def get_mod_date(self):
        return self.updated_at.strftime("%Y-%m-%d")

    def priority(self):
        return 0.9

    def get_keywords(self):
        return [self.title]

    def __str__(self):
        return self.title

    def time_since_posted(self):
        now = timezone.now()
        diff = now - self.datePosted
        if diff.days > 365:
            return f"{diff.days // 365} year(s) ago"
        if diff.days > 30:
            return f"{diff.days // 30} month(s) ago"
        if diff.days > 0:
            return f"{diff.days} day(s) ago"
        if diff.seconds > 3600:
            return f"{diff.seconds // 3600} hour(s) ago"
        if diff.seconds > 60:
            return f"{diff.seconds // 60} minute(s) ago"
        return "just now"

    def get_schema(self):
        del self.schema["apply_url"]
        self.schema.pop("apply_url", None)
        schema_json = json.dumps(self.schema, ensure_ascii=False)
        return schema_json

    def get_absolute_url(self):
        return WEBSITE_DOMAIN + f"/job/{self.job_id}/{urllib.parse.quote(self.title)}/"

    def get_formatted_description(self):
        if self.description:
            # Parse HTML content using BeautifulSoup
            soup = BeautifulSoup(self.description, "html.parser")
            # Extract text content
            text_content = soup.text[:200]
            return text_content
        else:
            return ""

    def is_expired(self):
        current_time = timezone.now()
        return self.validThrough <= current_time if self.validThrough else False

    def organization_get_absolute_url(self):
        return (
            WEBSITE_DOMAIN
            + f"/organization/{urllib.parse.quote(self.organization_name)}"
        )

    def address_get_absolute_url(self):
        return (
            WEBSITE_DOMAIN
            + f"/job/?location={urllib.parse.quote(self.address_complete_address)}"
        )