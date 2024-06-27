from django.contrib import admin
from .models import User, Trip

# Register your models here.
class TripInLine(admin.TabularInline):
    model = Trip

class UserAdmin(admin.ModelAdmin):
    fieldsets = [
        ('User Email', {'fields': ['user_email']}),
    ]
    inlines = [TripInLine]

admin.site.register(User, UserAdmin)
admin.site.register(Trip)
