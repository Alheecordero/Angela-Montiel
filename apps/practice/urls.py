from django.urls import path

from . import views

app_name = "practice"

# Áreas y figuras comparten el primer nivel de la URL (capítulo 3).
# `area` y `figure` apuntan a la misma vista; existen como nombres distintos
# para que reverse() sea explícito en los modelos.
urlpatterns = [
    path("<slug:slug>", views.area_view, name="area"),
    path("<slug:slug>", views.figure_view, name="figure"),
]
