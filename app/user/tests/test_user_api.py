from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

# allows us to test api requests
# allows us to make requests to api
from rest_framework.test import APIClient
# gives us the ability to see status codes
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

# remember that **param means as many arguments as you want
def create_user(**params):
    return get_user_model().objects.create_user(**params)

# call it public b/c anyone on the internet can make the request (makes sense b/c this is a create user request)
class PublicUserApiTests(TestCase):
    """test the users api (public)"""
    def setUp(self):
        self.client = APIClient()
    
    def test_create_valid_user_success(self):
        payload = {
            'email': 'ryan@ryan.com',
            'password': 'testpass',
            'name': 'Test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        # expects res.data to look like the payload except with extra id
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        # make sure password is not passed in the response
        self.assertNotIn('password', res.data)
    
    def test_user_exists_self(self):
        """"""
        payload = {'email': 'ryan@ryan.com', 'password': 'testpass', 'name': 'Test'}
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_password_too_short(self):
        """"test that pass must be more than 5 characters"""
        payload={'email': 'ryan@ryan.com', 'password': 'pw', 'name': 'Test'}
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)
    
    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {'email': 'ryan@ryan.com', 'password': 'password'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        # checks that token exists in res.data
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
    
    def test_create_token_invalid_credentials(self):
        """test that token is not created if invalid credentials are given"""
        create_user(email='ryan@ryan.com', password='password')
        payload = {'email': 'ryan@ryan.com', 'password': 'wrong'}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_token_no_user(self):
        payload = {'email': 'ryan@ryan.com', 'password': 'password'}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_token_missing_field(self):
        """test that email and password and required"""
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_retrieve_user_unauthorized(self):
        """test that authentication is required for users"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserApiTests(TestCase):
    """test aPI requests that require authentication"""
    
    def setUp(self):
        self.user = create_user(
            email='ryan@test.com',
            password='password',
            name='name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_retrieve_profile_success(self):
        """test retrievving profile for logged in user"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })
    
    def test_post_me_not_allowed(self):
        """"test than POST is not allowed on me url"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_update_user_profile(self):
        """test updating the user profile for authenticated user"""
        payload = {'name': 'new name', 'password': 'newpassword123'}
        
        res = self.client.patch(ME_URL, payload)
        # refresh_from_db updates the values in the database after we have updated them
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)