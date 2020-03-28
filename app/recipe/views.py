from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe
from recipe import serializers

class BaseRecipeAttrViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    """base viewset for user owned recipe attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    # this is what is called when the ListModelMixin is called (i.e)
    def get_queryset(self):
        """return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# when u define the list model mixin you add a query set
# basically this stupid thing is designed to be a get request
# create model mixin
class TagViewSet(BaseRecipeAttrViewSet):
    """manage tags in the database"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    
class IngredientViewSet(BaseRecipeAttrViewSet):
    """manages ingredients in the database"""
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    
class RecipeViewSet(viewsets.ModelViewSet):
    """manage recipes in db"""
    
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """return appro serializer class"""
        # the actions that this view set can get are either list or retrieve, for retrieve we want to give the detailed view and the detail serializer will give the serialized ingredients and tags
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        
        return self.serializer_class
    
    def perform_create(self, serializer):
        """create a new recipe"""
        # if you pass a serializer in and it is assigned a model, then when you pass it any values (such as telling it who the user is here), it will know what to do
        serializer.save(user=self.request.user)
