from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

class AdminSiteTests(TestCase):
    # run b4 all tests are run
    def setUp(self):
        # makes all these vars 
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@test.com',
            password='pass123'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='test@test.com',
            password='test123',
            name='Test user full name'
        )
    
    def test_users_listed(self):
        # generate url for list user page
        # use reverse b/c if we ever change the url this will still be able to find it
        # get the changelist (i.e. the list of all the users)
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        # check that response has a certain items; also 200 response and content of res
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)
    
    def test_user_change_page(self):
        """test that user edit page works"""
        #/admin/core/user/:id is the endpoint for the following
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
    
    def test_create_user_page(self):
        """test that create user page works"""
        url=reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)