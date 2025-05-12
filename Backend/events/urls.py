from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='events/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    path('', views.event_list, name='event_list'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/register/', views.register_event, name='register_event'),
    path('events/<int:event_id>/cancel/', views.cancel_registration, name='cancel_registration'),
    path('events/<int:event_id>/regenerate_qr/', views.regenerate_qr_code, name='regenerate_qr'),

    path('create/', views.create_event, name='create_event'),
    path('admin/approve/', views.approve_event_list, name='approve_event_list'),
    path('admin/approve/<int:event_id>/', views.approve_event, name='approve_event'),
]
