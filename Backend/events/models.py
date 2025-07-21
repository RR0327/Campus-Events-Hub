from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import qrcode
from io import BytesIO
from django.core.files import File
from datetime import timedelta


# Role choices for the user
ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('student', 'Student'),
]

class CustomUserManager(BaseUserManager):
    def create_user(self, email, full_name, studentid=None, department=None, role='student', password=None):
        """
        Create and return a regular user with email, full_name, studentid, department, role, and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            full_name=full_name,
            studentid=studentid or '',  # Use empty string if studentid is not provided
            department=department or '',  # Use empty string if department is not provided
            role=role
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None):
        """
        Create and return a superuser with email, full_name, and password.
        """
        # Here, we're only using email, full_name, and password for superuser creation
        user = self.create_user(
            email,
            full_name,
            password=password,
            role='admin',  # Set role to 'admin' for superuser
        )
        user.is_staff = True  # Required for admin access
        user.is_superuser = True  # Grants full permissions
        user.save(using=self._db)
        return user

class CustomUser(AbstractUser):
    username = None  # Removing the default username field
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    studentid = models.CharField(max_length=20, blank=True, null=True)  # Optional field for student ID
    department = models.CharField(max_length=50, blank=True, null=True)  # Optional field for department
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')  # Role can be 'admin' or 'student'
    is_verified = models.BooleanField(default=False)
    additional_email = models.EmailField(null=True, blank=True)  # Added field for additional email
    mobile_number = models.CharField(max_length=15, null=True, blank=True)  # Added field for mobile number
    
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    # Required for Django's authentication system
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']  # Only email and full_name are required for superuser creation

    # Set the custom manager here
    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
    def otp_is_valid(self):
        if self.otp_created_at:
            return timezone.now() < self.otp_created_at + timedelta(minutes=5)
        return False


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
        return self.registrations.count() < self.capacity and self.is_upcoming()

    def is_upcoming(self):
        return self.date > timezone.now()
    
    def is_past(self):
        """Check if the event is in the past."""
        return self.date < timezone.now()
    
    def remaining_seats(self):
        """Return the remaining number of seats for the event."""
        return self.capacity - self.registrations.count()

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


# -------------------- Registration Model -------------------- #
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
# from reportlab.lib.units import inch
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import landscape, A6
from reportlab.graphics.barcode import code128

class Registration(models.Model):
    event = models.ForeignKey('Event', related_name='registrations', on_delete=models.CASCADE)
    student = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    ticket_pdf = models.FileField(upload_to='event_tickets/', null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.generate_qr_code()
        self.create_ticket_pdf()
        self.send_confirmation_email()

    def generate_qr_code(self):
        data = f"{self.event.title} | {self.student.full_name} | {self.student.mobile_number}"
        qr = qrcode.make(data)
        buffer = BytesIO()
        qr.save(buffer)
        buffer.seek(0)
        self.qr_code.save(f'qr_ticket_{self.id}.png', File(buffer), save=False)

    def create_ticket_pdf(self):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=landscape(A6))  # Wider layout

        # === Colors ===
        left_color = HexColor("#5A00F0")
        right_color = HexColor("#3D2C8D")
        text_white = colors.white
        accent = HexColor("#00FFD1")

        # === Sections ===
        width, height = landscape(A6)  # ~ (420, 297)
        left_width = width * 0.65
        right_width = width * 0.35

        # === Left Section ===
        c.setFillColor(left_color)
        c.rect(0, 0, left_width, height, fill=1)

        c.setFillColor(text_white)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(20, height - 40, self.event.title.upper())

        c.setFont("Helvetica", 10)
        c.drawString(20, height - 60, "Campus Event Pass")

        c.setFont("Helvetica", 8)
        c.drawString(20, height - 90, "NAME")
        c.setFont("Helvetica-Bold", 12)
        c.drawString(20, height - 105, self.student.full_name.upper())

        c.setFont("Helvetica", 8)
        c.drawString(20, height - 125, "CODE")
        code = f"REG{self.id:04d}"
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(accent)
        c.drawString(20, height - 140, code)

        # Barcode (simulated with lines)
        # c.setFillColor(text_white)
        # for i in range(20):
        #     x = 20 + i * 5
        #     height_offset = 20 + (i % 2) * 5
        #     c.rect(x, height_offset, 2, 30, fill=1, stroke=0)

        # === Right Section ===
        c.setFillColor(right_color)
        c.rect(left_width, 0, right_width, height, fill=1)

        # QR code
        if self.qr_code:
            c.drawImage(self.qr_code.path, left_width + 10, height - 110, width=60, height=60)

        # Vertical Text
        c.setFont("Helvetica", 7)
        c.setFillColor(text_white)
        c.saveState()
        c.translate(left_width + 90, height / 2)
        c.rotate(90)
        c.drawCentredString(0, 0, f"{self.student.full_name} | {code}")
        c.restoreState()

        # Time & Seat Details
        c.setFont("Helvetica", 6)
        c.drawString(left_width + 10, 20, f"Date: {self.event.date.strftime('%Y-%m-%d')}")
        c.drawString(left_width + 10, 10, f"Time: {self.event.date.strftime('%H:%M')}")

        c.save()
        buffer.seek(0)
        self.ticket_pdf.save(f"ticket_{self.id}.pdf", File(buffer), save=False)

    def send_confirmation_email(self):
        send_mail(
            subject="🎟 Your Event Ticket is Ready",
            message=f"Hello {self.student.full_name},\n\nYou're registered for: {self.event.title}.\nYour digital ticket has been generated.\n\nThanks,\nCampus Event Hub",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.student.email],
            fail_silently=True,
        )

    def __str__(self):
        return f"{self.student.email} → {self.event.title}"
    
# -------------------- Cancellation Model -------------------- #
class Cancellation(models.Model):
    registration = models.OneToOneField(Registration, on_delete=models.CASCADE)
    cancelled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cancelled: {self.registration}"
# Ensure that the Cancellation model is linked to a Registration
# and that it captures the cancellation time.