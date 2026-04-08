import pytest

from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
class TestContactViews:
    def test_contact_form_get_returns_200(self):
        client = Client()
        response = client.get(reverse("contact:contact"))
        assert response.status_code == 200
