from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.urls import reverse_lazy

from .models import Dashboard, Widget, Suggestion, DataSource


class DashboardListView(ListView):
    model = Dashboard
    template_name = 'dashboards/dashboard_list.html'
    context_object_name = 'dashboards'

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and getattr(user, 'is_owner', False):
            # Owner sees all dashboards
            return Dashboard.objects.all().select_related('owner')

        if user.is_authenticated:
            # Registered users see public and registered-only dashboards
            return Dashboard.objects.filter(
                visibility__in=[Dashboard.Visibility.PUBLIC, Dashboard.Visibility.REGISTERED]
            ).select_related('owner')

        # Anonymous users see only public dashboards
        return Dashboard.objects.filter(
            visibility=Dashboard.Visibility.PUBLIC
        ).select_related('owner')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_dashboards'] = self.get_queryset().filter(is_featured=True)[:3]
        return context


class DashboardDetailView(DetailView):
    model = Dashboard
    template_name = 'dashboards/dashboard_detail.html'
    context_object_name = 'dashboard'

    def get_queryset(self):
        return Dashboard.objects.prefetch_related('widgets', 'widgets__data_source')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.can_view(self.request.user):
            raise Http404("Dashboard not found")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_edit'] = self.object.can_edit(self.request.user)
        context['can_suggest'] = self.request.user.is_authenticated
        return context


class SuggestionCreateView(LoginRequiredMixin, CreateView):
    model = Suggestion
    template_name = 'dashboards/suggestion_form.html'
    fields = ['suggestion_type', 'title', 'description', 'data']

    def get_dashboard(self):
        return get_object_or_404(Dashboard, slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dashboard'] = self.get_dashboard()
        return context

    def form_valid(self, form):
        form.instance.dashboard = self.get_dashboard()
        form.instance.user = self.request.user
        messages.success(self.request, 'Your suggestion has been submitted. Thank you!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('dashboards:dashboard_detail', kwargs={'slug': self.kwargs['slug']})


def widget_data(request, pk):
    """API endpoint for widget data (for Chart.js)."""
    widget = get_object_or_404(Widget, pk=pk)

    # Check access
    if not widget.dashboard.can_view(request.user):
        return JsonResponse({'error': 'Access denied'}, status=403)

    data = widget.get_chart_data()
    return JsonResponse(data)


def dashboard_htmx_refresh(request, slug):
    """HTMX endpoint to refresh dashboard widgets."""
    dashboard = get_object_or_404(Dashboard, slug=slug)

    if not dashboard.can_view(request.user):
        return JsonResponse({'error': 'Access denied'}, status=403)

    return render(request, 'dashboards/partials/widgets.html', {
        'dashboard': dashboard,
        'widgets': dashboard.widgets.all()
    })
