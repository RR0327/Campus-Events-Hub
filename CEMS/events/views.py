from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Event, Registration, Cancellation, CustomUser
from .forms import CustomUserCreationForm, EventForm


# -------------------- Signup View -------------------- #
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'events/signup.html', {'form': form})

# -------------------- Dashboard View -------------------- #
@login_required
def dashboard_view(request):
    user = request.user
    if user.role == 'club_admin':
        events = Event.objects.filter(created_by=user)
        return render(request, 'events/club_dashboard.html', {'events': events})
    else:
        registrations = Registration.objects.filter(student=user)
        return render(request, 'events/student_dashboard.html', {'registrations': registrations})

# -------------------- Event List -------------------- #
def event_list(request):
    search_query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    events = Event.objects.filter(approved=True, date__gte=timezone.now())
    if search_query:
        events = events.filter(title__icontains=search_query)
    if category_filter:
        events = events.filter(category=category_filter)
    return render(request, 'events/event_list.html', {'events': events})

# -------------------- Event Detail & Registration -------------------- #
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    already_registered = Registration.objects.filter(event=event, student=request.user).exists()
    return render(request, 'events/event_detail.html', {'event': event, 'already_registered': already_registered})

@login_required
def register_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if event.is_open() and not Registration.objects.filter(event=event, student=request.user).exists():
        Registration.objects.create(event=event, student=request.user)
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
