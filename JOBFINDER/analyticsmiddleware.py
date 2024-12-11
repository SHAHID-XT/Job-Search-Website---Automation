# middleware.py
from django.http import HttpResponseNotFound
from django.shortcuts import render
from analytics.views import *
from django.utils import timezone
from analytics.models import *


class AnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self.process_request(request, response)
        update_user_visit_count(request)
        if response.status_code == 500:
            return render(request, "404.html")
        return response

    def process_request(self, request, response):
        page_url = request.path
        donotstore = True
        exclude = ["media", "admin", ".png", ".jpg", ".js", ".css", "xtc-"]

        for pattern in exclude:
            if pattern in request.path:
                donotstore = False

        if donotstore and not response.status_code == 500:
            session_id = request.session.session_key
            ip_address = request.META.get("REMOTE_ADDR")
            user = request.user if request.user.is_authenticated else None

            page, _ = Page.objects.get_or_create(url=page_url)

            last_interaction = (
                UserInteraction.objects.filter(session_id=session_id)
                .order_by("-timestamp")
                .first()
            )

            if last_interaction:
                if last_interaction.page_to != page:
                    time_spent_seconds = (
                        timezone.now() - last_interaction.timestamp
                    ).total_seconds()
                    last_interaction.time_spent = int(time_spent_seconds)
                    last_interaction.save(force_update=True)
                    UserInteraction.objects.create(
                        user=user,
                        page_from=last_interaction.page_to,
                        page_to=page,
                        timestamp=timezone.now(),
                        session_id=session_id,
                        ip_address=ip_address,
                        browser=str(request.user_agent.device.family)
                        + " - "
                        + str(request.user_agent.browser),
                    )
            else:
                UserInteraction.objects.create(
                    user=user,
                    page_from=None,  # Set page_from to None for the first interaction
                    page_to=page,
                    timestamp=timezone.now(),
                    session_id=session_id,
                    ip_address=ip_address,
                    browser=str(request.user_agent.device.family)
                    + " - "
                    + str(request.user_agent.browser),
                )

    def process_response(self, request, response):
        session_id = request.session.session_key
        try:
            last_interaction = UserInteraction.objects.filter(
                session_id=session_id
            ).latest("timestamp")
            time_spent_seconds = (
                timezone.now() - last_interaction.timestamp
            ).total_seconds()
            last_interaction.time_spent = int(time_spent_seconds)
            last_interaction.save()
        except UserInteraction.DoesNotExist:
            pass
        return response
