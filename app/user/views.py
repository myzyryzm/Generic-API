from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from user.serializers import UserSerializer, AuthTokenSerializer

class CreateUserView(generics.CreateAPIView):
    """create a new user in the system"""
    serializer_class = UserSerializer

class CreateTokenView(ObtainAuthToken):
    """create a new auth token for user"""    
    serializer_class = AuthTokenSerializer
    # all this stupid fucking shit does (this dude cant teach for shit) allows us to see this stupdia;lsdf,mn
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    # typically with api view it would link 2 item and u would get the objects for that; instead we gonna just retrieve the authenticated logged in user
    def get_object(self):
        # b/c we have the authentication classes we can just grab the user form the request
        return self.request.user