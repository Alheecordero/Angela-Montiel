from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.core.models import SiteSettings

from .forms import CONSENT_TEXT, NewsletterForm
from .models import Subscriber


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _send_confirmation(request, subscriber, site):
    confirm_url = site.absolute(f"/boletin/confirmar/{subscriber.confirm_token}")
    unsubscribe_url = site.absolute(f"/boletin/baja/{subscriber.unsubscribe_token}")
    body = (
        "Hola.\n\n"
        "Recibí tu solicitud para recibir el boletín de angelamontiel.cl. "
        "Para confirmarla, abre este enlace.\n\n"
        f"{confirm_url}\n\n"
        "Si no fuiste tú, ignora este correo y no recibirás nada más.\n\n"
        "Ángela Montiel\n"
        f"Darse de baja. {unsubscribe_url}\n"
    )
    send_mail(
        subject="Confirma tu suscripción al boletín de Ángela Montiel",
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[subscriber.email],
        fail_silently=False,
    )


@require_http_methods(["POST"])
def subscribe_view(request):
    site = SiteSettings.load()
    next_url = request.POST.get("next") or "/publicaciones"
    if not site.newsletter_enabled:
        raise Http404()

    form = NewsletterForm(request.POST)
    if not form.is_valid():
        for errors in form.errors.values():
            for error in errors:
                messages.error(request, error)
        return redirect(f"{next_url}#boletin")

    email = form.cleaned_data["email"]
    subscriber, created = Subscriber.objects.get_or_create(email=email)
    if subscriber.is_active:
        messages.info(request, "Ese correo ya recibe el boletín.")
        return redirect(f"{next_url}#boletin")

    subscriber.consent_at = timezone.now()
    subscriber.consent_text = CONSENT_TEXT
    subscriber.consent_ip = _client_ip(request)
    subscriber.save(update_fields=["consent_at", "consent_text", "consent_ip"])
    _send_confirmation(request, subscriber, site)
    messages.success(request, "Te envié un correo para confirmar la suscripción. Revisa tu bandeja de entrada.")
    return redirect(f"{next_url}#boletin")


@require_http_methods(["GET"])
def confirm_view(request, token):
    subscriber = get_object_or_404(Subscriber, confirm_token=token)
    if not subscriber.is_confirmed:
        subscriber.confirm()
    return render(request, "newsletter/confirmed.html", {"subscriber": subscriber, "page_meta": {"title": "Suscripción confirmada | Ángela Montiel", "noindex": True}})


@require_http_methods(["GET"])
def unsubscribe_view(request, token):
    subscriber = get_object_or_404(Subscriber, unsubscribe_token=token)
    subscriber.unsubscribe()
    return render(request, "newsletter/unsubscribe.html", {"subscriber": subscriber, "page_meta": {"title": "Baja del boletín | Ángela Montiel", "noindex": True}})
