from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        help_text=_('Required. Enter a valid email address.'),
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('This email address is already in use.'))
        return email

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('bio', 'location', 'birth_date', 'profile_picture', 'phone_number',
                 'website', 'facebook', 'twitter', 'instagram', 'linkedin')
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }