# -*- coding: utf-8 -*-
"""
Formulários do sistema de mensageria
dir: mensageria/forms.py
"""
from django import forms
from django.contrib.auth.models import Group as CustomGroup
from usuarios.models import CustomUser
from .models import TipoNotificacao, PrioridadeNotificacao


INPUT_CSS = (
    'w-full border border-gray-300 rounded-lg px-3 py-2 text-sm '
    'focus:ring-purple-500 focus:border-purple-500'
)


class EnviarNotificacaoForm(forms.Form):
    """Formulário para enviar notificação a um usuário ou grupo"""

    DESTINATARIO_TIPO_CHOICES = [
        ('grupo', 'Grupo / Instituição'),
        ('usuario', 'Usuário específico'),
    ]

    tipo_destinatario = forms.ChoiceField(
        choices=DESTINATARIO_TIPO_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'mr-2'}),
        initial='grupo',
        label='Enviar para',
    )

    destinatario_grupo = forms.ModelChoiceField(
        queryset=CustomGroup.objects.all().order_by('name'),
        required=False,
        label='Grupo / Instituição',
        empty_label='Selecione um grupo...',
        widget=forms.Select(attrs={'class': INPUT_CSS}),
    )

    destinatario_usuario = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_active=True).order_by('first_name'),
        required=False,
        label='Usuário',
        empty_label='Selecione um usuário...',
        widget=forms.Select(attrs={'class': INPUT_CSS}),
    )

    titulo = forms.CharField(
        max_length=200,
        label='Título',
        widget=forms.TextInput(attrs={
            'class': INPUT_CSS,
            'placeholder': 'Título da notificação',
        }),
    )

    mensagem = forms.CharField(
        label='Mensagem',
        widget=forms.Textarea(attrs={
            'class': INPUT_CSS,
            'rows': 4,
            'placeholder': 'Digite a mensagem...',
        }),
    )

    tipo = forms.ChoiceField(
        choices=TipoNotificacao.choices,
        initial=TipoNotificacao.MENSAGEM,
        label='Tipo',
        widget=forms.Select(attrs={'class': INPUT_CSS}),
    )

    prioridade = forms.ChoiceField(
        choices=PrioridadeNotificacao.choices,
        initial=PrioridadeNotificacao.NORMAL,
        label='Prioridade',
        widget=forms.Select(attrs={'class': INPUT_CSS}),
    )

    importante = forms.BooleanField(
        required=False,
        label='Marcar como importante',
        widget=forms.CheckboxInput(attrs={
            'class': 'rounded border-gray-300 text-purple-600 focus:ring-purple-500',
        }),
    )

    def clean(self):
        """Validar que existe um destinatário selecionado"""
        cleaned_data = super().clean()
        tipo_dest = cleaned_data.get('tipo_destinatario')

        if tipo_dest == 'grupo' and not cleaned_data.get('destinatario_grupo'):
            self.add_error('destinatario_grupo', 'Selecione um grupo.')
        elif tipo_dest == 'usuario' and not cleaned_data.get('destinatario_usuario'):
            self.add_error('destinatario_usuario', 'Selecione um usuário.')

        return cleaned_data