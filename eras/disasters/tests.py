from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date, timedelta
from PIL import Image
import io

from disasters.models import (
    Disaster, DisasterImage, DisasterAlert, DisasterUpdate,
    DisasterResponse, DisasterReport
)
from disasters.forms import (
    DisasterForm, DisasterImageForm, DisasterFilterForm,
    DisasterResponseForm, DisasterReportForm, AdminDisasterForm
)
from accounts.models import CitizenProfile, ServiceProviderProfile

User = get_user_model()


class DisasterModelTests(TestCase):
    """Test Disaster model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='test123',
            phone_number='+8801712345678',
            user_type='citizen'
        )
        self.profile = CitizenProfile.objects.create(
            user=self.user,
            city='Dhaka',
            area_sector='Gulshan'
        )
    
    def test_create_disaster(self):
        """Test creating a disaster"""
        disaster = Disaster.objects.create(
            title='Test Earthquake',
            disaster_type='earthquake',
            severity='high',
            description='Test earthquake description here',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.user
        )
        self.assertIsNotNone(disaster)
        self.assertEqual(disaster.disaster_type, 'earthquake')
        self.assertEqual(disaster.category, 'natural')
        self.assertEqual(disaster.status, 'draft')
    
    def test_auto_title_generation(self):
        """Test automatic title generation"""
        disaster = Disaster.objects.create(
            disaster_type='flood',
            severity='critical',
            description='Severe flooding in area',
            city='Dhaka',
            area_sector='Mirpur',
            incident_datetime=timezone.now(),
            reporter=self.user
        )
        self.assertEqual(disaster.title, 'Flood in Dhaka')
    
    def test_category_auto_assignment(self):
        """Test category is automatically assigned based on disaster type"""
        # Natural disaster
        natural = Disaster.objects.create(
            disaster_type='earthquake',
            severity='high',
            description='Test earthquake',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.user
        )
        self.assertEqual(natural.category, 'natural')
        
        # Man-made disaster
        manmade = Disaster.objects.create(
            disaster_type='building_fire',
            severity='high',
            description='Test fire',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.user
        )
        self.assertEqual(manmade.category, 'manmade')
    
    def test_get_time_since_reported(self):
        """Test time since reported calculation"""
        disaster = Disaster.objects.create(
            disaster_type='flood',
            severity='high',
            description='Test flood',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.user
        )
        time_str = disaster.get_time_since_reported()
        self.assertIn('ago', time_str.lower())
    
    def test_get_severity_color(self):
        """Test severity color mapping"""
        disaster = Disaster.objects.create(
            disaster_type='flood',
            severity='critical',
            description='Test',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.user
        )
        color = disaster.get_severity_color()
        self.assertIn('red', color)
    
    def test_can_edit_permissions(self):
        """Test edit permissions"""
        disaster = Disaster.objects.create(
            disaster_type='flood',
            severity='high',
            description='Test',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.user,
            status='draft'
        )
        
        # Reporter can edit draft
        self.assertTrue(disaster.can_edit(self.user))
        
        # Other user cannot edit
        other_user = User.objects.create_user(
            username='other',
            password='test123',
            phone_number='+8801712345679'
        )
        self.assertFalse(disaster.can_edit(other_user))
        
        # Approved disaster cannot be edited by reporter
        disaster.status = 'approved'
        disaster.save()
        self.assertFalse(disaster.can_edit(self.user))
    
    def test_can_delete_permissions(self):
        """Test delete permissions"""
        disaster = Disaster.objects.create(
            disaster_type='flood',
            severity='high',
            description='Test',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.user,
            status='draft'
        )
        
        # Reporter can delete draft
        self.assertTrue(disaster.can_delete(self.user))
        
        # Cannot delete approved
        disaster.status = 'approved'
        disaster.save()
        self.assertFalse(disaster.can_delete(self.user))


class DisasterImageModelTests(TestCase):
    """Test DisasterImage model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='test123',
            phone_number='+8801712345678'
        )
        self.disaster = Disaster.objects.create(
            disaster_type='flood',
            severity='high',
            description='Test',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.user
        )
    
    def create_test_image(self):
        """Helper to create test image"""
        file = io.BytesIO()
        image = Image.new('RGB', (100, 100), color='red')
        image.save(file, 'PNG')
        file.seek(0)
        return SimpleUploadedFile('test.png', file.read(), content_type='image/png')
    
    def test_create_disaster_image(self):
        """Test creating disaster image"""
        image = DisasterImage.objects.create(
            disaster=self.disaster,
            image=self.create_test_image(),
            caption='Test image',
            is_primary=True
        )
        self.assertIsNotNone(image)
        self.assertTrue(image.is_primary)
        self.assertEqual(image.caption, 'Test image')


