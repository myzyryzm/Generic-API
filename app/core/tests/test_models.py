from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models

def sample_user(email='test@test.com', password="password"):
    return get_user_model().objects.create_user(email, password)

class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """test that creating usr with email is correct"""
        email = 'test@ryan.com'
        password = 'Testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
    
    def test_new_user_email_normalized(self):
        """test email for user 2 b normalized"""
        email = 'test@RYAN.COM'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')
    
    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@test.com',
            'test123'
        )
        # is superuser is part of permissions mixin
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
    
    def test_tag_str(self):
        """test that tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )
        self.assertEqual(str(tag), tag.name)
    
    def test_tag_str(self):
        """test that ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber'
        )
        self.assertEqual(str(ingredient), ingredient.name)