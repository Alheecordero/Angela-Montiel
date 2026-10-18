from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("sobre-mi", views.AboutView.as_view(), name="about"),
    path("politica-de-privacidad", views.LegalPageView.as_view(), {"slug": "politica-de-privacidad"}, name="privacy"),
    path("terminos-de-uso", views.LegalPageView.as_view(), {"slug": "terminos-de-uso"}, name="terms"),
]
