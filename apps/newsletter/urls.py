from django.urls import path

from . import views

app_name = "newsletter"

urlpatterns = [
    path("boletin/suscribir", views.subscribe_view, name="subscribe"),
    path("boletin/confirmar/<str:token>", views.confirm_view, name="confirm"),
    path("boletin/baja/<str:token>", views.unsubscribe_view, name="unsubscribe"),
]
