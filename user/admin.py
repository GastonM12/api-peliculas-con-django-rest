from django.contrib import admin

from django.contrib.auth.admin import UserAdmin

from user.models import CustomUser


class CustomUserAdmin(UserAdmin):

    model = CustomUser
    list_display = ("username","is_staff","is_active")
    fieldsets= UserAdmin.fieldsets + (
        ("Aditional Information", {"fields":("birthdate",)}),
    )

admin.site.register(CustomUser,CustomUserAdmin)    