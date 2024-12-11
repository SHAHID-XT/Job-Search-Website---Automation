import json
import os, time
from django.core.management.base import BaseCommand
from job.models import Job
import gc, random


class Command(BaseCommand):
    help = "Cache data every hour"

    def handle(self, *args, **kwargs):
        files = [os.path.join("data", f) for f in os.listdir("data")]
        files = [random.choice(files)]
        for file_path in files:
            try:
                print(f"Processing file: {file_path}")
                jobs_data = []

                with open(file_path, "r", encoding="utf-8") as file:
                    jobs_data = json.load(file)

                Job.objects.bulk_create([Job(**job) for job in jobs_data])

                print(f"Created {len(jobs_data)} jobs from {file_path}")
                os.remove(file_path)
            except Exception as e:
                print(e)
                print(f"Failed {len(jobs_data)} jobs from {file_path}")
                pass

        self.stdout.write(self.style.SUCCESS("All jobs created successfully"))
