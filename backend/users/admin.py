from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

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
# тут я зарегистрировал кастомную модель (CustomUser)
# и модель, которую описал в админке выше (CustomUserAdmin)
# возможно это неправильно, т.к. в документации регистрируется
# только кастомная модель (CustomUser) и встроенный UserAdmin
admin.site.register(Follow)
