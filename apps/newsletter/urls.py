from django.urls import path

from . import views

app_name = "newsletter"

urlpatterns = [
    path("suscribir/", views.subscribe_view, name="subscribe"),
    path("baja/<str:token>/", views.unsubscribe_view, name="unsubscribe"),
]
