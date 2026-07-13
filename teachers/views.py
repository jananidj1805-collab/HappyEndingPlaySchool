from django.shortcuts import render, redirect, get_object_or_404
from .models import Teacher
from students.models import Admission
from django.db.models import Count

def teacher_dashboard(request):
    teacher_id = request.session.get('teacher_id')

    if not teacher_id:
        return redirect('login')

    teacher = get_object_or_404(Teacher, id=teacher_id)

    students = Admission.objects.filter(
        student_class=teacher.teacher_class,
        status="Approved"
    )

    return render(request, 'teacher_dashboard.html', {
        'teacher': teacher,
        'students': students
    })