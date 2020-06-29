from django.test import SimpleTestCase, TestCase, Client, RequestFactory
from django.urls import reverse, resolve
from dailystats import views, urls, models
from django.contrib.auth.models import Permission, User
from django.contrib.auth import authenticate, login, logout
import json, datetime
from django.utils import timezone
from dailystats.StatHandling import mfUpdater

datetime.datetime.now(tz=timezone.utc)

class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.index_url = reverse('dailystats:index')
        self.login_url  = reverse('dailystats:login')
        self.profile_url = reverse('dailystats:profile')
        self.overview_url = reverse('dailystats:overview')
        self.home_url = reverse('dailystats:home')
        self.register_url = reverse('dailystats:registrateUser')
        self.client.force_login(User.objects.get_or_create(username="testuser")[0])

    def test_index_view(self):
        response = self.client.get(self.index_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'dailystats/index.html')
    
    def test_info_view(self):
        sites = ['about', 'news', 'contact', 'navbar', 'sidenav']

        for address in sites:
            self.info_url = reverse('dailystats:info', args={address})
            response = self.client.get(self.info_url)
            self.assertEquals(response.status_code, 200)
            self.assertTemplateUsed(response, f'dailystats/{address}.html')

class TestLogin(TestCase):
    def setUp(self):
        self.client = Client()
        self.request_factory = RequestFactory()
        self.login_url  = reverse('dailystats:login')

    def test_loginview(self):
        response = self.client.get(self.login_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'dailystats/login.html')

    def test_loginview_logout_no_user(self):
        response = self.client.post(self.login_url,{
            'action': 'logout_button',
        })
        self.assertEquals(response.context['approval'], "Logged out successfully")
        self.assertFalse(response.context['new_user'])
        self.assertFalse(response.context['user'].is_active)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'dailystats/login.html')
        self.assertEquals(response.context['approval'], "Logged out successfully")  

    def test_loginview_logout_with_user(self):
        self.user = User.objects.create_user(username= 'testuser1', password='secret')
        response = self.client.post(self.login_url, {
            'action': 'login',
            'name': 'testuser1',
            'password': 'secret'
        })
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, b"Success")

        response_next = self.client.post(self.login_url, {
            'action': 'logout_button',
        })
        self.assertFalse(response_next.context['new_user'])
        self.assertFalse(response_next.context['user'].is_active)
        self.assertEquals(response_next.status_code, 200)
        self.assertTemplateUsed(response_next, 'dailystats/login.html')
        self.assertEquals(response_next.context['approval'], "Logged out successfully")

    def test_loginview_logout_with_user_force(self):
        self.client.force_login(User.objects.get_or_create(username="testuser")[0])

        response_next = self.client.post(self.login_url, {
            'action': 'logout_button',
        })
        self.assertFalse(response_next.context['new_user'])
        self.assertFalse(response_next.context['user'].is_active)
        self.assertEquals(response_next.status_code, 200)
        self.assertTemplateUsed(response_next, 'dailystats/login.html')

    def test_loginview_logout_with_user_force_failure(self):
        self.client.force_login(User.objects.get_or_create(username="testuser")[0])

        response_next = self.client.post(self.login_url, {
            'action': 'logout_button_random_failure',
        })
        self.assertFalse(response_next.context['new_user'])
        self.assertTrue(response_next.context['user'].is_active)
        self.assertEquals(response_next.status_code, 200)
        self.assertTemplateUsed(response_next, 'dailystats/login.html')
        self.assertNotEquals(response_next.context['approval'], "Logged out successfully")

    def test_loginview_newuser_pushed(self):
        response = self.client.post(self.login_url, {'action': 'new_user',})

        self.assertTrue(response.context['new_user'])
        self.assertFalse(response.context['user'].is_active)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'dailystats/login.html')

    def test_loginview_valid_user_login(self):
        self.user = User.objects.create_user(username= 'testuser1', password = 'secret')

        response = self.client.post(self.login_url, {
            'action': 'login',
            'name': 'testuser1',
            'password': 'secret'
        })

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, b"Success")

    def test_loginview_valid_user_login_2(self):
        self.user = User.objects.create_user(username= 'testuser50', password = 'secret')

        response = self.client.post(self.login_url, {
            'action': 'login',
            'name': 'testuser50',
            'password': 'secret'
        })

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, b"Success")

    def test_loginview_wrong_password_user_login(self):
        self.user = User.objects.create_user(username= 'testuser50', password= 'secret')

        response = self.client.post(self.login_url, {
            'action': 'login',
            'name': 'testuser50',
            'password': 'notsecret1'
        })

        self.assertEquals(response.status_code, 200)
        self.assertFalse(response.context['new_user'])
        self.assertTemplateUsed(response, 'dailystats/login.html')

    def test_loginview_wrong_username_user_login(self):
        self.user = User.objects.create_user(username= 'testuser50', password= 'secret')

        response = self.client.post(self.login_url, {
            'action': 'login',
            'name': 'testing',
            'password': 'secret'
        })

        self.assertEquals(response.status_code, 200)
        self.assertFalse(response.context['new_user'])
        self.assertTemplateUsed(response, 'dailystats/login.html')

    def test_loginview_all_wrong_user_login(self):
        self.user = User.objects.create_user(username= 'testuser50', password= 'secret')

        response = self.client.post(self.login_url, {
            'action': 'login',
            'name': 'testingasdasd',
            'password': 'secret12345'
        })

        self.assertEquals(response.status_code, 200)
        self.assertFalse(response.context['new_user'])
        self.assertTemplateUsed(response, 'dailystats/login.html')

    def test_loginview_password_empty_user_login(self):
        self.user = User.objects.create_user(username= 'testuser50', password= 'secret')

        response = self.client.post(self.login_url, {
            'action': 'login',
            'name': 'testingasdasd',
            'password': ''
        })

        self.assertEquals(response.status_code, 200)
        self.assertFalse(response.context['new_user'])
        self.assertTemplateUsed(response, 'dailystats/login.html')

    def test_loginview_username_empty_user_login(self):
        self.user = User.objects.create_user(username= 'testuser50', password= 'secret')

        response = self.client.post(self.login_url, {
            'action': 'login',
            'name': '',
            'password': 'secret'
        })

        self.assertEquals(response.status_code, 200)
        self.assertFalse(response.context['new_user'])
        self.assertTemplateUsed(response, 'dailystats/login.html')

    def test_loginview_both_empty_user_login(self):
        self.user = User.objects.create_user(username= 'testuser50', password= 'secret')

        response = self.client.post(self.login_url, {
            'action': 'login',
            'name': '',
            'password': ''
        })

        self.assertEquals(response.status_code, 200)
        self.assertFalse(response.context['new_user'])
        self.assertTemplateUsed(response, 'dailystats/login.html')

    def test_loginview_wrong_action_user_login(self):
        self.user = User.objects.create_user(username= 'testuser50', password= 'secret')

        response = self.client.post(self.login_url, {
            'action': 'logint',
            'name': 'testuser50',
            'password': 'secret'
        })

        self.assertEquals(response.status_code, 200)
        self.assertFalse(response.context['new_user'])
        self.assertTemplateUsed(response, 'dailystats/login.html')

