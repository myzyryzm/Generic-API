from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe
from recipe.serializers import RecipeSerializer

# -list indicates that we using the listing api for functionality; i.e. we using dat listviewset
RECIPES_URL = reverse('recipe:recipe-list')

def sample_recipe(user, **params):
    """create and return a sample recipe"""
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    # update takes dict object and updates fields that are there or it will create them if they aint there
    defaults.update(params)
    
    return Recipe.objects.create(user=user, **defaults)

class PublicRecipeAPITests(TestCase):
    """test unauthenticated recipe API access"""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_auth_required(self):
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'password'
        )
        self.client.force_authenticate(self.user)
    
    def test_retrieve_recipes(self):
        """test retrieving a list of recipes"""
        res = self.client.get(RECIPES_URL)
        
        recipes = Recipe.objects.all().order_by('-id')
        # want 2 return data s list so we have to add many=True
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    def test_recipes_limited_to_user(self):
        user2 = get_user_model().objects.create_user(
            'test2@test.com',
            'password'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)
        
        res = self.client.get(RECIPES_URL)
        
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(recipes), 1)
        self.assertEqual(res.data, serializer.data)
    
    