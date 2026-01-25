from django import forms
from django.conf import settings
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """Contact form with spam protection."""

    # Honeypot field - should be hidden and left empty
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'hidden',
            'tabindex': '-1',
            'autocomplete': 'off'
        })
    )

    # Hidden timestamp field for timing check
    form_time = forms.FloatField(widget=forms.HiddenInput(), required=False)

    # reCAPTCHA v3 field (invisible)
    captcha = ReCaptchaField(widget=ReCaptchaV3())

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'Your name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'your@email.com'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'Subject'
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
                'placeholder': 'Your message...',
                'rows': 5
            }),
        }

    def clean(self):
        cleaned_data = super().clean()

        # Check honeypot
        if cleaned_data.get('website'):
            raise forms.ValidationError('Spam detected.')

        return cleaned_data

    def save(self, commit=True, **kwargs):
        instance = super().save(commit=False)

        # Store honeypot value
        instance.honeypot = self.cleaned_data.get('website', '')

        # Calculate submission time
        import time
        form_time = self.cleaned_data.get('form_time', 0)
        if form_time:
            instance.submission_time = time.time() - form_time

        # Store additional metadata from kwargs
        instance.ip_address = kwargs.get('ip_address')
        instance.user_agent = kwargs.get('user_agent', '')[:500]
        instance.referrer = kwargs.get('referrer', '')[:200]

        # Auto-mark as spam if detected
        if instance.is_likely_spam:
            instance.status = ContactMessage.Status.SPAM

        if commit:
            instance.save()

        return instance
