from django.contrib import admin

from .models import Beneficiaries,Ration_Card,FPS,FPSInventory,FPSProfile

# Register your models here.
admin.site.register(Beneficiaries)
admin.site.register(Ration_Card)
admin.site.register(FPSProfile)
admin.site.register(FPS)
admin.site.register(FPSInventory)