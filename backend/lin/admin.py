from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Board

# Register your models here.


class BoardInfo(admin.ModelAdmin):
    list_display = ('sign', 'board')


admin.site.register(User, UserAdmin)
admin.site.register(Board, BoardInfo)
