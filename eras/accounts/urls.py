from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register_choice, name='register_choice'),
    path('register/citizen/', views.register_citizen, name='register_citizen'),
    path('register/service-provider/', views.register_service_provider,
         name='register_service_provider'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Citizen Profile URLs
    path('dashboard/citizen/', views.citizen_dashboard, name='citizen_dashboard'),
    path('profile/citizen/setup/', views.citizen_profile_update,
         name='citizen_profile_setup'),
    path('profile/citizen/update/', views.citizen_profile_update,
         name='citizen_profile_update'),


    # Service Provider Profile URLs
    path('profile/service-provider/setup/', views.service_provider_profile_setup,
         name='service_provider_profile_setup'),
    path('dashboard/service-provider/', views.service_provider_dashboard,
         name='service_provider_dashboard'),
    path('profile/service-provider/quick-update/',
         views.quick_update_service_provider, name='quick_update_service_provider'),
    path('settings/service-provider/', views.service_provider_settings,
         name='service_provider_settings'),

    # Public Directory URLs
    path('directory/service-providers/', views.service_provider_directory,
         name='service_provider_directory'),
    path('directory/service-provider/<int:provider_id>/',
         views.service_provider_detail, name='service_provider_detail'),
   
     path('api/blood-requests/', views.get_recent_blood_requests_json, name='blood_requests_api'),

    # NEW: Blood Network URL (Sprint 1)
    path('blood-network/', views.blood_network, name='blood_network'),
]
