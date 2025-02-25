from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.views.generic.edit import FormMixin
from .models import Event, EventCategory, EventTag, Comment, Review
from .forms import EventForm, CommentForm, ReviewForm


class EventListView(ListView):
    """Display list of events with search and filtering."""
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 12
    ordering = ['-start_date']

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_published=True)

        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(location_name__icontains=search_query) |
                Q(city__icontains=search_query)
            )

        # Category filter
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)

        # Tag filter
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__slug=tag)

        # Date filter
        date_filter = self.request.GET.get('date')
        if date_filter == 'upcoming':
            queryset = queryset.filter(end_date__gte=timezone.now())
        elif date_filter == 'past':
            queryset = queryset.filter(end_date__lt=timezone.now())

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = EventCategory.objects.all()
        context['tags'] = EventTag.objects.all()
        return context


class EventDetailView(FormMixin, DetailView):
    """Display event details with comments and reviews."""
    model = Event
    template_name = 'events/event_detail.html'
    form_class = CommentForm
    lookup_field = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(is_approved=True)
        context['reviews'] = self.object.reviews.filter(is_approved=True)
        if self.request.user.is_authenticated:
            context['user_review'] = self.object.reviews.filter(user=self.request.user).first()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(
                request.get_full_path(),
                login_url=reverse('users:login')
            )
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.event = self.object
        comment.user = self.request.user
        comment.save()
        messages.success(self.request, 'Your comment has been posted.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('events:event-detail', kwargs={'slug': self.object.slug})


class EventCreateView(LoginRequiredMixin, CreateView):
    """Create new event."""
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        messages.success(self.request, 'Event created successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('events:event-detail', kwargs={'slug': self.object.slug})


class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update existing event."""
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    lookup_field = 'slug'

    def test_func(self):
        event = self.get_object()
        return self.request.user == event.organizer

    def form_valid(self, form):
        messages.success(self.request, 'Event updated successfully!')
        return super().form_valid(form)


class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete existing event."""
    model = Event
    success_url = reverse_lazy('events:event-list')
    template_name = 'events/event_confirm_delete.html'
    lookup_field = 'slug'

    def test_func(self):
        event = self.get_object()
        return self.request.user == event.organizer

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Event deleted successfully!')
        return super().delete(request, *args, **kwargs)


def toggle_favorite(request, slug):
    """Toggle event favorite status for current user."""
    if not request.user.is_authenticated:
        return redirect('users:login')

    event = get_object_or_404(Event, slug=slug)
    if event in request.user.favorite_events.all():
        request.user.favorite_events.remove(event)
        messages.success(request, 'Event removed from favorites.')
    else:
        request.user.favorite_events.add(event)
        messages.success(request, 'Event added to favorites.')

    return redirect('events:event-detail', slug=slug)


def toggle_attendance(request, slug):
    """Toggle event attendance status for current user."""
    if not request.user.is_authenticated:
        return redirect('users:login')

    event = get_object_or_404(Event, slug=slug)
    attendance = event.eventattendee_set.filter(user=request.user).first()

    if attendance:
        if attendance.status == 'cancelled':
            attendance.status = 'registered'
            messages.success(request, 'You are now registered for this event.')
        else:
            attendance.status = 'cancelled'
            messages.success(request, 'Your registration has been cancelled.')
        attendance.save()
    else:
        EventAttendee.objects.create(
            event=event,
            user=request.user,
            status='registered'
        )
        messages.success(request, 'You are now registered for this event.')

    return redirect('events:event-detail', slug=slug)


class UserEventsListView(LoginRequiredMixin, ListView):
    """Display list of events created by the current user."""
    model = Event
    template_name = 'events/user_events_list.html'
    context_object_name = 'events'
    paginate_by = 12

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user).order_by('-start_date')


class UserFavoritesListView(LoginRequiredMixin, ListView):
    """Display list of events favorited by the current user."""
    model = Event
    template_name = 'events/user_favorites_list.html'
    context_object_name = 'events'
    paginate_by = 12

    def get_queryset(self):
        return self.request.user.favorite_events.all().order_by('-start_date')


class UserAttendingListView(LoginRequiredMixin, ListView):
    """Display list of events the user is attending."""
    model = Event
    template_name = 'events/user_attending_list.html'
    context_object_name = 'events'
    paginate_by = 12

    def get_queryset(self):
        return Event.objects.filter(
            eventattendee__user=self.request.user,
            eventattendee__status='registered'
        ).order_by('-start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['past_events'] = Event.objects.filter(
            eventattendee__user=self.request.user,
            eventattendee__status='attended',
            end_date__lt=timezone.now()
        ).order_by('-start_date')
        return context
