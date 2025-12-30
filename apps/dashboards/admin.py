from django.contrib import admin
from .models import Dashboard, DataSource, DataPoint, Widget, Suggestion


class WidgetInline(admin.TabularInline):
    model = Widget
    extra = 1
    fields = ('title', 'widget_type', 'data_source', 'order', 'width')


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'visibility', 'is_featured', 'widget_count', 'updated_at')
    list_filter = ('visibility', 'is_featured', 'created_at')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('owner',)
    inlines = [WidgetInline]

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description')
        }),
        ('Access', {
            'fields': ('owner', 'visibility')
        }),
        ('Display', {
            'fields': ('columns', 'is_featured')
        }),
    )

    def widget_count(self, obj):
        return obj.widgets.count()
    widget_count.short_description = 'Widgets'


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'source_type', 'owner', 'sync_enabled', 'last_sync')
    list_filter = ('source_type', 'sync_enabled')
    search_fields = ('name',)
    raw_id_fields = ('owner',)

    fieldsets = (
        (None, {
            'fields': ('name', 'source_type', 'owner')
        }),
        ('Configuration', {
            'fields': ('config', 'csv_file')
        }),
        ('Sync Settings', {
            'fields': ('sync_enabled', 'sync_interval', 'last_sync'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DataPoint)
class DataPointAdmin(admin.ModelAdmin):
    list_display = ('source', 'timestamp', 'data_preview')
    list_filter = ('source', 'timestamp')
    search_fields = ('source__name',)
    date_hierarchy = 'timestamp'
    raw_id_fields = ('source',)

    def data_preview(self, obj):
        data_str = str(obj.data)
        return data_str[:50] + '...' if len(data_str) > 50 else data_str
    data_preview.short_description = 'Data'


@admin.register(Widget)
class WidgetAdmin(admin.ModelAdmin):
    list_display = ('title', 'dashboard', 'widget_type', 'data_source', 'order')
    list_filter = ('widget_type', 'dashboard')
    search_fields = ('title', 'dashboard__title')
    raw_id_fields = ('dashboard', 'data_source')

    fieldsets = (
        (None, {
            'fields': ('dashboard', 'title', 'widget_type')
        }),
        ('Data', {
            'fields': ('data_source', 'config', 'static_data')
        }),
        ('Layout', {
            'fields': ('order', 'width')
        }),
    )


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'dashboard', 'user', 'suggestion_type', 'status', 'created_at')
    list_filter = ('status', 'suggestion_type', 'created_at')
    search_fields = ('title', 'description')
    raw_id_fields = ('dashboard', 'user')

    fieldsets = (
        (None, {
            'fields': ('dashboard', 'user', 'suggestion_type', 'title', 'description')
        }),
        ('Data', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
        ('Review', {
            'fields': ('status', 'admin_notes')
        }),
    )

    actions = ['approve_suggestions', 'reject_suggestions']

    @admin.action(description='Approve selected suggestions')
    def approve_suggestions(self, request, queryset):
        queryset.update(status=Suggestion.Status.APPROVED)

    @admin.action(description='Reject selected suggestions')
    def reject_suggestions(self, request, queryset):
        queryset.update(status=Suggestion.Status.REJECTED)
