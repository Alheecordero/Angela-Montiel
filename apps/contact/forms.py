from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Su nombre",
                "autocomplete": "name",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-input",
                "placeholder": "correo@ejemplo.cl",
                "autocomplete": "email",
                "inputmode": "email",
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "+56 9 ...",
                "autocomplete": "tel",
                "inputmode": "tel",
            }),
            "subject": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "Asunto de la consulta",
                "autocomplete": "off",
            }),
            "message": forms.Textarea(
                attrs={
                    "class": "form-input form-textarea",
                    "placeholder": "Cuénteme el contexto de su consulta...",
                    "rows": 5,
                }
            ),
        }
        labels = {
            "name": "Nombre completo",
            "email": "Correo electrónico",
            "phone": "Teléfono (opcional)",
            "subject": "Asunto",
            "message": "Mensaje",
        }

    def clean_website(self):
        value = self.cleaned_data.get("website", "")
        if value:
            raise forms.ValidationError("No se pudo enviar el formulario.")
        return value
