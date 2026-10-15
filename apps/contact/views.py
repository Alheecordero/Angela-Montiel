from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import ContactForm

CONTACT_RATE_LIMIT_KEY = "contact_last_submit"
CONTACT_RATE_LIMIT_SECONDS = 60


def _get_client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


@require_http_methods(["GET", "POST"])
def contact_view(request):
    if request.method == "POST":
        last_submit = request.session.get(CONTACT_RATE_LIMIT_KEY)
        if last_submit:
            from django.utils import timezone

            elapsed = (timezone.now() - last_submit).total_seconds()
            if elapsed < CONTACT_RATE_LIMIT_SECONDS:
                messages.error(
                    request,
                    "Por favor espere un momento antes de enviar otro mensaje.",
                )
                return redirect("contact:contact")

        form = ContactForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.ip_address = _get_client_ip(request)
            message.save()

            from django.utils import timezone

            request.session[CONTACT_RATE_LIMIT_KEY] = timezone.now()
            messages.success(
                request,
                "Su mensaje fue enviado correctamente. Nos pondremos en contacto pronto.",
            )
            return redirect("contact:contact")
    else:
        form = ContactForm()

    return render(request, "contact/contact.html", {"form": form})
