import pytest

from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
class TestBlogViews:
    def test_home_returns_200(self):
        client = Client()
        response = client.get(reverse("blog:home"))
        assert response.status_code == 200

    def test_post_list_returns_200(self):
        client = Client()
        response = client.get(reverse("blog:post_list"))
        assert response.status_code == 200

    def test_rss_feed_returns_200(self):
        client = Client()
        response = client.get(reverse("blog:feed"))
        assert response.status_code == 200
        assert "application/rss+xml" in response["Content-Type"]


@pytest.mark.django_db
class TestHealthEndpoint:
    def test_health_returns_200(self):
        client = Client()
        response = client.get("/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["db"] is True
