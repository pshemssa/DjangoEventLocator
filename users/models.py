from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Custom User model for the Event Locator application."""
    email = models.EmailField(_('email address'), unique=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    is_organizer = models.BooleanField(default=False)

    # Additional required fields
    phone_number = models.CharField(max_length=15, blank=True)
    website = models.URLField(max_length=200, blank=True)

    # Social media fields
    facebook = models.URLField(max_length=200, blank=True)
    twitter = models.URLField(max_length=200, blank=True)
    instagram = models.URLField(max_length=200, blank=True)
    linkedin = models.URLField(max_length=200, blank=True)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.get_full_name() or self.username

    def get_events_created(self):
        """Get all events created by this user."""
        return self.events_created.all()

    def get_events_attending(self):
        """Get all events this user is attending."""
        return self.events_attending.all()

    def get_favorite_events(self):
        """Get all events marked as favorite by this user."""
        return self.favorite_events.all()
