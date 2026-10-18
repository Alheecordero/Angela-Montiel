from django import forms

CONSENT_TEXT = "Acepto recibir el boletín y el tratamiento de mi correo según la política de privacidad."


class NewsletterForm(forms.Form):
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(
            attrs={
                "class": "form-input newsletter-input",
                "placeholder": "tu@empresa.cl",
                "autocomplete": "email",
                "id": "correo-pub",
            }
        ),
    )
    consent = forms.BooleanField(
        label=CONSENT_TEXT,
        required=True,
        error_messages={"required": "Para suscribirte debes aceptar el tratamiento de tu correo."},
        widget=forms.CheckboxInput(attrs={"id": "consentimiento-pub"}),
    )

    def clean_email(self):
        return self.cleaned_data["email"].lower().strip()
