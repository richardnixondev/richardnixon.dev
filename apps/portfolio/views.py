from django.views.generic import ListView, DetailView
from .models import Project, Technology


class ProjectListView(ListView):
    model = Project
    template_name = 'portfolio/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        queryset = Project.objects.filter(status=Project.Status.PUBLISHED)

        # Filter by technology
        tech = self.request.GET.get('tech')
        if tech:
            queryset = queryset.filter(technologies__slug=tech)

        return queryset.prefetch_related('technologies')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['technologies'] = Technology.objects.all()
        context['active_tech'] = self.request.GET.get('tech', '')
        context['featured_projects'] = Project.objects.filter(
            status=Project.Status.PUBLISHED,
            is_featured=True
        ).prefetch_related('technologies')[:3]
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'portfolio/project_detail.html'
    context_object_name = 'project'

    def get_queryset(self):
        return Project.objects.filter(
            status=Project.Status.PUBLISHED
        ).prefetch_related('technologies', 'images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get related projects by technology
        project_techs = self.object.technologies.all()
        context['related_projects'] = Project.objects.filter(
            technologies__in=project_techs,
            status=Project.Status.PUBLISHED
        ).exclude(pk=self.object.pk).distinct()[:3]
        return context
