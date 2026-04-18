from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from . import views, api_views

router = DefaultRouter()
router.register(r'api/blood-requests', api_views.BloodRequestViewSet, basename='api_blood_requests')

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

    # REST API URLs
    path('api/login/', api_views.api_login, name='api_login'),
    path('api/register/', api_views.api_register, name='api_register'),
    path('api/profile/', api_views.api_get_profile, name='api_get_profile'),
    path('api/profile/update/', api_views.api_update_profile, name='api_update_profile'),
    path('api/dashboard/', api_views.api_dashboard, name='api_dashboard'),
    path('', include(router.urls)),
]
