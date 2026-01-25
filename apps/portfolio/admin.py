from django.contrib import admin
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from modeltranslation.admin import TranslationAdmin
from .models import Technology, Project, ProjectImage


class ProjectAdminForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        widgets = {
            'description_pt_br': CKEditor5Widget(config_name='default'),
            'description_en': CKEditor5Widget(config_name='default'),
            'description': CKEditor5Widget(config_name='default'),
        }


@admin.register(Technology)
class TechnologyAdmin(TranslationAdmin):
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
class ProjectAdmin(TranslationAdmin):
    form = ProjectAdminForm
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
