from django.db import models
from django.core.mail import send_mail


class Teacher(models.Model):
    CLASS_CHOICES = [
        ('PreKG', 'PreKG'),
        ('LKG', 'LKG'),
        ('UKG', 'UKG'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100, default="teacher123")
    teacher_class = models.CharField(max_length=20, choices=CLASS_CHOICES)

    def __str__(self):
        return self.name


class TeacherApplication(models.Model):
    CLASS_CHOICES = [
        ('PreKG', 'PreKG'),
        ('LKG', 'LKG'),
        ('UKG', 'UKG'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    qualification = models.CharField(max_length=100)
    experience = models.CharField(max_length=50)
    subject = models.CharField(max_length=50)
    address = models.TextField()

    teacher_class = models.CharField(
        max_length=20,
        choices=CLASS_CHOICES,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected'),
        ],
        default='Pending'
    )

    def save(self, *args, **kwargs):
        old_status = None

        if self.pk:
            old = TeacherApplication.objects.get(pk=self.pk)
            old_status = old.status

        super().save(*args, **kwargs)

        if old_status != "Approved" and self.status == "Approved":

            if not self.teacher_class:
                return

            Teacher.objects.update_or_create(
                email=self.email,
                defaults={
                    'name': self.name,
                    'password': 'teacher123',
                    'teacher_class': self.teacher_class
                }
            )

            send_mail(
                "Teacher Job Approved 🎉",
                f"""Dear {self.name},

Greetings from Happy Ending Play School!

We are pleased to inform you that your application for the Teacher position has been approved.

Congratulations! You have been selected as a teacher in our school. 🎉

Assigned Class: {self.teacher_class}

Your login details:
Email: {self.email}
Password: teacher123

Please visit the school for further process, document verification, and discussion.

Warm regards,
Happy Ending Play School
""",
                "happyendingplaysch@gmail.com",
                [self.email],
                fail_silently=False
            )

        elif old_status != "Rejected" and self.status == "Rejected":
            send_mail(
                "Teacher Application Update",
                f"""Dear {self.name},

Greetings from Happy Ending Play School!

Thank you for applying for the Teacher position in our school.

After careful review, we regret to inform you that we are unable to proceed with your application at this time.

Please do not feel discouraged. We truly appreciate your interest in joining our team, and we encourage you to apply again in the future.

Warm regards,
Happy Ending Play School
""",
                "happyendingplaysch@gmail.com",
                [self.email],
                fail_silently=False
            )

    def __str__(self):
        return self.name