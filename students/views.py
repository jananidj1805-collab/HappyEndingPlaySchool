from django.shortcuts import render, redirect
from .models import Admission, Attendance, Marks, Homework, ParentQuery, Timetable
from django.contrib import messages
from teachers.models import Teacher, TeacherApplication
from datetime import date, datetime
from django.contrib.auth.hashers import make_password, check_password


# ------------------ FORM ------------------
def admission_form(request):
    if request.method == "POST":
        name = request.POST.get('name')
        dob = request.POST.get('dob')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        email = request.POST.get('email')
        password = make_password(request.POST.get('password'))
        address = request.POST.get('address')
        religion = request.POST.get('religion')
        student_class = request.POST.get('student_class')

        dob = date.fromisoformat(dob)

        Admission.objects.create(
            name=name,
            dob=dob,
            phone=phone,
            gender=gender,
            email=email,
            password=password,
            address=address,
            religion=religion,
            student_class=student_class
        )

        messages.success(
            request,
            "Your admission form has been submitted successfully. Please wait 1 or 2 days. You will receive an email about your admission approval status. Kindly check your email."
        )
        return redirect('/')

    return render(request, 'index.html')


# ------------------ STATIC ------------------
def success(request):
    return render(request, 'success.html')


def about(request):
    return render(request, 'ab.html')


# ------------------ LOGIN ------------------
def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        role = request.POST.get('role')

        if role == "student":
            user = Admission.objects.filter(email=email).first()

            if not user:
                return render(request, 'login.html', {'error': 'Student not found ❌'})

            if not check_password(password, user.password):
                return render(request, 'login.html', {'error': 'Wrong password ❌'})

            if user.status != "Approved":
                return render(request, 'login.html', {'error': 'Wait for Admin Approval ❌'})

            request.session['student_id'] = user.id
            return redirect('student_dashboard')

        elif role == "teacher":
            teacher = Teacher.objects.filter(email=email, password=password).first()

            if not teacher:
                return render(request, 'login.html', {'error': 'Invalid Teacher Login ❌'})

            request.session['teacher_id'] = teacher.id
            return redirect('teacher_dashboard')

        else:
            return render(request, 'login.html', {'error': 'Select role ❌'})

    return render(request, 'login.html')


# ------------------ STUDENT DASHBOARD ------------------
def student_dashboard(request):
    student_id = request.session.get('student_id')

    if not student_id:
        return redirect('login')

    student = Admission.objects.get(id=student_id)

    attendance = Attendance.objects.filter(student=student)
    marks = Marks.objects.filter(student=student)
    homework = Homework.objects.filter(student_class=student.student_class)

    today = date.today()
    age = today.year - student.dob.year - (
        (today.month, today.day) < (student.dob.month, student.dob.day)
    )

    total_days = attendance.count()
    present_days = attendance.filter(status="Present").count()
    absent_days = attendance.filter(status="Absent").count()
    attendance_percentage = (present_days / total_days) * 100 if total_days > 0 else 0

    return render(request, 'student_dashboard.html', {
        'student': student,
        'attendance': attendance,
        'marks': marks,
        'homework': homework,
        'age': age,
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'attendance_percentage': round(attendance_percentage, 2)
    })


# ------------------ TEACHER DASHBOARD ------------------
def teacher_dashboard(request):
    teacher_id = request.session.get('teacher_id')

    if not teacher_id:
        return redirect('login')

    teacher = Teacher.objects.get(id=teacher_id)

    students = Admission.objects.filter(
        student_class=teacher.teacher_class
    ).order_by('name')   # ✅ Alphabet order

    for student in students:
        if student.status:
            student.status = student.status.strip()

    return render(request, 'teacher_dashboard.html', {
        'teachers': teacher,
        'students': students
    })


# ------------------ ATTENDANCE ------------------
def add_attendance(request):
    teacher_id = request.session.get('teacher_id')

    if not teacher_id:
        return redirect('login')

    teacher = Teacher.objects.get(id=teacher_id)

    students = Admission.objects.filter(
        status="Approved",
        student_class=teacher.teacher_class
    ).order_by('name')   # ✅ Alphabet order

    if request.method == "POST":
        attendance_date = request.POST.get('date')

        if not attendance_date:
            messages.error(request, "❌ Please select date")
            return redirect('add_attendance')

        attendance_date = datetime.strptime(attendance_date, "%Y-%m-%d").date()

        for student in students:
            status = request.POST.get(f"status_{student.id}") or "Absent"

            Attendance.objects.create(
                student=student,
                date=attendance_date,
                status=status
            )

        messages.success(request, "✅ Attendance saved successfully!")
        return redirect('add_attendance')

    return render(request, 'add_attendance.html', {'students': students})


# ------------------ MARKS ------------------
def add_marks(request, student_id):
    student = Admission.objects.get(id=student_id)

    learning_areas = ["Spelling", "Reading", "Counting", "Drawing", "Playing", "Talking"]

    if request.method == "POST":
        for area in learning_areas:
            grade = request.POST.get(f"grade_{area.lower()}")
            comment = request.POST.get(f"comment_{area.lower()}")

            Marks.objects.update_or_create(
                student=student,
                learning=area,
                defaults={
                    'grade': grade,
                    'comments': comment
                }
            )

        messages.success(request, "✅ Marks saved successfully!")

    return render(request, 'add_mark.html', {
        'student': student,
        'learning_areas': learning_areas
    })


