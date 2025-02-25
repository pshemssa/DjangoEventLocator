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
            return redirect('profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Your profile has been updated successfully!'))
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    context = {
        'form': form,
        'events_created': request.user.get_events_created(),
        'events_attending': request.user.get_events_attending(),
        'favorite_events': request.user.get_favorite_events(),
    }
    return render(request, 'users/profile.html', context)
