from django.urls import path
from . import views

app_name = 'contact'

urlpatterns = [
    path('', views.ContactView.as_view(), name='contact'),
    path('resume/', views.ResumeDownloadView.as_view(), name='resume_download'),
]
