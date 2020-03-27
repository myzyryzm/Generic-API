from rest_framework import serializers
from core.models import Tag, Ingredient, Recipe

class TagSerializer(serializers.ModelSerializer):
    """serializer for tag objects"""
    
    class Meta:
        model = Tag
        fields=('id', 'name')
        read_only_fields = ('id',)

class IngredientSerializer(serializers.ModelSerializer):
    """serializer for ingredient objects"""
    
    class Meta:
        model = Ingredient
        fields=('id', 'name')
        read_only_fields = ('id',)

class RecipeSerializer(serializers.ModelSerializer):
    """serialize a recipe"""
    # creates a pk related field and allow many and the qset that will be all the ingredients
    #list ingredients with the ids 
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredient.objects.all()
    )
    
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    
    class Meta:
        model = Recipe
        fields=('id', 'title', 'tags', 'ingredients', 'time_minutes', 'price', 'link')
        read_only_fields = ('id',)
        