"""Formulário para cadastro/edição de atendimentos da Rede Catarina."""
from django import forms
from seguranca_publica.models.militar import AtendimentosRedeCatarina
from sistema_justica.django_toggle_switch import ToggleSwitchWidget

INPUT_CSS = (
    'w-full px-3 py-2 text-sm border border-gray-300 rounded-lg '
    'focus:ring-2 focus:ring-red-400 focus:border-red-400 outline-none'
)


class AtendimentoRedeCatarinaForm(forms.ModelForm):
    """Formulário de atendimento da Rede Catarina."""

    class Meta:
        model = AtendimentosRedeCatarina
        fields = [
            'tipo_patrulha', 'equipe', 'houve_contato_vitima',
            'vitima_relatou_descumprimento', 'descricao_descumprimento',
            'situacao_vitima', 'agressor_presente', 'providencias_tomadas',
            'data_atendimento', 'descricao_atendimento',
        ]
        widgets = {
            'tipo_patrulha': forms.Select(attrs={'class': INPUT_CSS}),
            'equipe': forms.TextInput(attrs={
                'class': INPUT_CSS,
                'placeholder': 'Ex: VTR 1234 / Equipe Alpha',
            }),
            'houve_contato_vitima': ToggleSwitchWidget(
                size='md',
                active_color='#16a34a',
                inactive_color='#9CA3AF',
                active_text='Sim',
                inactive_text='Não',
            ),
            'vitima_relatou_descumprimento': ToggleSwitchWidget(
                size='md',
                active_color='#dc2626',
                inactive_color='#9CA3AF',
                active_text='Sim — Autoridades serão notificadas',
                inactive_text='Não',
            ),
            'descricao_descumprimento': forms.Textarea(attrs={
                'class': INPUT_CSS,
                'rows': 3,
                'placeholder': 'Descreva o descumprimento relatado...',
            }),
            'situacao_vitima': forms.Select(attrs={'class': INPUT_CSS}),
            'agressor_presente': ToggleSwitchWidget(
                size='md',
                active_color='#ea580c',
                inactive_color='#9CA3AF',
                active_text='Sim',
                inactive_text='Não',
            ),
            'providencias_tomadas': forms.Textarea(attrs={
                'class': INPUT_CSS,
                'rows': 3,
                'placeholder': 'Providências adotadas no local...',
            }),
            'data_atendimento': forms.DateTimeInput(attrs={
                'class': INPUT_CSS,
                'type': 'datetime-local',
            }),
            'descricao_atendimento': forms.Textarea(attrs={
                'class': INPUT_CSS,
                'rows': 4,
                'placeholder': 'Descrição geral do atendimento...',
            }),
        }