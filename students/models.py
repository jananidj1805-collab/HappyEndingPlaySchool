from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password


class Admission(models.Model):
    name = models.CharField(max_length=100)
    dob = models.DateField()
    phone = models.CharField(max_length=10)
    gender = models.CharField(max_length=10)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    address = models.TextField()
    religion = models.CharField(max_length=50)

    student_class = models.CharField(
        max_length=20,
        choices=[
            ('PreKG', 'PreKG'),
            ('LKG', 'LKG'),
            ('UKG', 'UKG')
        ]
    )

    status = models.CharField(
        max_length=10,
        choices=[
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected'),
        ],
        default='Pending'
    )

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)

        if self.pk:
            old = Admission.objects.get(pk=self.pk)

            if old.status != "Approved" and self.status == "Approved":
                send_mail(
                    "Admission Approved 🎉",
                    f"""Dear {self.name},

Greetings from Happy Ending Play School!

We are delighted to inform you that your admission has been successfully approved. 🎉

Welcome to our school family! We are excited to be a part of your child's learning journey filled with fun, growth, and happiness.

We kindly request you to visit the school for further formalities and interaction with our team.

If you have any questions, feel free to contact us anytime.

We look forward to seeing you soon!

Warm regards,
Happy Ending Play School
""",
                    "happyendingplaysch@gmail.com",
                    [self.email],
                    fail_silently=False
                )

            elif old.status != "Rejected" and self.status == "Rejected":
                send_mail(
                    "Admission Application Update",
                    f"""Dear {self.name},

Greetings from Happy Ending Play School!

Thank you for your interest in our school and for submitting your admission application.

After careful review, we regret to inform you that we are unable to proceed with the admission at this time.

Please do not feel discouraged. We encourage you to apply again in the future.

We sincerely appreciate your interest in Happy Ending Play School and wish you all the very best.

Warm regards,
Happy Ending Play School
""",
                    "happyendingplaysch@gmail.com",
                    [self.email],
                    fail_silently=False
                )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.student_class})"


class Attendance(models.Model):
    student = models.ForeignKey(Admission, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"


class Marks(models.Model):
    student = models.ForeignKey(Admission, on_delete=models.CASCADE)
    learning = models.CharField(max_length=100)
    grade = models.CharField(max_length=10)
    comments = models.TextField()

    def __str__(self):
        return f"{self.student.name} - {self.learning} - {self.grade}"


class Homework(models.Model):
    CLASS_CHOICES = [
        ('PreKG', 'PreKG'),
        ('LKG', 'LKG'),
        ('UKG', 'UKG')
    ]

    student_class = models.CharField(max_length=20, choices=CLASS_CHOICES)
    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()

    def __str__(self):
        return self.title


class Announcement(models.Model):
    SEND_TO_CHOICES = [
        ('Students', 'Students'),
        ('Teachers', 'Teachers'),
        ('Both', 'Both'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    send_to = models.CharField(
        max_length=20,
        choices=SEND_TO_CHOICES,
        default='Both'
    )
    date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        from teachers.models import Teacher

        all_emails = []

        if self.send_to == "Students":
            all_emails = list(
                Admission.objects.filter(status="Approved")
                .values_list('email', flat=True)
            )

        elif self.send_to == "Teachers":
            all_emails = list(
                Teacher.objects.all()
                .values_list('email', flat=True)
            )

        elif self.send_to == "Both":
            student_emails = list(
                Admission.objects.filter(status="Approved")
                .values_list('email', flat=True)
            )
            teacher_emails = list(
                Teacher.objects.all()
                .values_list('email', flat=True)
            )
            all_emails = student_emails + teacher_emails

        all_emails = list(set([email for email in all_emails if email]))

        if all_emails:
            print("MAIL SENDING TO:", all_emails)

            send_mail(
                self.title,
                f"""{self.message}

If you have any questions or need further clarification, please contact our school administration at happyendingplaysch@gmail.com.
We will be happy to assist you.

Regards,
Happy Ending Play School
""",
                "happyendingplaysch@gmail.com",
                all_emails,
                fail_silently=False
            )

    def __str__(self):
        return self.title


class ParentQuery(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    reply = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Replied', 'Replied'),
        ],
        default='Pending'
    )

    def save(self, *args, **kwargs):
        old_reply = None

        if self.pk:
            old = ParentQuery.objects.get(pk=self.pk)
            old_reply = old.reply

        super().save(*args, **kwargs)

        if self.reply and self.reply != old_reply:
            send_mail(
                f"Reply to your query: {self.subject}",
                f"""Dear {self.name},

Thank you for contacting Happy Ending Play School.

Here is our response to your query:

{self.reply}

If you have any further questions, please feel free to contact us again.

Regards,
Happy Ending Play School
""",
                "happyendingplaysch@gmail.com",
                [self.email],
                fail_silently=False
            )

            if self.status != "Replied":
                self.status = "Replied"
                super().save(update_fields=["status"])

    def __str__(self):
        return self.name


class Timetable(models.Model):
    CLASS_CHOICES = [
        ('PreKG', 'PreKG'),
        ('LKG', 'LKG'),
        ('UKG', 'UKG'),
    ]

    DAY_CHOICES = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
    ]

    class_name = models.CharField(max_length=20, choices=CLASS_CHOICES)
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    time_slot = models.CharField(max_length=20)
    activity = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.class_name} - {self.day} - {self.time_slot}"