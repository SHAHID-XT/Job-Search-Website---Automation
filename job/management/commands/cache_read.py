import json
from django.core.management.base import BaseCommand
from django.core.serializers import serialize
from job.models import Job  # Adjust import according to your app and model
import requests
import random
class Command(BaseCommand):
    help = "Export job data to JSON"
    
    def handle(self, *args, **kwargs):
        jobs = Job.objects.all().order_by('-created_at')[:1000]

        related_jobs = [f.id for f in jobs]
        for job in jobs:
            if job.related_jobs:
                continue
            print(job.id)
            job.related_jobs =random.choices(related_jobs,k=10)
            job.save()
