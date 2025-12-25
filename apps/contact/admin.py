from django.contrib import admin
from .models import ContactMessage, Resume


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'status', 'created_at', 'is_spam')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('ip_address', 'user_agent', 'referrer', 'honeypot', 'submission_time', 'created_at')
    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'subject', 'message', 'status')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent', 'referrer', 'created_at'),
            'classes': ('collapse',)
        }),
        ('Spam Detection', {
            'fields': ('honeypot', 'submission_time'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_spam', 'mark_as_read', 'mark_as_archived']

    def is_spam(self, obj):
        return obj.is_likely_spam
    is_spam.boolean = True
    is_spam.short_description = 'Spam?'

    @admin.action(description='Mark selected as spam')
    def mark_as_spam(self, request, queryset):
        queryset.update(status=ContactMessage.Status.SPAM)

    @admin.action(description='Mark selected as read')
    def mark_as_read(self, request, queryset):
        queryset.update(status=ContactMessage.Status.READ)

    @admin.action(description='Archive selected')
    def mark_as_archived(self, request, queryset):
        queryset.update(status=ContactMessage.Status.ARCHIVED)


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'download_count', 'created_at')
    list_filter = ('is_active',)
