from django import forms

from .models import Subscriber


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ["email"]
        widgets = {
            "email": forms.EmailInput(
                attrs={"class": "form-input newsletter-input", "placeholder": "Su correo electrónico"}
            ),
        }
        labels = {"email": "Correo electrónico"}

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        existing = Subscriber.objects.filter(email=email).first()
        if existing and existing.is_active:
            raise forms.ValidationError("Este correo ya está suscrito.")
        return email
