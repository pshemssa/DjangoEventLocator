from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.text import slugify


class EventCategory(models.Model):
    """Model for event categories."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = _('event category')
        verbose_name_plural = _('event categories')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category-detail', kwargs={'slug': self.slug})


class EventTag(models.Model):
    """Model for event tags."""
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    """Model for events."""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, default='')
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Location fields
    location_name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Capacity and registration
    capacity = models.PositiveIntegerField(null=True, blank=True)
    registration_deadline = models.DateTimeField(null=True, blank=True)
    is_free = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Status and visibility
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    # Media
    main_image = models.ImageField(upload_to='event_images/', null=True, blank=True)

    # Relationships
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='events_created'
    )
    category = models.ForeignKey(
        EventCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='events'
    )
    tags = models.ManyToManyField(
        EventTag,
        related_name='events',
        blank=True
    )
    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='EventAttendee',
        related_name='events_attending'
    )
    favorites = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='favorite_events',
        blank=True
    )

    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['start_date', 'city', 'is_published']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate the initial slug
            self.slug = slugify(self.title)
            # Check if the slug exists
            counter = 1
            while Event.objects.filter(slug=self.slug).exists():
                self.slug = f"{slugify(self.title)}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('events:event-detail', kwargs={'slug': self.slug})

    @property
    def is_past(self):
        return self.end_date < timezone.now()

    @property
    def is_ongoing(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date


class EventAttendee(models.Model):
    """Model for event attendance tracking."""
    STATUS_CHOICES = [
        ('registered', _('Registered')),
        ('attended', _('Attended')),
        ('cancelled', _('Cancelled')),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered')
    registration_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['event', 'user']


class Comment(models.Model):
    """Model for event comments."""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.user.username} on {self.event.title}'


class Review(models.Model):
    """Model for event reviews."""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        unique_together = ['event', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f'Review by {self.user.username} on {self.event.title}'
