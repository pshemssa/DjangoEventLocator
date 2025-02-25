from django import forms
from django.utils import timezone
from .models import Event, Comment, Review, EventAttendee


class EventForm(forms.ModelForm):
    """Form for creating and updating events."""
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'start_date', 'end_date',
            'location_name', 'address', 'city', 'country',
            'latitude', 'longitude', 'capacity', 'registration_deadline',
            'is_free', 'price', 'category', 'tags', 'main_image',
            'is_published'
        ]
        widgets = {
            'start_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'end_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'registration_deadline': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'description': forms.Textarea(attrs={'rows': 5}),
            'tags': forms.CheckboxSelectMultiple(),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        registration_deadline = cleaned_data.get('registration_deadline')
        is_free = cleaned_data.get('is_free')
        price = cleaned_data.get('price')

        if start_date and end_date:
            if start_date >= end_date:
                raise forms.ValidationError(
                    "End date must be after start date."
                )
            if start_date < timezone.now():
                raise forms.ValidationError(
                    "Start date cannot be in the past."
                )

        if registration_deadline:
            if registration_deadline >= start_date:
                raise forms.ValidationError(
                    "Registration deadline must be before event start date."
                )

        if not is_free and not price:
            raise forms.ValidationError(
                "Price is required for paid events."
            )

        return cleaned_data


class CommentForm(forms.ModelForm):
    """Form for adding comments to events."""
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Write your comment here...'
                }
            )
        }

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content.strip()) < 10:
            raise forms.ValidationError(
                "Comment must be at least 10 characters long."
            )
        return content


class ReviewForm(forms.ModelForm):
    """Form for submitting event reviews."""
    class Meta:
        model = Review
        fields = ['rating', 'content']
        widgets = {
            'rating': forms.NumberInput(
                attrs={
                    'min': '1',
                    'max': '5',
                    'class': 'rating-input'
                }
            ),
            'content': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder': 'Write your review here...'
                }
            )
        }

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content.strip()) < 20:
            raise forms.ValidationError(
                "Review must be at least 20 characters long."
            )
        return content


class EventAttendeeForm(forms.ModelForm):
    """Form for managing event attendees."""
    status = forms.ChoiceField(
        choices=EventAttendee.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = EventAttendee
        fields = ['event', 'user', 'status']

    def clean_status(self):
        status = self.cleaned_data.get('status')
        if status not in dict(EventAttendee.STATUS_CHOICES):
            raise forms.ValidationError("Invalid status selection.")
        return status
