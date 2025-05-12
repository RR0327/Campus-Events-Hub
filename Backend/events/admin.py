from django.contrib import admin
from .models import CustomUser, Event, Registration, Cancellation

admin.site.register(CustomUser)
admin.site.register(Event)
admin.site.register(Registration)
admin.site.register(Cancellation)
