from django.contrib import admin
from .models.base import Vitima_dados, Agressor_dados

# Register your models here.
admin.site.register(Vitima_dados)
admin.site.register(Agressor_dados)
