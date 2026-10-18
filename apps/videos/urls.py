from django.urls import path

from . import views

app_name = "videos"

urlpatterns = [
    path("videos", views.VideoListView.as_view(), name="list"),
    path("videos/<slug:slug>", views.VideoListView.as_view(), name="detail"),
]