class DisasterAlertModelTests(TestCase):
    """Test DisasterAlert model"""
    
    def setUp(self):
        self.reporter = User.objects.create_user(
            username='reporter',
            password='test123',
            phone_number='+8801712345678'
        )
        self.citizen = User.objects.create_user(
            username='citizen',
            password='test123',
            phone_number='+8801712345679'
        )
        self.disaster = Disaster.objects.create(
            disaster_type='flood',
            severity='critical',
            description='Test',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.reporter
        )
    
    def test_create_alert(self):
        """Test creating disaster alert"""
        alert = DisasterAlert.objects.create(
            disaster=self.disaster,
            user=self.citizen,
            match_type='exact'
        )
        self.assertIsNotNone(alert)
        self.assertFalse(alert.is_read)
        self.assertEqual(alert.match_type, 'exact')
    
    def test_unique_alert_per_user(self):
        """Test each user gets only one alert per disaster"""
        DisasterAlert.objects.create(
            disaster=self.disaster,
            user=self.citizen,
            match_type='exact'
        )
        with self.assertRaises(Exception):
            DisasterAlert.objects.create(
                disaster=self.disaster,
                user=self.citizen,
                match_type='city'
            )


class DisasterResponseModelTests(TestCase):
    """Test DisasterResponse model"""
    
    def setUp(self):
        self.citizen = User.objects.create_user(
            username='citizen',
            password='test123',
            phone_number='+8801712345678',
            user_type='citizen'
        )
        self.sp_user = User.objects.create_user(
            username='hospital',
            password='test123',
            phone_number='+8801712345679',
            user_type='service_provider'
        )
        self.sp_profile = ServiceProviderProfile.objects.create(
            user=self.sp_user,
            organization_name='Test Hospital',
            service_type='hospital',
            email='hospital@test.com',
            contact_number='+8801712345679',
            city='Dhaka',
            area_sector='Gulshan'
        )
        self.disaster = Disaster.objects.create(
            disaster_type='earthquake',
            severity='high',
            description='Test',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.citizen,
            status='approved'
        )
    
    def test_create_response(self):
        """Test creating disaster response"""
        response = DisasterResponse.objects.create(
            disaster=self.disaster,
            service_provider=self.sp_profile,
            response_status='notified',
            response_notes='We are on our way'
        )
        self.assertIsNotNone(response)
        self.assertEqual(response.response_status, 'notified')
    
    def test_unique_response_per_provider(self):
        """Test each provider can only respond once"""
        DisasterResponse.objects.create(
            disaster=self.disaster,
            service_provider=self.sp_profile,
            response_status='notified'
        )
        with self.assertRaises(Exception):
            DisasterResponse.objects.create(
                disaster=self.disaster,
                service_provider=self.sp_profile,
                response_status='responding'
            )


class DisasterReportModelTests(TestCase):
    """Test DisasterReport model"""
    
    def setUp(self):
        self.reporter = User.objects.create_user(
            username='reporter',
            password='test123',
            phone_number='+8801712345678'
        )
        self.other_user = User.objects.create_user(
            username='other',
            password='test123',
            phone_number='+8801712345679'
        )
        self.disaster = Disaster.objects.create(
            disaster_type='flood',
            severity='high',
            description='Test',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.reporter,
            status='approved'
        )
    
    def test_create_report(self):
        """Test creating disaster report"""
        report = DisasterReport.objects.create(
            disaster=self.disaster,
            reported_by=self.other_user,
            reason='false_info',
            description='This information appears to be false'
        )
        self.assertIsNotNone(report)
        self.assertEqual(report.reason, 'false_info')
        self.assertFalse(report.is_reviewed)


