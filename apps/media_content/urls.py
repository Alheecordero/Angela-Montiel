from django.urls import path

from . import views

app_name = "media_content"

urlpatterns = [
    path("", views.VideoListView.as_view(), name="video_list"),
    path("<slug:slug>/", views.VideoDetailView.as_view(), name="video_detail"),
]
