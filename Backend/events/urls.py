from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.custom_login_view, name='login'),  # Use custom login view
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('csefest/', views.csefest,name='csefest'),
    path('eeeday/', views.eeeday, name='eeeday'),

    path('', views.index, name='Home'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/register/', views.register_event, name='register_event'),
    
    # path('events/<int:event_id>/cancel/', views.cancel_registration, name='cancel_registration'),
    # path('events/<int:event_id>/regenerate_qr/', views.regenerate_qr_code, name='regenerate_qr'),

    path('create/', views.create_event, name='create_event'),
    # path('admin/approve/', views.approve_event_list, name='approve_event_list'),
    # path('admin/approve/<int:event_id>/', views.approve_event, name='approve_event'),

    path('about/', views.about, name='about'),  # New about page URL
    path('contact/', views.contact, name='contact'),  # New contact page URL
    
    path('debate/', views.debate, name='debate'),
    path('language/',views.language, name='language'),

    path('cse/club', views.cseclub, name='cse_club'),
    path('eee/club', views.eeeclub, name='eee'),
    path('law/club', views.lawclub, name='law'),
    path('business/club', views.businessclub, name='business'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('delete-event/<int:event_id>/', views.delete_event, name='delete_event'),
    
    
]
