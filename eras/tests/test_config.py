"""
Test configuration for ERAS project.
Contains test data and configuration settings.
"""

# Test user credentials
TEST_USERS = {
    'citizen': {
        'username': 'testuser123',
        'email': 'test@test.com',
        'password': 'test123456',
        'phone': '01716572906',
        'address': '12/A, Dhanmondi Lake',
        'city': 'Dhaka'
    },
    'provider': {
        'username': 'dhanmondi_hospital',
        'email': 'hospital@test.com',
        'password': 'hospital123456',
        'organization_name': 'Dhanmondi General Hospital',
        'contact_number': '+8801757555290',
        'registration_number': '126485',
        'area_sector': 'Dhanmondi',
        'city': 'Dhaka',
        'street_address': '129/C, Dhanmondi'
    },
    'existing_citizen': {
        'username': 'mou123',
        'password': 'israt123456'
    }
}

# Test data for forms
TEST_DATA = {
    'blood_request': {
        'bags_needed': '2',
        'patient_name': 'Test Patient',
        'blood_type_needed': 'O+',
        'needed_by_date': '2025-10-26'
    },
    'disaster_alert': {
        'disaster_type': 'Fire (Wildfire)',
        'severity': 'High',
        'city': 'Dhaka',
        'area_sector': 'Test Area',
        'description': 'Test disaster alert'
    },
    'profile_update': {
        'phone_number': '01716572906',
        'house_road_no': '12/A, Dhanmondi Lake',
        'city': 'Dhaka',
        'emergency_contact_name': 'Test Contact',
        'emergency_contact_phone': '01757555290',
        'emergency_contact_relationship': 'Parent'
    }
}

# Test URLs
TEST_URLS = {
    'base_url': 'http://127.0.0.1:8000/',
    'login_url': '/accounts/login/',
    'register_url': '/accounts/register/',
    'dashboard_url': '/accounts/dashboard/',
    'blood_network_url': '/accounts/blood-network/',
    'alerts_url': '/disasters/alerts/',
    'services_url': '/accounts/services/'
}

# Browser configuration
BROWSER_CONFIG = {
    'headless': False,  # Set to True for headless testing
    'window_size': (1552, 880),
    'implicit_wait': 10,
    'page_load_timeout': 30
}

# Test timeouts
TIMEOUTS = {
    'element_wait': 10,
    'page_load': 30,
    'implicit': 10
}
