import uuid
from django.db import models
from django.conf import settings

# ENUM: Status do Ticket
class TicketStatusChoices(models.TextChoices):
    NOVO = 'novo', 'Novo'
    EM_ANDAMENTO = 'em_andamento', 'Em Andamento'
    RESOLVIDO = 'resolvido', 'Resolvido'


# Modelo: Tickets de Suporte
class SupportTicket(models.Model):
    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True,
        help_text="ID público para ser usado em URLs e APIs."
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # Se o usuário for deletado, mantém o ticket
        null=True,
        related_name='support_tickets',
        help_text="Usuário que abriu o chamado."
    )
    subject = models.CharField(max_length=255, help_text="Assunto do ticket.")
    message = models.TextField(help_text="Descrição detalhada do problema.")
    status = models.CharField(
        max_length=20,
        choices=TicketStatusChoices.choices,
        default=TicketStatusChoices.NOVO,
        help_text="Status atual do ticket."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True, help_text="Data em que o ticket foi marcado como resolvido.")

    class Meta:
        verbose_name = 'Ticket de Suporte'
        verbose_name_plural = 'Tickets de Suporte'
        ordering = ['-created_at'] # Ordena pelos mais novos primeiro

    def __str__(self):
        return f'Ticket #{self.id} - {self.subject}'