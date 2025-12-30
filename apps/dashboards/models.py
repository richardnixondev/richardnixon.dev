from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.text import slugify


class Dashboard(models.Model):
    """A dashboard containing multiple widgets."""

    class Visibility(models.TextChoices):
        PUBLIC = 'public', 'Public'
        PRIVATE = 'private', 'Private (Owner only)'
        REGISTERED = 'registered', 'Registered Users'

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dashboards'
    )
    visibility = models.CharField(max_length=20, choices=Visibility.choices, default=Visibility.PUBLIC)

    # Display settings
    columns = models.IntegerField(default=2, choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4')])
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('dashboards:dashboard_detail', kwargs={'slug': self.slug})

    def can_view(self, user):
        """Check if user can view this dashboard."""
        if self.visibility == self.Visibility.PUBLIC:
            return True
        if not user.is_authenticated:
            return False
        if self.visibility == self.Visibility.REGISTERED:
            return True
        # Private - only owner
        return user == self.owner or getattr(user, 'is_owner', False)

    def can_edit(self, user):
        """Check if user can edit this dashboard."""
        if not user.is_authenticated:
            return False
        return user == self.owner or getattr(user, 'is_owner', False)


class DataSource(models.Model):
    """Data source for dashboard widgets."""

    class Type(models.TextChoices):
        MANUAL = 'manual', 'Manual Entry'
        CSV = 'csv', 'CSV Import'
        API = 'api', 'External API'
        SCRAPE = 'scrape', 'Web Scraping'

    name = models.CharField(max_length=200)
    source_type = models.CharField(max_length=20, choices=Type.choices, default=Type.MANUAL)

    # Configuration (JSON)
    config = models.JSONField(default=dict, blank=True, help_text='Source-specific configuration')

    # For CSV imports
    csv_file = models.FileField(upload_to='dashboards/csv/', blank=True, null=True)

    # Scheduling
    sync_enabled = models.BooleanField(default=False)
    sync_interval = models.IntegerField(default=3600, help_text='Sync interval in seconds')
    last_sync = models.DateTimeField(null=True, blank=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='data_sources'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"


class DataPoint(models.Model):
    """Individual data point from a data source."""
    source = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='data_points')
    timestamp = models.DateTimeField(db_index=True)
    data = models.JSONField(default=dict)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['source', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.source.name} - {self.timestamp}"


class Widget(models.Model):
    """Widget in a dashboard."""

    class Type(models.TextChoices):
        LINE_CHART = 'line', 'Line Chart'
        BAR_CHART = 'bar', 'Bar Chart'
        PIE_CHART = 'pie', 'Pie Chart'
        DOUGHNUT_CHART = 'doughnut', 'Doughnut Chart'
        AREA_CHART = 'area', 'Area Chart'
        NUMBER = 'number', 'Single Number'
        TABLE = 'table', 'Data Table'
        TEXT = 'text', 'Text/Markdown'
        MAP = 'map', 'Map'

    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='widgets')
    title = models.CharField(max_length=200)
    widget_type = models.CharField(max_length=20, choices=Type.choices)

    # Data configuration
    data_source = models.ForeignKey(
        DataSource,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='widgets'
    )

    # Widget configuration (JSON)
    config = models.JSONField(default=dict, blank=True, help_text='Widget-specific configuration')

    # Static data (for manual/text widgets)
    static_data = models.JSONField(default=dict, blank=True)

    # Layout
    order = models.IntegerField(default=0)
    width = models.IntegerField(default=1, choices=[(1, '1 col'), (2, '2 cols'), (3, '3 cols'), (4, '4 cols')])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.title} ({self.get_widget_type_display()})"

    def get_chart_data(self):
        """Get data formatted for Chart.js."""
        if self.data_source:
            data_points = self.data_source.data_points.order_by('timestamp')[:100]
            labels = [dp.timestamp.strftime('%Y-%m-%d') for dp in data_points]
            values = [dp.data.get('value', 0) for dp in data_points]
            return {'labels': labels, 'values': values}
        return self.static_data


class Suggestion(models.Model):
    """User suggestion for a dashboard."""

    class Type(models.TextChoices):
        DATA_UPDATE = 'data', 'Data Update'
        NEW_WIDGET = 'widget', 'New Widget'
        BUG_REPORT = 'bug', 'Bug Report'
        FEATURE = 'feature', 'Feature Request'
        OTHER = 'other', 'Other'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        IMPLEMENTED = 'implemented', 'Implemented'

    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='suggestions')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='suggestions'
    )

    suggestion_type = models.CharField(max_length=20, choices=Type.choices, default=Type.OTHER)
    title = models.CharField(max_length=200)
    description = models.TextField()
    data = models.JSONField(default=dict, blank=True, help_text='Structured data for the suggestion')

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    admin_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
