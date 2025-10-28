from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from accounts.models import (
    User, CitizenProfile, ServiceProviderProfile, 
    ServiceProviderRating, BloodRequest
)
from accounts.forms import (
    CitizenRegistrationForm, CitizenProfileForm,
    ServiceProviderRegistrationForm, ServiceProviderProfileForm,
    QuickUpdateForm, ServiceProviderRatingForm
)

User = get_user_model()


class UserModelTests(TestCase):
    """Test User model"""
    
    def test_create_citizen_user(self):
        """Test creating a citizen user"""
        user = User.objects.create_user(
            username='testcitizen',
            email='citizen@test.com',
            password='testpass123',
            phone_number='+8801712345678',
            user_type='citizen'
        )
        self.assertEqual(user.username, 'testcitizen')
        self.assertEqual(user.user_type, 'citizen')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_create_service_provider_user(self):
        """Test creating a service provider user"""
        user = User.objects.create_user(
            username='test_hospital',
            email='hospital@test.com',
            password='testpass123',
            phone_number='+8801712345679',
            user_type='service_provider'
        )
        self.assertEqual(user.user_type, 'service_provider')
    
    def test_unique_phone_number(self):
        """Test phone number uniqueness constraint"""
        User.objects.create_user(
            username='user1',
            phone_number='+8801712345678',
            password='test123'
        )
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='user2',
                phone_number='+8801712345678',
                password='test123'
            )


class CitizenProfileModelTests(TestCase):
    """Test CitizenProfile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testcitizen',
            email='citizen@test.com',
            password='testpass123',
            phone_number='+8801712345678',
            user_type='citizen'
        )
        self.profile = CitizenProfile.objects.create(user=self.user)
    
    def test_profile_creation(self):
        """Test profile is created"""
        self.assertIsNotNone(self.profile)
        self.assertEqual(self.profile.user, self.user)
    
    def test_is_profile_complete_false(self):
        """Test incomplete profile"""
        self.assertFalse(self.profile.is_profile_complete())
    
    def test_is_profile_complete_true(self):
        """Test complete profile"""
        self.profile.date_of_birth = date(1990, 1, 1)
        self.profile.blood_group = 'A+'
        self.profile.phone_number = '+8801712345678'
        self.profile.emergency_contact_name = 'John Doe'
        self.profile.emergency_contact_phone = '+8801712345679'
        self.profile.house_road_no = '123 Main St'
        self.profile.area_sector = 'Gulshan'
        self.profile.city = 'Dhaka'
        self.profile.postal_code = '1212'
        self.profile.save()
        
        self.assertTrue(self.profile.is_profile_complete())
    
    def test_blood_group_choices(self):
        """Test valid blood group choices"""
        valid_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        for group in valid_groups:
            self.profile.blood_group = group
            self.profile.save()
            self.assertEqual(self.profile.blood_group, group)


class ServiceProviderProfileModelTests(TestCase):
    """Test ServiceProviderProfile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_hospital',
            email='hospital@test.com',
            password='testpass123',
            phone_number='+8801712345678',
            user_type='service_provider'
        )
        self.profile = ServiceProviderProfile.objects.create(
            user=self.user,
            organization_name='Test Hospital',
            service_type='hospital',
            email='hospital@test.com',
            contact_number='+8801712345678'
        )
    
    def test_profile_creation(self):
        """Test service provider profile creation"""
        self.assertIsNotNone(self.profile)
        self.assertEqual(self.profile.organization_name, 'Test Hospital')
        self.assertEqual(self.profile.service_type, 'hospital')
    
    def test_get_service_display_name(self):
        """Test service display name"""
        self.assertEqual(self.profile.get_service_display_name(), 'Hospital')
        
        # Test 'others' type
        self.profile.service_type = 'others'
        self.profile.service_type_other = 'Custom Service'
        self.profile.save()
        self.assertEqual(self.profile.get_service_display_name(), 'Custom Service')
    
    def test_get_capacity_percentage(self):
        """Test capacity percentage calculation"""
        self.profile.maximum_capacity = 100
        self.profile.current_capacity = 75
        self.profile.save()
        self.assertEqual(self.profile.get_capacity_percentage(), 75.0)
        
        # Test with no capacity set
        self.profile.maximum_capacity = None
        self.profile.save()
        self.assertIsNone(self.profile.get_capacity_percentage())
    
    def test_is_profile_complete(self):
        """Test profile completion check"""
        # Initially incomplete
        self.assertFalse(self.profile.is_profile_complete())
        
        # Complete all required fields
        self.profile.street_address = '123 Hospital Road'
        self.profile.area_sector = 'Gulshan'
        self.profile.city = 'Dhaka'
        self.profile.postal_code = '1212'
        self.profile.primary_contact_person = 'Dr. Smith'
        self.profile.emergency_hotline = '+8801712345679'
        self.profile.save()
        
        self.assertTrue(self.profile.is_profile_complete())


