from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget

from .models import Post


class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = "__all__"
        widgets = {
            "content": CKEditor5Widget(attrs={"class": "django_ckeditor_5"}, config_name="default"),
        }
