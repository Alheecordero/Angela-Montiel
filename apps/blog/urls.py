from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.BlogListView.as_view(), name="post_list"),
    path("categoria/<slug:category_slug>/", views.BlogListView.as_view(), name="post_list_by_category"),
    path("etiqueta/<slug:tag_slug>/", views.BlogListView.as_view(), name="post_list_by_tag"),
    path("<slug:slug>/", views.ContentDetailView.as_view(), name="post_detail"),
]
