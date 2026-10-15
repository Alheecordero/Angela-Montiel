from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import NewsletterForm
from .models import Subscriber


@require_http_methods(["POST"])
def subscribe_view(request):
    form = NewsletterForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data["email"]
        subscriber, created = Subscriber.objects.get_or_create(email=email)
        if not created and not subscriber.is_active:
            subscriber.is_active = True
            subscriber.save(update_fields=["is_active"])
        messages.success(request, "¡Gracias por suscribirse al newsletter!")
    else:
        for error in form.errors.get("email", []):
            messages.error(request, error)

    next_url = request.POST.get("next", request.META.get("HTTP_REFERER", "/"))
    return redirect(next_url or "/")


@require_http_methods(["GET"])
def unsubscribe_view(request, token):
    subscriber = get_object_or_404(Subscriber, unsubscribe_token=token)
    subscriber.is_active = False
    subscriber.save(update_fields=["is_active"])
    return render(request, "newsletter/unsubscribe.html", {"subscriber": subscriber})
