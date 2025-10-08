from django.urls import path
from . import views

app_name = 'disasters'

urlpatterns = [
    # Public disaster views
    path('', views.disaster_list, name='disaster_list'),
    path('<int:disaster_id>/', views.disaster_detail, name='disaster_detail'),

    # Disaster management
    path('create/', views.create_disaster, name='create_disaster'),
    path('<int:disaster_id>/edit/', views.edit_disaster, name='edit_disaster'),
    path('<int:disaster_id>/delete/', views.delete_disaster, name='delete_disaster'),
    path('my-disasters/', views.my_disasters, name='my_disasters'),
path('citizen/nearby/', views.citizen_nearby_disasters, name='citizen_nearby_disasters'),

    # Service provider responses
    path('<int:disaster_id>/respond/', views.add_response, name='add_response'),
    path('nearby/', views.nearby_disasters, name='nearby_disasters'),

    # Reporting and moderation
    path('<int:disaster_id>/report/', views.report_disaster, name='report_disaster'),

    # Admin functions
    path('admin/', views.admin_disasters, name='admin_disasters'),
    path('admin/<int:disaster_id>/approve/', views.approve_disaster, name='approve_disaster'),

    # AJAX endpoints
    path('api/areas-by-city/', views.get_areas_by_city, name='get_areas_by_city'),
    path('api/<int:disaster_id>/mark-resolved/', views.mark_resolved, name='mark_resolved'),
    path('api/alerts/', views.user_alerts, name='user_alerts'),
    path('api/alerts/<int:alert_id>/mark-read/', views.mark_alert_read, name='mark_alert_read'),
]