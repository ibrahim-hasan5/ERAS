from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register_choice, name='register_choice'),
    path('register/citizen/', views.register_citizen, name='register_citizen'),
    path('register/service-provider/', views.register_service_provider,
         name='register_service_provider'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('profile/setup/', views.citizen_profile_setup, name='citizen_profile_setup'),
]
