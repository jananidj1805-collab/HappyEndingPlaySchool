from django.contrib import admin
from .models import Teacher, TeacherApplication


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'teacher_class')
    list_filter = ('teacher_class',)
    search_fields = ('name', 'email')
    ordering = ('teacher_class', 'name')


admin.site.register(Teacher, TeacherAdmin)


class TeacherApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'qualification', 'experience', 'subject', 'status')
    list_filter = ('status', 'experience')
    search_fields = ('name', 'email', 'phone', 'qualification', 'subject')
    ordering = ('status', 'name')


admin.site.register(TeacherApplication, TeacherApplicationAdmin)