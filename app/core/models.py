from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    #take any extra fields that passed into create_user and pass them into extra_fields
    def create_user(self, email, password=None, **extra_fields):
        """Create and saves a new user"""
        if not email:
            raise ValueError('Users must have an email address')
        # way management commands work is that u can call self.model to access the model it controls
        # normalize_email is part of base user class therefore we call self 2 get access 2 it
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        # using statement is for when you are using multiple databases; not necessary but good practice anyways
        user.save(using=self._db)

        return user
    
    def create_superuser(self, email, password):
        """creates superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user

# give all features that come with user class but allow us to customize
class User(AbstractBaseUser, PermissionsMixin):
    """create a user model with email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    # sets username field 2 b email
    USERNAME_FIELD = 'email'
