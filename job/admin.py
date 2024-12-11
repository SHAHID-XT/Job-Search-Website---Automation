from django.contrib import admin
from .models import *


admin.site.site_header = "Talenttrackers"  
admin.site.index_title = "Talenttrackers"  
admin.site.site_title = "Talenttrackers"



admin.site.register(Job)
admin.site.register(Address)
admin.site.register(Organization)
admin.site.register(Salary)
admin.site.register(save_job)
admin.site.register(cache_job)



