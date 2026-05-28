from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from support.models import SupportTicket
from django.core.mail import send_mail
from django.conf import settings

@login_required
def suporte_view(request):
    if request.method == "POST":
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()
        errors = {}
        if not subject:
            errors["subject_error"] = "Este campo é obrigatório."
        elif len(subject) > 255:
            errors["subject_error"] = "O assunto deve ter no máximo 255 caracteres."
        if not message:
            errors["message_error"] = "Este campo é obrigatório."
        if errors:
            return render(request, "support/suporte.html", errors)
        ticket = SupportTicket.objects.create(user=request.user, subject=subject, message=message)
        try:
            send_mail(
                subject=f"[Suporte] {subject}",
                message=f"Ticket #{ticket.id}\nUsuário: {request.user.id}\nE-mail: {request.user.email}\n\nMensagem:\n{message}",
                from_email=None,
                recipient_list=[getattr(settings, "SUPPORT_EMAIL", "support@hipersaber.local")],
            )
        except Exception:
            pass
        return render(request, "support/suporte.html", {"success_message": True})
    return render(request, "support/suporte.html")

# Create your views here.
