from apps.media_content.models import VideoPost

from .models import Post


def get_published_content(content_type=None, category_slug=None, tag_slug=None):
    posts = Post.objects.published().select_related("category").prefetch_related("tags")
    videos = VideoPost.objects.published().select_related("category")

    if category_slug:
        posts = posts.filter(category__slug=category_slug)
        videos = videos.filter(category__slug=category_slug)
    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)
        videos = VideoPost.objects.none()

    items = []
    for post in posts:
        items.append(
            {
                "type": "article",
                "obj": post,
                "published_at": post.published_at,
            }
        )
    for video in videos:
        items.append(
            {
                "type": "video",
                "obj": video,
                "published_at": video.published_at,
            }
        )

    items.sort(key=lambda item: item["published_at"], reverse=True)

    if content_type == "articulos":
        items = [item for item in items if item["type"] == "article"]
    elif content_type == "videos":
        items = [item for item in items if item["type"] == "video"]

    return items
