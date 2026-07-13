from django.urls import path
from . import views

urlpatterns = [
    path('', views.admission_form, name='home'),
    path('success/', views.success, name='success'),
    path('about/', views.about, name='about'), 
     # ✅ LOGIN
    path('login/', views.login_view, name='login'),

    # ✅ DASHBOARD
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('add-attendance/', views.add_attendance, name='add_attendance'),
    path('add-marks/<int:student_id>/', views.add_marks, name='add_marks'),
    path('marks-students/', views.marks_students_list, name='marks_students'),
    path('add-homework/', views.add_homework, name='add_homework'),
    path('attendance/', views.attendance_view, name='attendance'),
    path('marks/', views.marks_view, name='marks'),
    path('homework/', views.homework_view, name='homework'),
    path('careers/', views.teacher_application, name='careers'),
    path('teacher-success/', views.teacher_success, name='teacher_success'),
    path('marks-list/', views.marks_students_list, name='marks_students_list'),
    path('timetable/', views.timetable_view, name='timetable'),
    path('parent-query/', views.parent_query, name='parent_query'),
    path('manage-timetable/', views.manage_timetable, name='manage_timetable'),
    path('timetable/', views.timetable_view, name='timetable'),
    path('teacher-timetable/', views.teacher_timetable_view, name='teacher_timetable'),
]