class TestRegistrate(TestCase):
    def setUp(self):
        self.client = Client()
        self.request_factory = RequestFactory()
        self.register_url = reverse('dailystats:registrateUser')

    def test_register_view(self):
        response = self.client.get(self.register_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'dailystats/login.html')

    def test_register_username_check_false(self):
        response = self.client.post(self.register_url, {
            'name': '',
            'password': 'hans',
            'confirmation': 'hans'
        })
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.context['approval'] == 'Please input username')
        self.assertTrue(response.context['new_user'])
        self.assertTemplateUsed(response, 'dailystats/login.html')

    def test_register_password_check_false(self):
        response = self.client.post(self.register_url, {
            'name': 'hans',
            'password': '',
            'confirmation': ''
        })
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.context['approval'] == 'Please input password')
        self.assertTrue(response.context['new_user'])
        self.assertTemplateUsed(response, 'dailystats/login.html')

    def test_register_confirmation_check_false_empty(self):
        response = self.client.post(self.register_url, {
            'name': 'hans',
            'password': '1234',
            'confirmation': ''
        })
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.context['approval'] == 'Failure - passwords not matching')
        self.assertTrue(response.context['new_user'])
        self.assertTemplateUsed(response, 'dailystats/login.html')

    def test_register_confirmation_check_false(self):
        response = self.client.post(self.register_url, {
            'name': 'hans',
            'password': '1234',
            'confirmation': '4321'
        })
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.context['approval'] == 'Failure - passwords not matching')
        self.assertTrue(response.context['new_user'])
        self.assertTemplateUsed(response, 'dailystats/login.html')

    def test_register_username_taken_check(self):
        self.user = User.objects.create_user(username= 'testuser50', password= 'secret')

        response = self.client.post(self.register_url, {
            'name': 'testuser50',
            'password': '1234',
            'confirmation': '4321'
        })
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.context['approval'] == 'Failure - user already exists')
        self.assertTrue(response.context['new_user'])
        self.assertTemplateUsed(response, 'dailystats/login.html')

    def test_register_username_taken_check_2(self):
        self.user = User.objects.create_user(username= 'testuser50', password= 'secret')

        response = self.client.post(self.register_url, {
            'name': 'testuser50',
            'password': '1234',
            'confirmation': '1234'
        })
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.context['approval'] == 'Failure - user already exists')
        self.assertTrue(response.context['new_user'])
        self.assertTemplateUsed(response, 'dailystats/login.html')

    def test_register_user_successfully(self):
        response = self.client.post(self.register_url, {
            'name': 'testuser51',
            'password': '1234',
            'confirmation': '1234'
        })
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.context['approval'] == 'Success')
        self.assertEquals(User.objects.first().username, 'testuser51')
        self.assertFalse(response.context['new_user'])
        self.assertTemplateUsed(response, 'dailystats/login.html')

    def test_register_empty_input(self):
        response = self.client.post(self.register_url, {
            'name': '',
            'password': '',
            'confirmation': ''
        })
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.context['approval'] == 'Please input username')
        self.assertTrue(response.context['new_user'])
        self.assertTemplateUsed(response, 'dailystats/login.html')

