from django.urls import path
from . import views

app_name = 'dashboards'

urlpatterns = [
    path('', views.DashboardListView.as_view(), name='dashboard_list'),
    path('<slug:slug>/', views.DashboardDetailView.as_view(), name='dashboard_detail'),
    path('<slug:slug>/suggest/', views.SuggestionCreateView.as_view(), name='suggestion_create'),
    path('<slug:slug>/refresh/', views.dashboard_htmx_refresh, name='dashboard_refresh'),
    path('api/widget/<int:pk>/data/', views.widget_data, name='widget_data'),
]
