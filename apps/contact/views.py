import time
from django.shortcuts import render, redirect
from django.views.generic import FormView, View
from django.http import FileResponse, Http404
from django.contrib import messages
from django.urls import reverse_lazy

from .forms import ContactForm
from .models import Resume


class ContactView(FormView):
    template_name = 'contact/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact:contact')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_time'] = time.time()
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial['form_time'] = time.time()
        return initial

    def form_valid(self, form):
        form.save(
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            referrer=self.request.META.get('HTTP_REFERER', '')
        )
        messages.success(self.request, 'Thank you for your message! I will get back to you soon.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return self.request.META.get('REMOTE_ADDR')


class ResumeDownloadView(View):
    def get(self, request):
        resume = Resume.objects.filter(is_active=True).first()
        if not resume:
            raise Http404("Resume not found")

        resume.increment_download()

        response = FileResponse(
            resume.file.open('rb'),
            as_attachment=True,
            filename=f"richard_nixon_resume.pdf"
        )
        return response