class TestOverview(TestCase):
    def setUp(self):
        self.client = Client()
        self.request_factory = RequestFactory()
        self.overview_url = reverse('dailystats:overview')

    def test_overview_view_redirect_no_login(self):
        response = self.client.get(self.overview_url)

        self.assertEquals(response.status_code, 302)

    def test_overview_view(self):
        self.client.force_login(User.objects.get_or_create(username="testuser")[0])
        response = self.client.get(self.overview_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'dailystats/overview.html')

    def test_overview_output(self):
        self.client.force_login(User.objects.get_or_create(username="testuser")[0])
        response = self.client.get(self.overview_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'dailystats/overview.html')
        self.assertTrue(response.context['amounts'] == [])
        self.assertTrue(response.context['total_results'] == [])
        self.assertTrue(response.context['dates'][0] == datetime.date.today() - datetime.timedelta(days=6))
        self.assertTrue(response.context['dates'][6] == datetime.date.today())

class TestHome(TestCase):
    def setUp(self):
        self.client = Client()
        self.request_factory = RequestFactory()
        self.home_url = reverse('dailystats:home')

    def test_home_view_redirect(self):
        response = self.client.get(self.home_url)

        self.assertEquals(response.status_code, 302)

    def test_home_view(self):
        self.client.force_login(User.objects.get_or_create(username="testuser")[0])
        response = self.client.get(self.home_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'dailystats/measurefields.html')

    def test_home_view_output(self):
        self.assertFalse(models.Measure.objects.exists())

        self.client.force_login(User.objects.get_or_create(username="testuser")[0])
        response = self.client.post(self.home_url, {
            'name': 'testing',
            'value': 3.0,
            'number': 2.0
        })

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'dailystats/measurefields.html')
        self.assertEqual(response.context['measures'][0].id, models.Measure.objects.all()[0].id)
        self.assertEqual(response.context['totals'][0][0], 6)

    def test_home_view_output_multiple(self):
        self.client.force_login(User.objects.get_or_create(username="testuser")[0])
        self.client.post(self.home_url, {
            'name': 'testing',
            'value': 3.0,
            'number': 2.0
        })

        response = self.client.post(self.home_url, {
            'name': 'testing_again',
            'value': 6.0,
            'number': 4.0
        })

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'dailystats/measurefields.html')
        self.assertEqual(response.context['measures'][1].id, models.Measure.objects.all()[1].id)
        self.assertEqual(response.context['totals'][0][0], 30)

    def test_home_view_output_multiple_different_dates(self):
        self.client.force_login(User.objects.get_or_create(username="testuser")[0])
        self.client.post(self.home_url, {
            'name': 'testing',
            'value': 3.0,
            'number': 2.0
        })

        test_amount = models.AmountModel.objects.first()
        test_amount.creation_date -= datetime.timedelta(days=1)
        test_amount.save()

        response = self.client.post(self.home_url, {
            'name': 'testing_again',
            'value': 6.0,
            'number': 4.0
        })

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'dailystats/measurefields.html')
        self.assertEqual(response.context['measures'][1].id, models.Measure.objects.all()[1].id)
        self.assertEqual(response.context['totals'][0][0], 24)

    def test_home_view_amount_generator_different_dates(self):
        self.client.force_login(User.objects.get_or_create(username="testuser")[0])
        self.client.post(self.home_url, {
            'name': 'testing',
            'value': 3.0,
            'number': 2.0
        })

        self.assertEqual(models.AmountModel.objects.count(), 1)
        
        test_measure = models.Measure.objects.first()
        test_measure.last_updated = datetime.date.today() - datetime.timedelta(days=1)
        test_measure.save()

        response = self.client.post(self.home_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'dailystats/measurefields.html')
        self.assertEqual(response.context['measures'][0].id, models.Measure.objects.first().id)
        self.assertEqual(response.context['totals'][0][0], 6)
        self.assertEqual(models.AmountModel.objects.count(), 2)

    def test_home_view_updater(self):
        self.client.force_login(User.objects.get_or_create(username="testuser")[0])
        self.client.post(self.home_url, {
            'name': 'testing',
            'value': 3.0,
            'number': 2.0
        })
        measure_id = f'mf_amount_{models.Measure.objects.first().id}'  
        response = self.client.post(self.home_url, {
            'action': 'update_valuefield',
            'new_value': 5.0,
            'measure_id': measure_id
        })
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'dailystats/measurefields.html')
        self.assertEqual(response.context['measures'][0].id, models.Measure.objects.first().id)
        self.assertEqual(response.context['totals'][0][0], 15)
        self.assertEqual(models.Measure.objects.first().measure_input, 5.0)

    def test_home_view_updater_many(self):
        self.client.force_login(User.objects.get_or_create(username="testuser")[0])

        for i in range(20):
            self.client.post(self.home_url, {
            'name': f'testing{i}',
            'value': 3.0,
            'number': 2.0
            })
            measure_id = f'mf_amount_{models.Measure.objects.all()[i].id}'  
            self.client.post(self.home_url, {
            'action': 'update_valuefield',
            'new_value': 15.0 - i,
            'measure_id': measure_id
            })
        
        response = self.client.post(self.home_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'dailystats/measurefields.html')
        self.assertEqual(response.context['measures'][0].id, models.Measure.objects.first().id)
        self.assertEqual(response.context['measures'][19].id, models.Measure.objects.all()[19].id)
        self.assertEqual(models.Measure.objects.count(), 20)
        self.assertEqual(models.AmountModel.objects.count(), 20)
        self.assertEqual(models.Measure.objects.first().measure_input, 15.0)
        self.assertEqual(models.Measure.objects.all()[9].measure_input, 6.0)
        self.assertEqual(models.Measure.objects.last().measure_input, 0.0)

    def test_home_view_deletion(self):
        self.client.force_login(User.objects.get_or_create(username="testuser")[0])
        self.client.post(self.home_url, {
            'name': 'testing',
            'value': 3.0,
            'number': 2.0
        })
        self.client.post(self.home_url, {
            'name': 'testing2',
            'value': 4.0,
            'number': 3.0
        })

        self.assertEqual(models.Measure.objects.count(), 2)

        test_action = f'mf_deleteb_{models.Measure.objects.first().id}'  
        response = self.client.post(self.home_url, {
            'check': 'delete',
            'action': test_action
        })
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'dailystats/measurefields.html')
        self.assertEqual(response.context['measures'][0].id, models.Measure.objects.first().id)
        self.assertEqual(models.Measure.objects.first().measure_input, 3.0)
        self.assertEqual(models.Measure.objects.count(), 1)
        self.assertEqual(models.AmountModel.objects.count(), 1)