# ------------------ HOMEWORK ------------------
def add_homework(request):
    teacher_id = request.session.get('teacher_id')

    if not teacher_id:
        return redirect('login')

    teacher = Teacher.objects.get(id=teacher_id)

    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        hw_date = request.POST.get('date')

        Homework.objects.create(
            title=title,
            description=description,
            date=hw_date,
            student_class=teacher.teacher_class
        )

        messages.success(request, "✅ Homework added successfully!")
        return redirect('add_homework')

    return render(request, 'add_homework.html')


# ------------------ MARK STUDENT LIST ------------------
def marks_students_list(request):
    teacher_id = request.session.get('teacher_id')

    if not teacher_id:
        return redirect('login')

    teacher = Teacher.objects.get(id=teacher_id)

    students = Admission.objects.filter(
        status="Approved",
        student_class=teacher.teacher_class
    ).order_by('name')   # ✅ Alphabet order

    return render(request, 'students_mark_list.html', {
        'students': students
    })


# ------------------ STUDENT ATTENDANCE VIEW ------------------
def attendance_view(request):
    student_id = request.session.get('student_id')
    attendance = Attendance.objects.filter(student_id=student_id)
    return render(request, 'attendance.html', {'attendance': attendance})


# ------------------ STUDENT MARKS VIEW ------------------
def marks_view(request):
    student_id = request.session.get('student_id')
    marks = Marks.objects.filter(student_id=student_id)
    return render(request, 'marks.html', {'marks': marks})


# ------------------ STUDENT HOMEWORK VIEW ------------------
def homework_view(request):
    student_id = request.session.get('student_id')
    student = Admission.objects.get(id=student_id)

    homework = Homework.objects.filter(student_class=student.student_class)

    return render(request, 'homework.html', {'homework': homework})


# ------------------ TEACHER APPLICATION ------------------
def teacher_application(request):
    if request.method == "POST":
        TeacherApplication.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            qualification=request.POST.get('qualification'),
            experience=request.POST.get('experience'),
            subject=request.POST.get('subject'),
            address=request.POST.get('address'),
        )
        messages.success(
            request,
            "Your application has been submitted successfully. Please wait for the approval mail."
        )

    return render(request, 'careers.html')


def teacher_success(request):
    return render(request, 'teacher_success.html')


# ------------------ TIMETABLE ------------------
def timetable_view(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('login')

    student = Admission.objects.get(id=student_id)

    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    time_slots = ['8.45am-9.00am','9.00am-9.30am','9.30am-10.00am','10.00am-10.30am','10.30am-11.00am','11.00am-11.30am','11.30am-12.00am']

    timetable_data = {}
    for day in days:
        timetable_data[day] = {}
        for slot in time_slots:
            entry = Timetable.objects.filter(
                class_name=student.student_class,
                day=day,
                time_slot=slot
            ).first()
            timetable_data[day][slot] = entry.activity if entry else "-"

    return render(request, 'student_timetable.html', {
        'student': student,
        'days': days,
        'time_slots': time_slots,
        'timetable_data': timetable_data,
    })


def teacher_timetable_view(request):
    teacher_id = request.session.get('teacher_id')
    if not teacher_id:
        return redirect('login')

    teacher = Teacher.objects.get(id=teacher_id)

    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    time_slots = ['8.45am-9.00am','9.00am-9.30am','9.30am-10.00am','10.00am-10.30am','10.30am-11.00am','11.00am-11.30am','11.30am-12.00am']

    timetable_data = {}
    for day in days:
        timetable_data[day] = {}
        for slot in time_slots:
            entry = Timetable.objects.filter(
                class_name=teacher.teacher_class,
                day=day,
                time_slot=slot
            ).first()
            timetable_data[day][slot] = entry.activity if entry else "-"

    return render(request, 'teacher_timetable.html', {
        'teacher': teacher,
        'days': days,
        'time_slots': time_slots,
        'timetable_data': timetable_data,
    })
# ------------------ PARENT QUERY ------------------
def parent_query(request):
    if request.method == "POST":
        ParentQuery.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            subject=request.POST.get('subject'),
            message=request.POST.get('message'),
        )
        messages.success(
            request,
            "Your query has been submitted successfully. Our school administration will respond soon."
        )
        return render(request, 'parent_query.html')

    return render(request, 'parent_query.html')



def manage_timetable(request):
    teacher_id = request.session.get('teacher_id')
    if not teacher_id:
        return redirect('login')

    teacher = Teacher.objects.get(id=teacher_id)
    class_name = teacher.teacher_class

    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    time_slots = ['9.30-10', '10-10.30', '10.30-11', '11-11.30', '11.30-12']

    if request.method == "POST":
        for day in days:
            for slot in time_slots:
                field_name = f"{day}_{slot}".replace('.', '').replace('-', '_')
                activity = request.POST.get(field_name, '').strip()

                Timetable.objects.update_or_create(
                    class_name=class_name,
                    day=day,
                    time_slot=slot,
                    defaults={'activity': activity}
                )

        messages.success(request, "Timetable saved successfully!")
        return redirect('manage_timetable')

    timetable_data = {}
    for day in days:
        timetable_data[day] = {}
        for slot in time_slots:
            entry = Timetable.objects.filter(
                class_name=class_name,
                day=day,
                time_slot=slot
            ).first()
            timetable_data[day][slot] = entry.activity if entry else ""

    return render(request, 'manage_timetable.html', {
        'teacher': teacher,
        'class_name': class_name,
        'days': days,
        'time_slots': time_slots,
        'timetable_data': timetable_data,
    })
