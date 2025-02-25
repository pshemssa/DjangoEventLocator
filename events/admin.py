from django.contrib import admin
from django.utils.html import format_html
from .models import EventCategory, EventTag, Event, EventAttendee, Comment, Review
from .forms import EventAttendeeForm


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')


@admin.register(EventTag)
class EventTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


class EventAttendeeInline(admin.TabularInline):
    model = EventAttendee
    extra = 0
    raw_id_fields = ('user',)


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    raw_id_fields = ('user',)
    readonly_fields = ('created_at',)


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    raw_id_fields = ('user',)
    readonly_fields = ('created_at',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'category', 'start_date', 'end_date',
                   'city', 'is_published', 'is_featured', 'event_status')
    list_filter = ('is_published', 'is_featured', 'category', 'city',
                  'start_date', 'is_free')
    search_fields = ('title', 'description', 'location_name', 'address', 'city')
    raw_id_fields = ('organizer',)
    prepopulated_fields = {}
    date_hierarchy = 'start_date'
    filter_horizontal = ('tags', 'favorites')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [EventAttendeeInline, CommentInline, ReviewInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'organizer', 'category', 'tags')
        }),
        ('Date and Time', {
            'fields': ('start_date', 'end_date', 'registration_deadline')
        }),
        ('Location', {
            'fields': ('location_name', 'address', 'city', 'country',
                      'latitude', 'longitude')
        }),
        ('Capacity and Price', {
            'fields': ('capacity', 'is_free', 'price')
        }),
        ('Status', {
            'fields': ('is_published', 'is_featured')
        }),
        ('Media', {
            'fields': ('main_image',)
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def event_status(self, obj):
        if obj.is_past:
            return format_html('<span style="color: red;">Past</span>')
        elif obj.is_ongoing:
            return format_html('<span style="color: green;">Ongoing</span>')
        return format_html('<span style="color: blue;">Upcoming</span>')
    event_status.short_description = 'Status'


@admin.register(EventAttendee)
class EventAttendeeAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'status', 'registration_date')
    list_filter = ('status', 'registration_date')
    search_fields = ('event__title', 'user__username', 'user__email')
    raw_id_fields = ('event', 'user')
    date_hierarchy = 'registration_date'
    form = EventAttendeeForm


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'content_preview', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('event__title', 'user__username', 'content')
    raw_id_fields = ('event', 'user')
    date_hierarchy = 'created_at'
    actions = ['approve_comments', 'disapprove_comments']

    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = "Approve selected comments"

    def disapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_comments.short_description = "Disapprove selected comments"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'rating', 'content_preview', 'created_at', 'is_approved')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('event__title', 'user__username', 'content')
    raw_id_fields = ('event', 'user')
    date_hierarchy = 'created_at'
    actions = ['approve_reviews', 'disapprove_reviews']

    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = "Approve selected reviews"

    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_reviews.short_description = "Disapprove selected reviews"
