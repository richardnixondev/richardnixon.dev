from django.contrib import admin
from .models import Technology, Project, ProjectImage


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'color', 'project_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def project_count(self, obj):
        return obj.projects.count()
    project_count.short_description = 'Projects'


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'is_featured', 'order', 'start_date', 'end_date')
    list_filter = ('status', 'is_featured', 'technologies')
    search_fields = ('title', 'description', 'tagline')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('technologies',)
    inlines = [ProjectImageInline]

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'tagline', 'description')
        }),
        ('Media', {
            'fields': ('featured_image', 'thumbnail')
        }),
        ('Technologies', {
            'fields': ('technologies',)
        }),
        ('Links', {
            'fields': ('live_url', 'github_url', 'documentation_url')
        }),
        ('Display', {
            'fields': ('is_featured', 'order', 'status')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date'),
            'classes': ('collapse',)
        }),
    )
