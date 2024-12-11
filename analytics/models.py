from django.db import models
from base.models import User as CustomUser

class RequestLog(models.Model):
    ip_address = models.CharField(max_length=100)
    visit_count = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    def __str__(self):
        return str(
            f"{self.ip_address} has visit {self.visit_count} times"
        )


class User_Visit_page(models.Model):
    ip_address = models.CharField(max_length=100)
    page = models.CharField(max_length=200,null=True, blank=True)
    visit_count = models.IntegerField(null=True, blank=True,default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True,blank=True)
    def __str__(self):
        return f"IP: {self.ip_address} visit '{self.visit_count}' times. - {self.page}"


class Page(models.Model):
    url = models.URLField(unique=True)
    def __str__(self) -> str:
        return self.url




class UserInteraction(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True
    )
    page_from = models.ForeignKey(
        Page, on_delete=models.SET_NULL, null=True, blank=True, related_name="page_from"
    )
    page_to = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="page_to")
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    time_spent = models.CharField(null=True, blank=True, max_length=100)
    browser = models.CharField(null=True, blank=True, max_length=100)
    @classmethod
    def create_interaction(cls, user, page_from, page_to, session_id, ip_address):
        interaction = cls(
            user=user,
            page_from=page_from,
            page_to=page_to,
            session_id=session_id,
            ip_address=ip_address,
        )
        interaction.save()

    def __str__(self) -> str:
        if self.user:
            return f"User '{self.user}' visited from page '{self.page_from}' to page '{self.page_to}' - Time Spent: {self.time_spent} seconds"
        else:
            return f"Anonymous user with IP '{self.ip_address}' visited from page '{self.page_from}' to page '{self.page_to}' - Time Spent: {self.time_spent} seconds"
