from django.contrib import admin

# Register your models here.
from contents import models

admin.site.register(models.ContentCategory)
admin.site.register(models.Content)