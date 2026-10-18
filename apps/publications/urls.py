from django.urls import path

from . import views

app_name = "publications"

urlpatterns = [
    path("publicaciones", views.PublicationListView.as_view(), name="list"),
    path("publicaciones/<slug:slug>", views.PublicationDetailView.as_view(), name="detail"),
]
