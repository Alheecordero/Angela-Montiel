from django.urls import path

from . import views

app_name = "resources"

urlpatterns = [
    path("recursos", views.ResourcesView.as_view(), name="index"),
]