class DisasterFormTests(TestCase):
    """Test DisasterForm"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='test123',
            phone_number='+8801712345678'
        )
        CitizenProfile.objects.create(
            user=self.user,
            city='Dhaka',
            area_sector='Gulshan'
        )
    
    def test_valid_form(self):
        """Test form with valid data"""
        form_data = {
            'title': 'Test Disaster',
            'disaster_type': 'flood',
            'severity': 'high',
            'description': 'Test description here',
            'city': 'Dhaka',
            'area_sector': 'Gulshan',
            'incident_date': date.today(),
            'incident_time': '12:00:00'
        }
        form = DisasterForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
    
    def test_description_max_length_validation(self):
        """Test description cannot exceed 50 characters"""
        form_data = {
            'disaster_type': 'flood',
            'severity': 'high',
            'description': 'A' * 51,  # 51 characters
            'city': 'Dhaka',
            'area_sector': 'Gulshan',
            'incident_date': date.today(),
            'incident_time': '12:00:00'
        }
        form = DisasterForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)
    
    def test_description_min_length_validation(self):
        """Test description must be at least 10 characters"""
        form_data = {
            'disaster_type': 'flood',
            'severity': 'high',
            'description': 'Short',  # Less than 10 characters
            'city': 'Dhaka',
            'area_sector': 'Gulshan',
            'incident_date': date.today(),
            'incident_time': '12:00:00'
        }
        form = DisasterForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
    
    def test_future_incident_datetime_validation(self):
        """Test incident datetime cannot be in future"""
        future_date = date.today() + timedelta(days=1)
        form_data = {
            'disaster_type': 'flood',
            'severity': 'high',
            'description': 'Test description here',
            'city': 'Dhaka',
            'area_sector': 'Gulshan',
            'incident_date': future_date,
            'incident_time': '12:00:00'
        }
        form = DisasterForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())


class DisasterViewTests(TestCase):
    """Test disaster views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='test123',
            phone_number='+8801712345678',
            user_type='citizen'
        )
        self.profile = CitizenProfile.objects.create(
            user=self.user,
            city='Dhaka',
            area_sector='Gulshan'
        )
    
    def test_disaster_list_public_access(self):
        """Test disaster list is publicly accessible"""
        response = self.client.get(reverse('disasters:disaster_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_create_disaster_requires_login(self):
        """Test creating disaster requires login"""
        response = self.client.get(reverse('disasters:create_disaster'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_create_disaster_authenticated(self):
        """Test authenticated user can access create disaster"""
        self.client.login(username='testuser', password='test123')
        response = self.client.get(reverse('disasters:create_disaster'))
        self.assertEqual(response.status_code, 200)
    
    def test_create_disaster_post(self):
        """Test creating disaster via POST"""
        self.client.login(username='testuser', password='test123')
        form_data = {
            'title': 'Test Disaster',
            'disaster_type': 'flood',
            'severity': 'high',
            'description': 'Test flood description',
            'city': 'Dhaka',
            'area_sector': 'Gulshan',
            'incident_date': date.today().isoformat(),
            'incident_time': '12:00:00',
            'form-TOTAL_FORMS': '0',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '5',
        }
        response = self.client.post(reverse('disasters:create_disaster'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Disaster.objects.filter(title='Test Disaster').exists())
    
    def test_disaster_detail_view(self):
        """Test disaster detail view"""
        disaster = Disaster.objects.create(
            disaster_type='flood',
            severity='high',
            description='Test flood',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.user,
            status='approved'
        )
        response = self.client.get(
            reverse('disasters:disaster_detail', args=[disaster.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, disaster.title)
    
    def test_my_disasters_requires_login(self):
        """Test my disasters requires login"""
        response = self.client.get(reverse('disasters:my_disasters'))
        self.assertEqual(response.status_code, 302)
    
    def test_my_disasters_authenticated(self):
        """Test authenticated access to my disasters"""
        self.client.login(username='testuser', password='test123')
        response = self.client.get(reverse('disasters:my_disasters'))
        self.assertEqual(response.status_code, 200)
    
    def test_edit_disaster_permission(self):
        """Test only reporter can edit their disaster"""
        disaster = Disaster.objects.create(
            disaster_type='flood',
            severity='high',
            description='Test',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.user,
            status='draft'
        )
        
        # Reporter can edit
        self.client.login(username='testuser', password='test123')
        response = self.client.get(
            reverse('disasters:edit_disaster', args=[disaster.id])
        )
        self.assertEqual(response.status_code, 200)
        
        # Other user cannot edit
        other_user = User.objects.create_user(
            username='other',
            password='test123',
            phone_number='+8801712345679'
        )
        self.client.login(username='other', password='test123')
        response = self.client.get(
            reverse('disasters:edit_disaster', args=[disaster.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirect


class ServiceProviderResponseViewTests(TestCase):
    """Test service provider response views"""
    
    def setUp(self):
        self.client = Client()
        self.citizen = User.objects.create_user(
            username='citizen',
            password='test123',
            phone_number='+8801712345678',
            user_type='citizen'
        )
        self.sp_user = User.objects.create_user(
            username='hospital',
            password='test123',
            phone_number='+8801712345679',
            user_type='service_provider'
        )
        self.sp_profile = ServiceProviderProfile.objects.create(
            user=self.sp_user,
            organization_name='Test Hospital',
            service_type='hospital',
            email='hospital@test.com',
            contact_number='+8801712345679',
            city='Dhaka',
            area_sector='Gulshan',
            street_address='123 Road',
            postal_code='1212',
            primary_contact_person='Dr. Smith',
            emergency_hotline='+8801700000000'
        )
        self.disaster = Disaster.objects.create(
            disaster_type='earthquake',
            severity='high',
            description='Test earthquake',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.citizen,
            status='approved'
        )
    
    def test_add_response_requires_service_provider(self):
        """Test only service providers can respond"""
        self.client.login(username='citizen', password='test123')
        response = self.client.get(
            reverse('disasters:add_response', args=[self.disaster.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_add_response_service_provider(self):
        """Test service provider can add response"""
        self.client.login(username='hospital', password='test123')
        response = self.client.get(
            reverse('disasters:add_response', args=[self.disaster.id])
        )
        self.assertEqual(response.status_code, 200)
    
    def test_nearby_disasters_view(self):
        """Test nearby disasters view for service provider"""
        self.client.login(username='hospital', password='test123')
        response = self.client.get(reverse('disasters:nearby_disasters'))
        self.assertEqual(response.status_code, 200)


class CitizenNearbyDisastersViewTests(TestCase):
    """Test citizen nearby disasters view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='citizen',
            password='test123',
            phone_number='+8801712345678',
            user_type='citizen'
        )
        self.profile = CitizenProfile.objects.create(
            user=self.user,
            city='Dhaka',
            area_sector='Gulshan'
        )
        self.reporter = User.objects.create_user(
            username='reporter',
            password='test123',
            phone_number='+8801712345679'
        )
    
    def test_citizen_nearby_disasters_requires_login(self):
        """Test view requires login"""
        response = self.client.get(reverse('disasters:citizen_nearby_disasters'))
        self.assertEqual(response.status_code, 302)
    
    def test_citizen_nearby_disasters_shows_local(self):
        """Test view shows disasters in user's area"""
        # Create disaster in same area
        local_disaster = Disaster.objects.create(
            disaster_type='flood',
            severity='high',
            description='Local flood',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.reporter,
            status='approved'
        )
        
        # Create disaster in different city
        remote_disaster = Disaster.objects.create(
            disaster_type='fire',
            severity='high',
            description='Remote fire',
            city='Chittagong',
            area_sector='Patenga',
            incident_datetime=timezone.now(),
            reporter=self.reporter,
            status='approved'
        )
        
        self.client.login(username='citizen', password='test123')
        response = self.client.get(reverse('disasters:citizen_nearby_disasters'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Local flood')
        self.assertNotContains(response, 'Remote fire')


class DisasterFilterTests(TestCase):
    """Test disaster filtering"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='user',
            password='test123',
            phone_number='+8801712345678'
        )
        
        # Create various disasters
        Disaster.objects.create(
            disaster_type='flood',
            severity='high',
            description='Flood in Dhaka',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.user,
            status='approved'
        )
        Disaster.objects.create(
            disaster_type='earthquake',
            severity='critical',
            description='Earthquake in Chittagong',
            city='Chittagong',
            area_sector='Agrabad',
            incident_datetime=timezone.now(),
            reporter=self.user,
            status='approved'
        )
    
    def test_filter_by_disaster_type(self):
        """Test filtering by disaster type"""
        response = self.client.get(
            reverse('disasters:disaster_list') + '?disaster_type=flood'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Flood')
        self.assertNotContains(response, 'Earthquake')
    
    def test_filter_by_severity(self):
        """Test filtering by severity"""
        response = self.client.get(
            reverse('disasters:disaster_list') + '?severity=critical'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Chittagong')
    
    def test_filter_by_city(self):
        """Test filtering by city"""
        response = self.client.get(
            reverse('disasters:disaster_list') + '?city=Dhaka'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dhaka')
        self.assertNotContains(response, 'Chittagong')


class DisasterSearchTests(TestCase):
    """Test disaster search functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='user',
            password='test123',
            phone_number='+8801712345678'
        )
        
        Disaster.objects.create(
            title='Major Flooding Event',
            disaster_type='flood',
            severity='high',
            description='Severe flooding',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.user,
            status='approved'
        )
    
    def test_search_by_title(self):
        """Test searching by title"""
        response = self.client.get(
            reverse('disasters:disaster_list') + '?search=Major'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Major Flooding Event')
    
    def test_search_by_description(self):
        """Test searching by description"""
        response = self.client.get(
            reverse('disasters:disaster_list') + '?search=Severe'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Major Flooding Event')


class AdminDisasterViewTests(TestCase):
    """Test admin disaster management views"""
    
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username='admin',
            password='admin123',
            phone_number='+8801712345678',
            email='admin@test.com'
        )
        self.user = User.objects.create_user(
            username='user',
            password='test123',
            phone_number='+8801712345679'
        )
        self.disaster = Disaster.objects.create(
            disaster_type='flood',
            severity='high',
            description='Test flood',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.user,
            status='pending'
        )
    
    def test_admin_disasters_requires_superuser(self):
        """Test admin view requires superuser"""
        self.client.login(username='user', password='test123')
        response = self.client.get(reverse('disasters:admin_disasters'))
        self.assertEqual(response.status_code, 302)
    
    def test_admin_disasters_access(self):
        """Test superuser can access admin disasters"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('disasters:admin_disasters'))
        self.assertEqual(response.status_code, 200)
    
    def test_approve_disaster(self):
        """Test approving a disaster"""
        self.client.login(username='admin', password='admin123')
        form_data = {
            'status': 'approved',
            'rejection_reason': ''
        }
        response = self.client.post(
            reverse('disasters:approve_disaster', args=[self.disaster.id]),
            data=form_data
        )
        self.disaster.refresh_from_db()
        self.assertEqual(self.disaster.status, 'approved')
        self.assertIsNotNone(self.disaster.approved_by)


class DisasterAlertSystemTests(TestCase):
    """Test disaster alert system"""
    
    def setUp(self):
        self.reporter = User.objects.create_user(
            username='reporter',
            password='test123',
            phone_number='+8801712345678'
        )
        self.citizen1 = User.objects.create_user(
            username='citizen1',
            password='test123',
            phone_number='+8801712345679'
        )
        self.citizen2 = User.objects.create_user(
            username='citizen2',
            password='test123',
            phone_number='+8801712345680'
        )
        
        CitizenProfile.objects.create(
            user=self.citizen1,
            city='Dhaka',
            area_sector='Gulshan'
        )
        CitizenProfile.objects.create(
            user=self.citizen2,
            city='Dhaka',
            area_sector='Banani'
        )
    
    def test_alerts_sent_on_approval(self):
        """Test alerts are sent when disaster is approved"""
        disaster = Disaster.objects.create(
            disaster_type='flood',
            severity='critical',
            description='Critical flood',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.reporter,
            status='approved'
        )
        
        from disasters.views import send_disaster_alerts
        count = send_disaster_alerts(disaster)
        
        # Should send alerts to citizens in Dhaka
        self.assertGreater(count, 0)
        self.assertTrue(
            DisasterAlert.objects.filter(
                disaster=disaster,
                user=self.citizen1
            ).exists()
        )


class DisasterReportingTests(TestCase):
    """Test disaster reporting functionality"""
    
    def setUp(self):
        self.client = Client()
        self.reporter = User.objects.create_user(
            username='reporter',
            password='test123',
            phone_number='+8801712345678'
        )
        self.user = User.objects.create_user(
            username='user',
            password='test123',
            phone_number='+8801712345679'
        )
        self.disaster = Disaster.objects.create(
            disaster_type='flood',
            severity='high',
            description='Test flood',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.reporter,
            status='approved'
        )
    
    def test_report_disaster_requires_login(self):
        """Test reporting requires login"""
        response = self.client.get(
            reverse('disasters:report_disaster', args=[self.disaster.id])
        )
        self.assertEqual(response.status_code, 302)
    
    def test_report_disaster_authenticated(self):
        """Test authenticated user can report"""
        self.client.login(username='user', password='test123')
        response = self.client.get(
            reverse('disasters:report_disaster', args=[self.disaster.id])
        )
        self.assertEqual(response.status_code, 200)
    
    def test_submit_disaster_report(self):
        """Test submitting a report"""
        self.client.login(username='user', password='test123')
        form_data = {
            'reason': 'false_info',
            'description': 'This information appears to be incorrect'
        }
        response = self.client.post(
            reverse('disasters:report_disaster', args=[self.disaster.id]),
            data=form_data
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            DisasterReport.objects.filter(
                disaster=self.disaster,
                reported_by=self.user
            ).exists()
        )


class APIEndpointTests(TestCase):
    """Test API endpoints"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='user',
            password='test123',
            phone_number='+8801712345678'
        )
        CitizenProfile.objects.create(
            user=self.user,
            city='Dhaka',
            area_sector='Gulshan'
        )
    
    def test_get_areas_by_city(self):
        """Test get areas by city API"""
        response = self.client.get(
            reverse('disasters:get_areas_by_city') + '?city=Dhaka'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('areas', data)
    
    def test_mark_resolved_requires_permission(self):
        """Test mark resolved requires proper permissions"""
        disaster = Disaster.objects.create(
            disaster_type='flood',
            severity='high',
            description='Test',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.user,
            status='approved'
        )
        
        self.client.login(username='user', password='test123')
        response = self.client.post(
            reverse('disasters:mark_resolved', args=[disaster.id])
        )
        self.assertEqual(response.status_code, 200)
        
        disaster.refresh_from_db()
        self.assertEqual(disaster.status, 'resolved')
    
    def test_user_alerts_api(self):
        """Test user alerts API endpoint"""
        disaster = Disaster.objects.create(
            disaster_type='flood',
            severity='critical',
            description='Test flood',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.user,
            status='approved'
        )
        
        DisasterAlert.objects.create(
            disaster=disaster,
            user=self.user,
            match_type='exact'
        )
        
        self.client.login(username='user', password='test123')
        response = self.client.get(reverse('disasters:user_alerts'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('alerts', data)
        self.assertGreater(data['count'], 0)
    
    def test_mark_alert_read(self):
        """Test marking alert as read"""
        disaster = Disaster.objects.create(
            disaster_type='flood',
            severity='high',
            description='Test',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.user,
            status='approved'
        )
        
        alert = DisasterAlert.objects.create(
            disaster=disaster,
            user=self.user,
            match_type='city'
        )
        
        self.client.login(username='user', password='test123')
        response = self.client.post(
            reverse('disasters:mark_alert_read', args=[alert.id])
        )
        self.assertEqual(response.status_code, 200)
        
        alert.refresh_from_db()
        self.assertTrue(alert.is_read)
        self.assertIsNotNone(alert.read_at)


class DisasterUpdateModelTests(TestCase):
    """Test DisasterUpdate model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='user',
            password='test123',
            phone_number='+8801712345678'
        )
        self.disaster = Disaster.objects.create(
            disaster_type='flood',
            severity='high',
            description='Test',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.user
        )
    
    def test_create_update(self):
        """Test creating disaster update"""
        update = DisasterUpdate.objects.create(
            disaster=self.disaster,
            updated_by=self.user,
            update_type='status_change',
            old_values={'status': 'draft'},
            new_values={'status': 'pending'},
            notes='Status changed to pending'
        )
        self.assertIsNotNone(update)
        self.assertEqual(update.update_type, 'status_change')


class DisasterResponseFormTests(TestCase):
    """Test DisasterResponseForm"""
    
    def test_valid_form(self):
        """Test form with valid data"""
        form_data = {
            'response_status': 'notified',
            'response_notes': 'We have been notified',
            'estimated_arrival': (timezone.now() + timedelta(hours=1)).isoformat()
        }
        form = DisasterResponseForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_past_estimated_arrival_validation(self):
        """Test estimated arrival cannot be in past"""
        form_data = {
            'response_status': 'responding',
            'response_notes': 'On our way',
            'estimated_arrival': (timezone.now() - timedelta(hours=1)).isoformat()
        }
        form = DisasterResponseForm(data=form_data)
        self.assertFalse(form.is_valid())


class DisasterReportFormTests(TestCase):
    """Test DisasterReportForm"""
    
    def test_valid_form(self):
        """Test form with valid data"""
        form_data = {
            'reason': 'false_info',
            'description': 'This appears to be false information'
        }
        form = DisasterReportForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_description_min_length(self):
        """Test description minimum length validation"""
        form_data = {
            'reason': 'spam',
            'description': 'Short'  # Less than 10 characters
        }
        form = DisasterReportForm(data=form_data)
        self.assertFalse(form.is_valid())


class AdminDisasterFormTests(TestCase):
    """Test AdminDisasterForm"""
    
    def test_rejection_requires_reason(self):
        """Test rejection status requires reason"""
        form_data = {
            'status': 'rejected',
            'rejection_reason': ''
        }
        form = AdminDisasterForm(data=form_data)
        self.assertFalse(form.is_valid())
        
        # With reason
        form_data['rejection_reason'] = 'Invalid information provided'
        form = AdminDisasterForm(data=form_data)
        self.assertTrue(form.is_valid())


class DisasterPaginationTests(TestCase):
    """Test disaster pagination"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='user',
            password='test123',
            phone_number='+8801712345678'
        )
        
        # Create 15 disasters
        for i in range(15):
            Disaster.objects.create(
                disaster_type='flood',
                severity='high',
                description=f'Flood {i}',
                city='Dhaka',
                area_sector='Gulshan',
                incident_datetime=timezone.now(),
                reporter=self.user,
                status='approved'
            )
    
    def test_pagination_exists(self):
        """Test pagination is working"""
        response = self.client.get(reverse('disasters:disaster_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('page_obj' in response.context)
        self.assertTrue(response.context['page_obj'].has_other_pages())
    
    def test_page_two_access(self):
        """Test accessing second page"""
        response = self.client.get(reverse('disasters:disaster_list') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].number, 2)


class DisasterStatisticsTests(TestCase):
    """Test disaster statistics calculations"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='user',
            password='test123',
            phone_number='+8801712345678'
        )
        
        # Create disasters with different statuses
        Disaster.objects.create(
            disaster_type='flood',
            severity='high',
            description='Test 1',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.user,
            status='draft'
        )
        Disaster.objects.create(
            disaster_type='earthquake',
            severity='critical',
            description='Test 2',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.user,
            status='approved'
        )
        Disaster.objects.create(
            disaster_type='fire',
            severity='medium',
            description='Test 3',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.user,
            status='resolved'
        )
    
    def test_my_disasters_statistics(self):
        """Test statistics in my disasters view"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('disasters:my_disasters'))
        
        self.assertEqual(response.status_code, 200)
        stats = response.context['stats']
        self.assertEqual(stats['total'], 3)
        self.assertEqual(stats['draft'], 1)
        self.assertEqual(stats['approved'], 1)
        self.assertEqual(stats['resolved'], 1)


class DisasterImageValidationTests(TestCase):
    """Test disaster image validation"""
    
    def create_test_image(self, size_mb=1):
        """Helper to create test image of specific size"""
        file = io.BytesIO()
        # Create larger image for size testing
        image = Image.new('RGB', (1000, 1000), color='red')
        image.save(file, 'PNG')
        file.seek(0)
        return SimpleUploadedFile(
            'test.png',
            file.read(),
            content_type='image/png'
        )
    
    def test_valid_image(self):
        """Test valid image upload"""
        form = DisasterImageForm()
        self.assertIsNotNone(form)


class DisasterDeleteTests(TestCase):
    """Test disaster deletion"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='user',
            password='test123',
            phone_number='+8801712345678'
        )
        self.other_user = User.objects.create_user(
            username='other',
            password='test123',
            phone_number='+8801712345679'
        )
    
    def test_delete_own_draft(self):
        """Test user can delete their own draft"""
        disaster = Disaster.objects.create(
            disaster_type='flood',
            severity='high',
            description='Test',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.user,
            status='draft'
        )
        
        self.client.login(username='user', password='test123')
        response = self.client.post(
            reverse('disasters:delete_disaster', args=[disaster.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Disaster.objects.filter(id=disaster.id).exists())
    
    def test_cannot_delete_approved(self):
        """Test user cannot delete approved disaster"""
        disaster = Disaster.objects.create(
            disaster_type='flood',
            severity='high',
            description='Test',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.user,
            status='approved'
        )
        
        self.client.login(username='user', password='test123')
        response = self.client.get(
            reverse('disasters:delete_disaster', args=[disaster.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirect (permission denied)
    
    def test_cannot_delete_others_disaster(self):
        """Test user cannot delete other's disaster"""
        disaster = Disaster.objects.create(
            disaster_type='flood',
            severity='high',
            description='Test',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.other_user,
            status='draft'
        )
        
        self.client.login(username='user', password='test123')
        response = self.client.get(
            reverse('disasters:delete_disaster', args=[disaster.id])
        )
        self.assertEqual(response.status_code, 302)  # Redirect (permission denied)


class DisasterViewCountTests(TestCase):
    """Test disaster view count increment"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='user',
            password='test123',
            phone_number='+8801712345678'
        )
        self.disaster = Disaster.objects.create(
            disaster_type='flood',
            severity='high',
            description='Test flood',
            city='Dhaka',
            area_sector='Gulshan',
            incident_datetime=timezone.now(),
            reporter=self.user,
            status='approved'
        )
    
    def test_view_count_increments(self):
        """Test view count increments on each view"""
        initial_count = self.disaster.view_count
        
        # View disaster
        self.client.get(
            reverse('disasters:disaster_detail', args=[self.disaster.id])
        )
        
        self.disaster.refresh_from_db()
        self.assertEqual(self.disaster.view_count, initial_count + 1)
        
        # View again
        self.client.get(
            reverse('disasters:disaster_detail', args=[self.disaster.id])
        )
        
        self.disaster.refresh_from_db()
        self.assertEqual(self.disaster.view_count, initial_count + 2)