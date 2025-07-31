from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Event, Registration, Cancellation, CustomUser
from .forms import CustomUserCreationForm, EventForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings


def index(request):
    # Get the next upcoming event (closest future date)
    upcoming_event = Event.objects.filter(date__gte=timezone.now()).order_by('date').first()
   

    
    context = {
        'upcoming_event': upcoming_event if upcoming_event else None,
    }
    return render(request, 'index.html', context)

def csefest(request):
    return render(request, 'csefest.html')

def eeeday(request):
    return render(request, 'eeeday.html')

def debate(request):
    return render(request,'debate.html')

def language(request):
    return render(request, 'language.html')

# -------------------- Signup View -------------------- #
# def signup_view(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('dashboard')
#     else:
#         form = CustomUserCreationForm()
#     return render(request, 'signup.html', {'form': form})

# Signup view
import random
def generate_otp():
    return str(random.randint(100000, 999999))

def signup_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        studentid = request.POST.get('studentid')
        department = request.POST.get('department')
        role = request.POST.get('role')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('signup')

        user = CustomUser.objects.create_user(
            email=email,
            full_name=full_name,
            studentid=studentid,
            department=department,
            role=role,
            password=password1  # No need for 'username' field here
        )
        
        otp = generate_otp()
        user.otp_code = otp
        user.otp_created_at = timezone.now()
        user.is_verified = False
        user.save()
        
        send_mail(
            subject="Welcome to Campus Event Hub!",
            message=f"Hi {full_name},\n\nYour OTP for email verification is: {otp}\n(Valid for 5 minutes)",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False
        )
        
        login(request, user)
        
        
        # Send welcome email
        
        messages.success(request, "Please enter your OTP that have been provided in your email")
        return redirect('verify_otp')


    return render(request, 'signup.html')


from datetime import timedelta


@login_required
def verify_otp_view(request):
    user = request.user  # Get the logged-in user

    # If the user is already verified, redirect to the dashboard
    if user.is_verified:
        messages.info(request, "Your email is already verified.")
        return redirect('dashboard')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')

        # Check if OTP exists
        if not user.otp_code:
            messages.error(request, "No OTP found. Please request a new one.")
            return redirect('verify_otp')

        # Check OTP expiration (5 minutes)
        expiry_time = user.otp_created_at + timedelta(minutes=5)
        if timezone.now() > expiry_time:
            user.otp_code = None  # Invalidate expired OTP
            user.save()
            # send_mail(
            #     subject="Welcome to Campus Event Hub!",
            #     message=f"Hi {user.full_name},\n\nWelcome to Campus Event Hub! We're excited to have you onboard. Now that your email is verified, you can start exploring all the events and activities we offer.\n\nFor further assistance, reach out to us at franklin.gta.vmi@gmail.com \n\nBest regards,\nTeam EventEase",
            #     from_email=settings.DEFAULT_FROM_EMAIL,
            #     recipient_list=[user.email],
            #     fail_silently=False
            # )
            messages.error(request, "Your OTP has expired. Please request a new one.")
            return redirect('verify_otp')

        # Check if entered OTP matches
        if entered_otp == user.otp_code:
            user.is_verified = True
            user.otp_code = None  # Clear OTP after successful verification
            user.save()
            send_mail(
                subject="Welcome to Campus Event Hub!",
                message=f"Hi {user.full_name},\n\nWelcome to Campus Event Hub! We're excited to have you onboard. Now that your email is verified, you can start exploring all the events and activities we offer.\n\nFor further assistance, reach out to us at franklin.gta.vmi@gmail.com \n\nBest regards,\nTeam EventEase",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )
            messages.success(request, "Your email has been verified successfully!")
            return redirect('dashboard')  # Redirect to dashboard after successful verification
        else:
            messages.error(request, "Incorrect OTP. Please try again.")
            return redirect('verify_otp')  # Redirect back to OTP verification page if OTP is wrong

    return render(request, 'verify_otp.html')  # Show OTP form if GET request

