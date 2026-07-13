from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import Admission, Attendance, Marks, Homework, Announcement, ParentQuery, Timetable


# ✅ Admission Admin
class AdmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'student_class', 'phone', 'status')
    list_filter = ('student_class', 'status')
    search_fields = ('name', 'phone', 'email')

    def save_model(self, request, obj, form, change):
        if obj.password and not obj.password.startswith('pbkdf2'):
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)

admin.site.register(Admission, AdmissionAdmin)


# ✅ Attendance Admin
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'get_class', 'date', 'status')
    list_filter = ('student__student_class', 'status', 'date')
    search_fields = ('student__name',)

    def get_class(self, obj):
        return obj.student.student_class

    get_class.short_description = 'Class'

admin.site.register(Attendance, AttendanceAdmin)


# ✅ Marks Admin
class MarksAdmin(admin.ModelAdmin):
    list_display = ('student', 'get_class', 'learning', 'grade')
    list_filter = ('student__student_class', 'grade', 'learning')
    search_fields = ('student__name',)

    def get_class(self, obj):
        return obj.student.student_class

    get_class.short_description = 'Class'

admin.site.register(Marks, MarksAdmin)


# ✅ Homework Admin
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'student_class', 'date')
    list_filter = ('student_class', 'date')
    search_fields = ('title',)

admin.site.register(Homework, HomeworkAdmin)


# ✅ Announcement
admin.site.register(Announcement)


# ✅ Parent Query
class ParentQueryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'status')
    list_filter = ('status',)
    search_fields = ('name', 'email', 'subject')

admin.site.register(ParentQuery, ParentQueryAdmin)


# ✅ Timetable Admin (🔥 IMPORTANT)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('class_name', 'day', 'time_slot', 'activity')
    list_filter = ('class_name', 'day')
    search_fields = ('activity', 'time_slot')
    ordering = ('class_name', 'day', 'time_slot')

admin.site.register(Timetable, TimetableAdmin)