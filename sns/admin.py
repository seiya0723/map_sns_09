from django.contrib import admin

from .models import Category,Park,Tag


admin.site.register(Category)
admin.site.register(Park)
admin.site.register(Tag)