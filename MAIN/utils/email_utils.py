# MAIN/utils/email_utils.py
"""Utilitários para envio de e-mail do PIEVDCS."""

from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()


def enviar_email_grupo(grupo_nome: str, assunto: str, mensagem: str) -> int:
    """
    Envia e-mail para todos os usuários ativos de um grupo.

    Retorna o número de usuários notificados.
    """
    try:
        grupo = Group.objects.get(name=grupo_nome)
    except Group.DoesNotExist:
        return 0

    destinatarios = list(
        User.objects.filter(
            groups=grupo,
            is_active=True,
            email__isnull=False,
        ).exclude(email='')
        .values_list('email', flat=True)
    )

    if not destinatarios:
        return 0

    send_mail(
        subject=assunto,
        message=mensagem,
        from_email=None,  # usa DEFAULT_FROM_EMAIL do settings
        recipient_list=destinatarios,
        fail_silently=True,  # não quebra o sistema se o e-mail falhar
    )

    return len(destinatarios)