from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    # Event CRUD
    path('', views.EventListView.as_view(), name='event-list'),
    path('new/', views.EventCreateView.as_view(), name='event-create'),
    path('<slug:slug>/', views.EventDetailView.as_view(), name='event-detail'),
    path('<slug:slug>/edit/', views.EventUpdateView.as_view(), name='event-update'),
    path('<slug:slug>/delete/', views.EventDeleteView.as_view(), name='event-delete'),

    # Event actions
    path('<slug:slug>/favorite/', views.toggle_favorite, name='event-favorite'),
    path('<slug:slug>/attend/', views.toggle_attendance, name='event-attend'),

    # Categories and tags
    path('category/<slug:slug>/', views.EventListView.as_view(), name='category-detail'),
    path('tag/<slug:slug>/', views.EventListView.as_view(), name='tag-detail'),

    # User-specific views
    path('my-events/', views.UserEventsListView.as_view(), name='user-events'),
    path('my-favorites/', views.UserFavoritesListView.as_view(), name='user-favorites'),
    path('attending/', views.UserAttendingListView.as_view(), name='user-attending'),
]
