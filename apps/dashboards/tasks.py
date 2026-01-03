"""Celery tasks for dashboards app."""
import csv
import json
import logging
from datetime import datetime
from io import StringIO

import requests
from celery import shared_task
from django.utils import timezone

from .models import DataSource, DataPoint

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def sync_data_source(self, source_id):
    """Sync data from a data source."""
    try:
        source = DataSource.objects.get(pk=source_id)
    except DataSource.DoesNotExist:
        logger.error(f"DataSource {source_id} not found")
        return

    try:
        if source.source_type == DataSource.Type.API:
            sync_api_source(source)
        elif source.source_type == DataSource.Type.CSV:
            sync_csv_source(source)
        elif source.source_type == DataSource.Type.SCRAPE:
            sync_scrape_source(source)

        source.last_sync = timezone.now()
        source.save(update_fields=['last_sync'])
        logger.info(f"Successfully synced DataSource {source_id}")

    except Exception as exc:
        logger.error(f"Error syncing DataSource {source_id}: {exc}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


def sync_api_source(source):
    """Fetch data from an external API."""
    config = source.config
    url = config.get('url')
    method = config.get('method', 'GET')
    headers = config.get('headers', {})
    params = config.get('params', {})

    if not url:
        logger.error(f"No URL configured for DataSource {source.id}")
        return

    response = requests.request(method, url, headers=headers, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    # Extract data based on config
    data_path = config.get('data_path', '')
    if data_path:
        for key in data_path.split('.'):
            data = data.get(key, {})

    # Handle list or single item
    if isinstance(data, list):
        for item in data:
            create_data_point(source, item, config)
    else:
        create_data_point(source, data, config)


def sync_csv_source(source):
    """Import data from a CSV file."""
    if not source.csv_file:
        logger.error(f"No CSV file for DataSource {source.id}")
        return

    content = source.csv_file.read().decode('utf-8')
    reader = csv.DictReader(StringIO(content))

    config = source.config
    timestamp_field = config.get('timestamp_field', 'date')
    timestamp_format = config.get('timestamp_format', '%Y-%m-%d')

    # Clear existing data points if configured
    if config.get('clear_on_import', False):
        source.data_points.all().delete()

    for row in reader:
        timestamp_str = row.pop(timestamp_field, None)
        if timestamp_str:
            try:
                timestamp = datetime.strptime(timestamp_str, timestamp_format)
                timestamp = timezone.make_aware(timestamp)
            except ValueError:
                timestamp = timezone.now()
        else:
            timestamp = timezone.now()

        DataPoint.objects.create(
            source=source,
            timestamp=timestamp,
            data=row
        )


def sync_scrape_source(source):
    """Scrape data from a webpage."""
    config = source.config
    url = config.get('url')

    if not url:
        logger.error(f"No URL configured for DataSource {source.id}")
        return

    # Basic scraping - can be extended with BeautifulSoup
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    # Store raw HTML or extracted data
    selector = config.get('selector')
    if selector:
        # Would need BeautifulSoup here for actual scraping
        # For now, just store raw content
        data = {'raw': response.text[:10000]}
    else:
        data = {'raw': response.text[:10000]}

    DataPoint.objects.create(
        source=source,
        timestamp=timezone.now(),
        data=data
    )


def create_data_point(source, item, config):
    """Create a data point from API response item."""
    timestamp_field = config.get('timestamp_field', 'timestamp')
    timestamp_format = config.get('timestamp_format', '%Y-%m-%dT%H:%M:%S')

    timestamp_str = item.get(timestamp_field)
    if timestamp_str:
        try:
            timestamp = datetime.strptime(timestamp_str[:19], timestamp_format)
            timestamp = timezone.make_aware(timestamp)
        except ValueError:
            timestamp = timezone.now()
    else:
        timestamp = timezone.now()

    # Check for duplicates
    value_field = config.get('value_field', 'value')
    existing = DataPoint.objects.filter(
        source=source,
        timestamp=timestamp
    ).first()

    if existing:
        existing.data = item
        existing.save()
    else:
        DataPoint.objects.create(
            source=source,
            timestamp=timestamp,
            data=item
        )


@shared_task
def sync_all_enabled_sources():
    """Periodic task to sync all enabled data sources."""
    sources = DataSource.objects.filter(sync_enabled=True)

    for source in sources:
        # Check if enough time has passed since last sync
        if source.last_sync:
            elapsed = (timezone.now() - source.last_sync).total_seconds()
            if elapsed < source.sync_interval:
                continue

        sync_data_source.delay(source.id)


@shared_task
def cleanup_old_data_points(days=90):
    """Remove data points older than specified days."""
    cutoff = timezone.now() - timezone.timedelta(days=days)
    deleted, _ = DataPoint.objects.filter(timestamp__lt=cutoff).delete()
    logger.info(f"Deleted {deleted} old data points")
