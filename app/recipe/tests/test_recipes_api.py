# allows u to make temp files
import tempfile
import os
from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

# -list indicates that we using the listing api for functionality; i.e. we using dat listviewset
# /api/recipe/recipes
RECIPES_URL = reverse('recipe:recipe-list')

def image_upload_url(recipe_id):
    """return image upload url"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])

# /api/recipe/recipes/:id/
def detail_url(recipe_id):
    """return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])

def sample_tag(user, name='Main course'):
    """create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)

def sample_ingredient(user, name='Cinnamon'):
    """create and return a sample tag"""
    return Ingredient.objects.create(user=user, name=name)

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
    
    def test_view_recipe_detail(self):
        """test viewing a recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))
        
        url = detail_url(recipe.id)
        res = self.client.get(url)
        
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
    
    def test_create_basic_recipe(self):
        """test creating recipe"""
        payload = {
            'title': 'Chocolate cheesecake',
            'time_minutes': 30,
            'price': 5.00
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            # getattr is used rather than recipe[key] b/c recipe[key] is not allowed as recipe is a QuerySet not a dictionary
            # getattr allows us to pass in an object and a name of a variable and get that out
            self.assertEqual(payload[key], getattr(recipe, key))
    
    def test_create_recipe_with_tags(self):
        """test creating a recipe with tags"""
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Desert')
        payload = {
            'title': 'Avocaddd',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price': 20.00
        }
        res = self.client.post(RECIPES_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)
    
    def test_create_recipe_with_ingredients(self):
        """test creating recipe with ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name='Carrot')
        ingredient2 = sample_ingredient(user=self.user, name='Ranch')
        payload = {
            'title': 'Dip',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 60,
            'price': 20.00
        }
        res = self.client.post(RECIPES_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)
    
    def test_partial_update_recipe(self):
        """updating with patch (used for updating fields in payload)"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='curry')
        
        payload = {
            'title': 'Chicken and Shit',
            'tags': [new_tag.id]
        }
        # use detail url when you want to update an object
        url = detail_url(recipe.id)
        self.client.patch(url, payload)
        
        # refreshes the db to get new values for recipe
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)
    
    def test_full_update_recipe(self):
        """teest updating recipe with put"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload={
            'title': 'Spag',
            'time_minutes': 25,
            'price': 5.00
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)
        
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)

class RecipeImageUploadTests(TestCase):
    
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'password'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.recipe = sample_recipe(user=self.user)
    
    # runs at the end; want 2 remove test files from system
    def tearDown(self):
        self.recipe.image.delete()
    
    def test_upload_image_to_recipe(self):
        """test uploading an image to recipe"""
        url = image_upload_url(self.recipe.id)
        # create a named random temp file somewhere in system (usually temp)
        # ntf => named temporary file
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10,10))
            img.save(ntf, format='JPEG')
            # tell to go back to start
            ntf.seek(0)
            # form that consists of data therefore need to add format=multipart
            res = self.client.post(url, {'image': ntf}, format='multipart')
        
        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))
    
    def test_upload_image_bad_request(self):
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')
        
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_filter_recipes_by_tags(self):
        """test returning recipes with specific tags"""
        recipe1 = sample_recipe(user=self.user, title='Thai Veg Curry')
        recipe2 = sample_recipe(user=self.user, title='Aubergine with tahini')
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Vegetarians')
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)
        recipe3 = sample_recipe(user=self.user, title='Fish and chips')
        
        res = self.client.get(
            RECIPES_URL,
            {'tags': f'{tag1.id},{tag2.id}'}
        )
        
        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
    
    def test_filter_recipes_by_ingredients(self):
        """test returning recipes with specific ingredients"""
        recipe1 = sample_recipe(user=self.user, title='Thai Veg Curry')
        recipe2 = sample_recipe(user=self.user, title='Aubergine with tahini')
        ingredient1 = sample_ingredient(user=self.user, name='Feta Cheese')
        ingredient2 = sample_ingredient(user=self.user, name='Stupid')
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)
        recipe3 = sample_recipe(user=self.user, title='Fish and chips')
        # makes url of /api/recipe/recipes/?ingredients=:id1,:id2,etc...
        # second argument is a list of query params
        res = self.client.get(
            RECIPES_URL,
            {'ingredients': f'{ingredient1.id},{ingredient2.id}'}
        )
        
        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)