class TestProfile(TestCase):
    def setUp(self):
        self.client = Client()
        self.request_factory = RequestFactory()
        self.profile_url = reverse('dailystats:profile')
        self.login_url = reverse('dailystats:login')

    def test_profile_view_redirect(self):
        response = self.client.get(self.profile_url)

        self.assertEquals(response.status_code, 302)

    def test_profile_view(self):
        self.client.force_login(User.objects.get_or_create(username="testuser")[0])
        response = self.client.get(self.profile_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'dailystats/profile.html')

    def test_profile_view_base_view(self):
        self.client.force_login(User.objects.get_or_create(username="testuser")[0])
        response = self.client.get(self.profile_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'dailystats/profile.html')
        self.assertEqual(response.context['user'], User.objects.first())

    def test_profile_view_user_deletion(self):
        self.user = User.objects.create_user(username= 'testuser1', password = 'secret')

        self.client.post(self.login_url, {
            'action': 'login',
            'name': 'testuser1',
            'password': 'secret'
        })

        self.assertEqual(User.objects.count(), 1)

        response = self.client.post(self.profile_url, {
            'action': 'delete_confirmed',
        })

        self.assertEqual(User.objects.count(), 0)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'dailystats/login.html')

    def test_profile_view_username_change(self):
        self.user = User.objects.create_user(username= 'testuser1', password = 'secret')

        self.client.post(self.login_url, {
            'action': 'login',
            'name': 'testuser1',
            'password': 'secret'
        })
        self.assertEqual(User.objects.first().username, 'testuser1')

        response = self.client.post(self.profile_url, {
            'action': 'user_change_confirmed',
            'new_name': 'testuserchanged'
        })

        self.assertEqual(User.objects.first().username, 'testuserchanged')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['message'], 'Success')
        self.assertTemplateUsed(response, 'dailystats/profile.html')

    def test_profile_view_username_change_fails(self):
        self.user = User.objects.create_user(username= 'testuser1', password = 'secret')
        self.user = User.objects.create_user(username= 'testuser2', password = 'secret')

        self.client.post(self.login_url, {
            'action': 'login',
            'name': 'testuser1',
            'password': 'secret'
        })
        self.assertEqual(User.objects.first().username, 'testuser1')

        response = self.client.post(self.profile_url, {
            'action': 'user_change_confirmed',
            'new_name': 'testuser2'
        })

        self.assertEqual(User.objects.first().username, 'testuser1')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['message'], 'Username unavailable')
        self.assertTemplateUsed(response, 'dailystats/profile.html')

    def test_profile_view_username_change_no_input(self):
        self.user = User.objects.create_user(username= 'testuser1', password = 'secret')

        self.client.post(self.login_url, {
            'action': 'login',
            'name': 'testuser1',
            'password': 'secret'
        })
        self.assertEqual(User.objects.first().username, 'testuser1')

        response = self.client.post(self.profile_url, {
            'action': 'user_change_confirmed',
            'new_name': ''
        })

        self.assertEqual(User.objects.first().username, 'testuser1')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['message'], 'Error - input too short(<5)')
        self.assertTemplateUsed(response, 'dailystats/profile.html')

    def test_profile_view_username_change_input_too_short(self):
        self.user = User.objects.create_user(username= 'testuser1', password = 'secret')

        self.client.post(self.login_url, {
            'action': 'login',
            'name': 'testuser1',
            'password': 'secret'
        })
        self.assertEqual(User.objects.first().username, 'testuser1')

        response = self.client.post(self.profile_url, {
            'action': 'user_change_confirmed',
            'new_name': '1234'
        })

        self.assertEqual(User.objects.first().username, 'testuser1')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['message'], 'Error - input too short(<5)')
        self.assertTemplateUsed(response, 'dailystats/profile.html')
        

    def test_profile_view_firstname_change(self):
        self.user = User.objects.create_user(username= 'testuser1', password = 'secret', first_name='tester')

        self.client.post(self.login_url, {
            'action': 'login',
            'name': 'testuser1',
            'password': 'secret'
        })
        self.assertEqual(User.objects.first().first_name, 'tester')

        response = self.client.post(self.profile_url, {
            'action': 'first_change_confirmed',
            'new_name': 'testuserchanged'
        })

        self.assertEqual(User.objects.first().first_name, 'testuserchanged')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['message'], 'Success')
        self.assertTemplateUsed(response, 'dailystats/profile.html')

    def test_profile_view_lastname_change(self):
        self.user = User.objects.create_user(username= 'testuser1', password = 'secret', last_name='tester')

        self.client.post(self.login_url, {
            'action': 'login',
            'name': 'testuser1',
            'password': 'secret'
        })
        self.assertEqual(User.objects.first().last_name, 'tester')

        response = self.client.post(self.profile_url, {
            'action': 'last_change_confirmed',
            'new_name': 'testuserchanged'
        })

        self.assertEqual(User.objects.first().last_name, 'testuserchanged')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['message'], 'Success')
        self.assertTemplateUsed(response, 'dailystats/profile.html')

    def test_profile_view_email_change(self):
        self.user = User.objects.create_user(username= 'testuser1', password = 'secret', email='tester@hotmail.dk')

        self.client.post(self.login_url, {
            'action': 'login',
            'name': 'testuser1',
            'password': 'secret'
        })
        self.assertEqual(User.objects.first().email, 'tester@hotmail.dk')

        response = self.client.post(self.profile_url, {
            'action': 'mail_change_confirmed',
            'new_email': 'tester@gmail.dk',
            'repeat_new_email': 'tester@gmail.dk'
        })
        self.assertEqual(User.objects.first().email, 'tester@gmail.dk')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['message'], 'Success')
        self.assertTemplateUsed(response, 'dailystats/profile.html')

    def test_profile_view_email_change_not_matching(self):
        self.user = User.objects.create_user(username= 'testuser1', password = 'secret', email='tester@hotmail.dk')

        self.client.post(self.login_url, {
            'action': 'login',
            'name': 'testuser1',
            'password': 'secret'
        })
        self.assertEqual(User.objects.first().email, 'tester@hotmail.dk')

        response = self.client.post(self.profile_url, {
            'action': 'mail_change_confirmed',
            'new_email': 'tester@gmail.dk',
            'repeat_new_email': 'false_email'
        })
        self.assertEqual(User.objects.first().email, 'tester@hotmail.dk')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['message'], 'Inputs do not match')
        self.assertTemplateUsed(response, 'dailystats/profile.html')

    def test_profile_view_email_change_empty_input(self):
        self.user = User.objects.create_user(username= 'testuser1', password = 'secret', email='tester@hotmail.dk')

        self.client.post(self.login_url, {
            'action': 'login',
            'name': 'testuser1',
            'password': 'secret'
        })
        self.assertEqual(User.objects.first().email, 'tester@hotmail.dk')

        response = self.client.post(self.profile_url, {
            'action': 'mail_change_confirmed',
            'new_email': '',
            'repeat_new_email': ''
        })
        self.assertEqual(User.objects.first().email, 'tester@hotmail.dk')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['message'], 'Error - input too short(<5)')
        self.assertTemplateUsed(response, 'dailystats/profile.html')

    def test_profile_view_email_change_input_too_short(self):
        self.user = User.objects.create_user(username= 'testuser1', password = 'secret', email='tester@hotmail.dk')

        self.client.post(self.login_url, {
            'action': 'login',
            'name': 'testuser1',
            'password': 'secret'
        })
        self.assertEqual(User.objects.first().email, 'tester@hotmail.dk')

        response = self.client.post(self.profile_url, {
            'action': 'mail_change_confirmed',
            'new_email': '1234',
            'repeat_new_email': '1234'
        })
        self.assertEqual(User.objects.first().email, 'tester@hotmail.dk')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['message'], 'Error - input too short(<5)')
        self.assertTemplateUsed(response, 'dailystats/profile.html')

    def test_profile_view_password_change(self):
        self.user = User.objects.create_user(username= 'testuser1', password = 'secret')

        self.client.post(self.login_url, {
            'action': 'login',
            'name': 'testuser1',
            'password': 'secret'
        })

        response = self.client.post(self.profile_url, {
            'action': 'pass_change_confirmed',
            'new_password': 'secret2',
            'repeat_new_password': 'secret2'
        })

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['approval'], 'Password changed')
        self.assertTemplateUsed(response, 'dailystats/login.html')

    def test_profile_view_password_change_not_matching(self):
        self.user = User.objects.create_user(username= 'testuser1', password = 'secret')

        self.client.post(self.login_url, {
            'action': 'login',
            'name': 'testuser1',
            'password': 'secret'
        })

        response = self.client.post(self.profile_url, {
            'action': 'pass_change_confirmed',
            'new_password': 'secret2',
            'repeat_new_password': 'secret_fail'
        })

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['message'], 'Inputs do not match')
        self.assertTemplateUsed(response, 'dailystats/profile.html')

    def test_profile_view_password_change_empty_input(self):
        self.user = User.objects.create_user(username= 'testuser1', password = 'secret')

        self.client.post(self.login_url, {
            'action': 'login',
            'name': 'testuser1',
            'password': 'secret'
        })

        response = self.client.post(self.profile_url, {
            'action': 'pass_change_confirmed',
            'new_password': '',
            'repeat_new_password': ''
        })

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['message'], 'Error - input too short(<5)')
        self.assertTemplateUsed(response, 'dailystats/profile.html')

    def test_profile_view_password_change_too_short_input(self):
        self.user = User.objects.create_user(username= 'testuser1', password = 'secret')

        self.client.post(self.login_url, {
            'action': 'login',
            'name': 'testuser1',
            'password': 'secret'
        })

        response = self.client.post(self.profile_url, {
            'action': 'pass_change_confirmed',
            'new_password': '1234',
            'repeat_new_password': '1234'
        })

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context['message'], 'Error - input too short(<5)')
        self.assertTemplateUsed(response, 'dailystats/profile.html')