@login_required
def resend_otp(request):
    user = request.user
    now = timezone.now()

    if user.otp_created_at and (now - user.otp_created_at).seconds < 120:
        wait_time = 120 - (now - user.otp_created_at).seconds
        messages.warning(request, f"Please wait {wait_time} seconds before resending OTP.")
    else:
        new_otp = generate_otp()
        user.otp_code = new_otp
        user.otp_created_at = timezone.now()
        user.save()

        send_mail(
            subject="Resent OTP - Campus Event Hub",
            message=f"Your new OTP is: {new_otp}\n(Valid for 5 minutes)",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
        messages.success(request, "OTP resent successfully!")

    return redirect('verify_otp')

# Custom login view

def custom_login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')  # Email field used as username
        password = request.POST.get('password')

        # Authenticate the user using email (we're using email as the USERNAME_FIELD)
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            # Check if the user is verified
            if not user.is_verified:
                messages.error(request, "Your email is not verified. Please verify your email first.")
                return redirect('verify_otp')  # Redirect to OTP verification page
                
            login(request, user)  # Log in if verified
            return redirect('dashboard')  # Redirect to the dashboard for verified users

        else:
            messages.error(request, "Invalid login credentials")
            return redirect('login')

    return render(request, 'login.html')

# -------------------- Dashboard View -------------------- #
@login_required
def dashboard_view(request):
    user = request.user  # Get the logged-in user

    # Handle profile update if the form is submitted via POST
    if request.method == 'POST':
        # user.full_name = request.POST.get('full_name', user.full_name)
        # user.email = request.POST.get('email', user.email)
        user.additional_email = request.POST.get('additional_email', user.additional_email)
        # user.department = request.POST.get('department', user.department)
        user.mobile_number = request.POST.get('mobile_number', user.mobile_number)
        
        user.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('dashboard')  # Reload the dashboard after the update

    # Fetch events the user has registered for
    registrations = Registration.objects.filter(student=user)
    events_attended = registrations.count()  # Number of events attended

    # Example achievements (modify if you have an achievements model)
    achievements = []  # Fetch achievements if you have any achievements model

    # Example clubs (fetch the clubs the user is a part of)
    clubs = []  # Fetch clubs if you have a clubs model
    events = Event.objects.filter(approved=True).order_by('date')

    return render(request, 'student_dashboard.html', {
        'user': user,
        'registrations': registrations,
        'events_attended': events_attended,
        'achievements': achievements,
        'clubs': clubs,
        'events': events,
    })


# -------------------- Event List -------------------- #
from .models import Event
from .forms import EventSearchForm
def event_list(request):
    search_query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    events = Event.objects.filter(approved=True, date__gte=timezone.now())
    if search_query:
        events = events.filter(title__icontains=search_query)
    if category_filter:
        events = events.filter(category=category_filter)
        
    form = EventSearchForm(request.GET)  # Use GET method to handle search/filter parameters

    if form.is_valid():
        events = form.filter_events()
    else:
        events = Event.objects.all()  # Show all events if the form is not submitted or invalid
    return render(request, 'events/event_list.html', {'events': events, 'form': form})

# -------------------- Event Detail & Registration -------------------- #
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    # already_registered = Registration.objects.filter(event=event, student=request.user).exists()
    # Django template language doesn’t support calling methods like .exists() directly inside {% if %} blocks.
    
    already_registered = False
    reg = None

    if request.user.is_authenticated:
        try:
            reg = Registration.objects.get(event=event, student=request.user)
            already_registered = True
        except Registration.DoesNotExist:
            pass
    event_status = "Open" if event.is_open() else "Closed"
    
    return render(request, 'events/event_detail.html', {'event': event, 'already_registered': already_registered, 'reg': reg,'event_status': event_status})

from django.core.exceptions import ObjectDoesNotExist
@login_required
def register_event(request, event_id):
    try:
        event = get_object_or_404(Event, id=event_id)
    except ObjectDoesNotExist:
        messages.error(request, "Event does not exist.")
        return redirect('event_list')
    
    if event.is_past():
        messages.error(request, "Registration is closed for this event as it has already passed.")
        return redirect('event_list')  # Redirect to the event list if the event is in the past

    
    if Registration.objects.filter(event=event, student=request.user).exists():
        messages.warning(request, 'You are already registered for this event.')
    if event.registrations.count() >= event.capacity:
        messages.error(request, 'Sorry, this event is full.')
    
    registration=Registration.objects.create(event=event, student=request.user)
    registration.save()  # Generate QR code and PDF
    messages.success(request, 'Successfully registered for the event.')
    
    
    # if event.is_open() and not Registration.objects.filter(event=event, student=request.user).exists():
    #     Registration.objects.create(event=event, student=request.user)
    return redirect('dashboard')

@login_required
def cancel_registration(request, event_id):
    registration = Registration.objects.filter(event_id=event_id, student=request.user).first()
    if registration:
        Cancellation.objects.create(registration=registration)
        registration.delete()
    return redirect('dashboard')

# -------------------- Event Creation (Admin Only) -------------------- #
@login_required
def create_event(request):
    if request.user.role != 'club_admin':
        return redirect('dashboard')
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            return redirect('dashboard')
    else:
        form = EventForm()
    return render(request, 'events/create_event.html', {'form': form})

# For About file
def about(request):
    return render(request, 'about.html')

    # For Contact file
def contact(request):
    return render(request, 'contact.html')

# For cse club
def cseclub(request):
    return render(request, 'cse_club.html')

# For eee clib
def eeeclub(request):
    return render(request, 'eee.html')

# For law club:
def lawclub(request):
    return render(request, 'law.html')

# For business club
def businessclub(request):
    return render(request, 'business.html')


@login_required
def admin_dashboard_view(request):
    if not (request.user.role == 'admin' or request.user.role == 'club_admin'):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('dashboard')
    
    # Get all events
    all_events = Event.objects.all().order_by('date')
    
    # Get statistics
    total_events = Event.objects.count()
    upcoming_events = Event.objects.filter(date__gte=timezone.now()).count()
    total_registrations = Registration.objects.count()
    
    # Get events happening today
    today = timezone.now().date()
    active_events = Event.objects.filter(
        date__date=today
    ).count()
    
    # Get recent registrations
    recent_registrations = Registration.objects.select_related('event', 'student').order_by('-timestamp')[:10]
    
    # Get all registrations for the registrations tab
    all_registrations = Registration.objects.select_related('event', 'student').order_by('-timestamp')
    
    return render(request, 'admin_dashboard.html', {
        'user': request.user,
        'all_events': all_events,
        'total_events': total_events,
        'upcoming_events': upcoming_events,
        'total_registrations': total_registrations,
        'active_events': active_events,
        'recent_registrations': recent_registrations,
        'all_registrations': all_registrations,
    })


@login_required
def delete_event(request, event_id):
    if not (request.user.role == 'admin' or request.user.role == 'club_admin'):
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('dashboard')
    
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    messages.success(request, "Event deleted successfully.")
    return redirect('admin_dashboard')