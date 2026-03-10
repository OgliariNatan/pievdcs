"""Utilitários compartilhados entre os formulários do sistema de justiça."""

from django import forms


def validar_eproc(eproc: str | None) -> str | None:
    """Valida número eProc CNJ: exatamente 20 dígitos numéricos."""
    if not eproc:
        return eproc

    if not eproc.isdigit():
        raise forms.ValidationError('Digite apenas números, sem traços ou pontos.')

    if len(eproc) != 20:
        raise forms.ValidationError(
            f'O número deve ter 20 dígitos. Você digitou {len(eproc)}.'
        )

    return eproc