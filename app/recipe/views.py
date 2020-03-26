from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient
from recipe import serializers

# when u define the list model mixin you add a query set
# basically this stupid thing is designed to be a get request
# create model mixin
class TagViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    """manage tags in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    # this is what is called when the ListModelMixin is called (i.e)
    def get_queryset(self):
        """return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by('-name')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class IngredientViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')