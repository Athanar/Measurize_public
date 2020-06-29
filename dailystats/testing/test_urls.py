from django.test import SimpleTestCase
from django.urls import reverse, resolve
from dailystats import views

class TestUrls(SimpleTestCase):

    def test_login_url_is_resolved(self):
        url = reverse('dailystats:login')
        self.assertEquals(resolve(url).func, views.LoginView)

    def test_index_url_is_resolved1(self):
        url = reverse('dailystats:index')
        self.assertEquals(resolve(url).func, views.IndexView)

    def test_profile_url_is_resolved2(self):
        url = reverse('dailystats:profile')
        self.assertEquals(resolve(url).func, views.ProfileView)

    def test_info_url_is_resolved3(self):
        url = reverse('dailystats:info', args={'about'})
        self.assertEquals(resolve(url).func, views.infoHandler)

    def test_overview_url_is_resolved4(self):
        url = reverse('dailystats:overview')
        self.assertEquals(resolve(url).func, views.OverView)

    def test_home_url_is_resolved5(self):
        url = reverse('dailystats:home')
        self.assertEquals(resolve(url).func, views.HomeView)

    def test_registrateuser_url_is_resolved6(self):
        url = reverse('dailystats:registrateUser')
        self.assertEquals(resolve(url).func, views.registrateUser)