class BloodRequestModelTests(TestCase):
    """Test BloodRequest model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            phone_number='+8801712345678',
            password='test123'
        )
    
    def test_create_blood_request(self):
        """Test creating blood request"""
        request = BloodRequest.objects.create(
            requester_name='John Doe',
            patient_name='Jane Doe',
            blood_type_needed='A+',
            bags_needed=2,
            location='Dhaka Medical College',
            contact_phone='+8801712345678',
            urgency='urgent',
            needed_by_date=date.today() + timedelta(days=1),
            created_by=self.user
        )
        self.assertIsNotNone(request)
        self.assertEqual(request.blood_type_needed, 'A+')
        self.assertEqual(request.bags_needed, 2)
        self.assertEqual(request.status, 'open')
    
    def test_is_urgent(self):
        """Test urgency check"""
        urgent_request = BloodRequest.objects.create(
            requester_name='John Doe',
            patient_name='Jane Doe',
            blood_type_needed='O+',
            location='Hospital',
            contact_phone='+8801712345678',
            urgency='urgent',
            needed_by_date=date.today()
        )
        self.assertTrue(urgent_request.is_urgent())
        
        normal_request = BloodRequest.objects.create(
            requester_name='John Doe',
            patient_name='Jane Doe',
            blood_type_needed='O+',
            location='Hospital',
            contact_phone='+8801712345679',
            urgency='normal',
            needed_by_date=date.today()
        )
        self.assertFalse(normal_request.is_urgent())


class CitizenRegistrationFormTests(TestCase):
    """Test CitizenRegistrationForm"""
    
    def test_valid_form(self):
        """Test form with valid data"""
        form_data = {
            'username': 'testcitizen',
            'email': 'citizen@test.com',
            'phone_number': '+8801712345678',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }
        form = CitizenRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_password_mismatch(self):
        """Test form with mismatched passwords"""
        form_data = {
            'username': 'testcitizen',
            'email': 'citizen@test.com',
            'phone_number': '+8801712345678',
            'password1': 'TestPass123!',
            'password2': 'DifferentPass123!'
        }
        form = CitizenRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())


class ServiceProviderRegistrationFormTests(TestCase):
    """Test ServiceProviderRegistrationForm"""
    
    def test_valid_form(self):
        """Test form with valid data"""
        form_data = {
            'organization_name': 'Test Hospital',
            'service_type': 'hospital',
            'email': 'hospital@test.com',
            'contact_number': '+8801712345678',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }
        form = ServiceProviderRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_others_service_type_validation(self):
        """Test validation when 'others' is selected"""
        form_data = {
            'organization_name': 'Custom Service',
            'service_type': 'others',
            'email': 'service@test.com',
            'contact_number': '+8801712345678',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }
        form = ServiceProviderRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        
        # Add service_type_other
        form_data['service_type_other'] = 'Custom Emergency Service'
        form = ServiceProviderRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())


class CitizenViewTests(TestCase):
    """Test citizen views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testcitizen',
            email='citizen@test.com',
            password='testpass123',
            phone_number='+8801712345678',
            user_type='citizen'
        )
        self.profile = CitizenProfile.objects.create(
            user=self.user,
            city='Dhaka',
            area_sector='Gulshan'
        )
    
    def test_citizen_dashboard_requires_login(self):
        """Test dashboard requires authentication"""
        response = self.client.get(reverse('citizen_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_citizen_dashboard_access(self):
        """Test authenticated access to dashboard"""
        self.client.login(username='testcitizen', password='testpass123')
        response = self.client.get(reverse('citizen_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
    
    def test_register_citizen_view(self):
        """Test citizen registration view"""
        response = self.client.get(reverse('register_citizen'))
        self.assertEqual(response.status_code, 200)
        
        # Test POST
        form_data = {
            'username': 'newcitizen',
            'email': 'new@test.com',
            'phone_number': '+8801712345679',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }
        response = self.client.post(reverse('register_citizen'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(User.objects.filter(username='newcitizen').exists())


class ServiceProviderViewTests(TestCase):
    """Test service provider views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test_hospital',
            email='hospital@test.com',
            password='testpass123',
            phone_number='+8801712345678',
            user_type='service_provider'
        )
        self.profile = ServiceProviderProfile.objects.create(
            user=self.user,
            organization_name='Test Hospital',
            service_type='hospital',
            email='hospital@test.com',
            contact_number='+8801712345678',
            city='Dhaka',
            street_address='123 Hospital Road',
            area_sector='Gulshan',
            postal_code='1212',
            primary_contact_person='Dr. Smith',
            emergency_hotline='+8801712345679',
            is_verified=True,
            current_status='active'
        )
    
    def test_service_provider_dashboard_requires_login(self):
        """Test dashboard requires authentication"""
        response = self.client.get(reverse('service_provider_dashboard'))
        self.assertEqual(response.status_code, 302)
    
    def test_service_provider_dashboard_access(self):
        """Test authenticated access to dashboard"""
        self.client.login(username='test_hospital', password='testpass123')
        response = self.client.get(reverse('service_provider_dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_service_provider_directory(self):
        """Test public service provider directory"""
        response = self.client.get(reverse('service_provider_directory'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Hospital')
    
    def test_service_provider_detail(self):
        """Test service provider detail view"""
        response = self.client.get(
            reverse('service_provider_detail', args=[self.profile.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Hospital')


class BloodNetworkViewTests(TestCase):
    """Test blood network views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            phone_number='+8801712345678'
        )
        self.profile = CitizenProfile.objects.create(
            user=self.user,
            blood_group='A+',
            available_to_donate='yes',
            city='Dhaka',
            phone_number='+8801712345678'
        )
    
    def test_blood_network_public_access(self):
        """Test blood network is publicly accessible"""
        response = self.client.get(reverse('blood_network'))
        self.assertEqual(response.status_code, 200)
    
    def test_create_blood_request_anonymous(self):
        """Test anonymous user can create blood request"""
        form_data = {
            'requester_name': 'John Doe',
            'patient_name': 'Jane Doe',
            'blood_type_needed': 'A+',
            'bags_needed': 2,
            'location': 'Dhaka Medical College',
            'contact_phone': '+8801712345678',
            'urgency': 'urgent',
            'needed_by_date': (date.today() + timedelta(days=1)).isoformat(),
            'additional_notes': 'Urgent requirement'
        }
        response = self.client.post(reverse('blood_network'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(BloodRequest.objects.filter(patient_name='Jane Doe').exists())
    
    def test_blood_request_api(self):
        """Test blood request JSON API"""
        BloodRequest.objects.create(
            requester_name='John Doe',
            patient_name='Jane Doe',
            blood_type_needed='O+',
            bags_needed=1,
            location='Hospital',
            contact_phone='+8801712345678',
            urgency='urgent',
            needed_by_date=date.today(),
            status='open'
        )
        response = self.client.get(reverse('blood_requests_api'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('requests', data)
        self.assertEqual(len(data['requests']), 1)


class ServiceProviderRatingTests(TestCase):
    """Test service provider rating functionality"""
    
    def setUp(self):
        self.client = Client()
        self.sp_user = User.objects.create_user(
            username='hospital',
            password='test123',
            phone_number='+8801712345678',
            user_type='service_provider'
        )
        self.sp_profile = ServiceProviderProfile.objects.create(
            user=self.sp_user,
            organization_name='Test Hospital',
            service_type='hospital',
            email='hospital@test.com',
            contact_number='+8801712345678',
            is_verified=True,
            city='Dhaka',
            street_address='123 Road',
            area_sector='Gulshan',
            postal_code='1212',
            primary_contact_person='Dr. Smith',
            emergency_hotline='+8801712345679'
        )
        self.citizen = User.objects.create_user(
            username='citizen',
            password='test123',
            phone_number='+8801712345679',
            user_type='citizen'
        )
    
    def test_create_rating(self):
        """Test creating a rating"""
        rating = ServiceProviderRating.objects.create(
            service_provider=self.sp_profile,
            user=self.citizen,
            rating=5,
            review='Excellent service!'
        )
        self.assertEqual(rating.rating, 5)
        self.assertEqual(rating.review, 'Excellent service!')
    
    def test_unique_rating_per_user(self):
        """Test user can only rate once"""
        ServiceProviderRating.objects.create(
            service_provider=self.sp_profile,
            user=self.citizen,
            rating=5
        )
        with self.assertRaises(Exception):
            ServiceProviderRating.objects.create(
                service_provider=self.sp_profile,
                user=self.citizen,
                rating=4
            )


class LogoutViewTests(TestCase):
    """Test logout functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='test123',
            phone_number='+8801712345678'
        )
    
    def test_logout(self):
        """Test user logout"""
        self.client.login(username='testuser', password='test123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect to homepage
        # Verify user is logged out
        response = self.client.get(reverse('citizen_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login