from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from .forms import UserRegistrationForm, UserProfileForm

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _('Your account has been created successfully!'))
            return redirect('users:profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request, username=None):
    if username is None:
        user = request.user
        if request.method == 'POST':
            form = UserProfileForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, _('Your profile has been updated successfully!'))
                return redirect('users:profile')
        else:
            form = UserProfileForm(instance=user)
    else:
        from django.shortcuts import get_object_or_404
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = get_object_or_404(User, username=username)
        form = None

    context = {
        'profile_user': user,
        'form': form,
        'events_created': user.get_events_created(),
        'events_attending': user.get_events_attending(),
        'favorite_events': user.get_favorite_events(),
        'is_own_profile': user == request.user
    }
    return render(request, 'users/profile.html', context)
