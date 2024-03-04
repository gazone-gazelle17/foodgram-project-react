from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import Follow, CustomUser


class CustomUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = (
        'email',
        'username'
    )
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name'
    )
    ordering = ('username',)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Follow)
admin.site.unregister(Group)
