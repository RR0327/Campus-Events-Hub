from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import qrcode
from io import BytesIO
from django.core.files import File

# -------------------- Custom User -------------------- #
class CustomUser(AbstractUser):
    USER_ROLES = (
        ('student', 'Student'),
        ('club_admin', 'Club Admin'),
    )
    role = models.CharField(max_length=20, choices=USER_ROLES, default='student')
    is_verified = models.BooleanField(default=False)  # For email verification

    def __str__(self):
        return self.username

# -------------------- Event Model -------------------- #
class Event(models.Model):
    CATEGORY_CHOICES = [
        ('tech', 'Tech'),
        ('culture', 'Culture'),
        ('sports', 'Sports'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255)
    image = models.ImageField(upload_to='event_images/')
    capacity = models.PositiveIntegerField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def is_open(self):
        return self.registrations.count() < self.capacity

    def is_upcoming(self):
        return self.date > timezone.now()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Generate QR code after saving
        if not self.qr_code:
            qr = qrcode.make(f"Event ID: {self.id} | Title: {self.title}")
            buffer = BytesIO()
            qr.save(buffer)
            self.qr_code.save(f'qr_event_{self.id}.png', File(buffer), save=False)
            super().save(*args, **kwargs)

    def __str__(self):
        return self.title

# -------------------- Registration -------------------- #
class Registration(models.Model):
    event = models.ForeignKey(Event, related_name='registrations', on_delete=models.CASCADE)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Send confirmation email
        send_mail(
            subject='Event Registration Confirmed',
            message=f'Thank you {self.student.username} for registering for {self.event.title}.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.student.email],
            fail_silently=True
        )

    def __str__(self):
        return f"{self.student.username} -> {self.event.title}"

# -------------------- Cancellation -------------------- #
class Cancellation(models.Model):
    registration = models.OneToOneField(Registration, on_delete=models.CASCADE)
    cancelled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cancelled: {self.registration}"
