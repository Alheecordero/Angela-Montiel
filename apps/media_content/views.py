from django.http import Http404
from django.views.generic import DetailView, ListView

from .models import VideoPost


class VideoListView(ListView):
    model = VideoPost
    template_name = "media_content/video_list.html"
    context_object_name = "videos"
    paginate_by = 9

    def get_queryset(self):
        return VideoPost.objects.published().select_related("category")


class VideoDetailView(DetailView):
    model = VideoPost
    template_name = "media_content/video_detail.html"
    context_object_name = "video"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return VideoPost.objects.select_related("category")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.is_published and not self.request.user.is_staff:
            raise Http404()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["related_videos"] = (
            VideoPost.objects.published().exclude(pk=self.object.pk)[:3]
        )
        return context
