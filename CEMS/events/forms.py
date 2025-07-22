from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Event

# class CustomUserCreationForm(UserCreationForm):
#     class Meta:
#         model = CustomUser
#         fields = ['full_name', 'email', 'role', 'password1', 'password2']
#     studentid = forms.CharField(required=True)
#     department = forms.CharField(required=True)

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'studentid', 'department', 'role', 'password1', 'password2', 'additional_email', 'mobile_number']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.full_name = self.cleaned_data['full_name']
        user.email = self.cleaned_data['email']
        user.studentid = self.cleaned_data['studentid']
        user.department = self.cleaned_data['department']
        user.role = self.cleaned_data['role']
        user.additional_email = self.cleaned_data['additional_email']
        user.mobile_number = self.cleaned_data['mobile_number']

        if commit:
            user.save()
        return user


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'location', 'image', 'capacity', 'category']
        

from django.utils import timezone
class EventSearchForm(forms.Form):
    title = forms.CharField(required=False, label='Event Title', max_length=100)
    category = forms.ChoiceField(choices=Event.CATEGORY_CHOICES, required=False)
    is_upcoming = forms.BooleanField(required=False, label='Upcoming Events', initial=True)
    is_past = forms.BooleanField(required=False, label='Past Events', initial=False)
    
    def filter_events(self):
        """Filter events based on form data."""
        events = Event.objects.all()

        # Title search
        if self.cleaned_data['title']:
            events = events.filter(title__icontains=self.cleaned_data['title'])
        
        # Category filter
        if self.cleaned_data['category']:
            events = events.filter(category=self.cleaned_data['category'])
        
        # Upcoming or past filter
        if self.cleaned_data['is_upcoming']:
            events = events.filter(date__gte=timezone.now())  # Future events
        
        if self.cleaned_data['is_upcoming'] and self.cleaned_data['is_past']:
        # If both Upcoming and Past are selected, show all events
            return events
        
        if self.cleaned_data['is_past']:
            events = events.filter(date__lt=timezone.now())  # Past events

        return events