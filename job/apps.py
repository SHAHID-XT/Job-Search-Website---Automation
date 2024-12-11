from django.apps import AppConfig
import threading
import schedule
import time
import os



class JobConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "job"

