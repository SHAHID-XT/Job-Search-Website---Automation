from django.apps import AppConfig
from .helper import *
import time

global is_running
is_running = False


class AutomaticConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "automatic"
    write_json(
        {
            "is_running": False,
        }
    )

    def ready(self):
        global is_running
        if not read_json()["is_running"] and not is_running:
            is_running = True
            from automatic.scrape import start_population_thread

            start_population_thread()
