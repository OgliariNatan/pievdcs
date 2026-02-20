# municipio/forms/municipio_forms.py
from django import forms
from django.forms import ModelForm
from seguranca_publica.models.penal import tipo_atendimento, ModeloPenal


class MunicipioAtendimentoForm(ModelForm):
    """Formulário de atendimento filtrado por instituição municipal."""

    class Meta:
        model = ModeloPenal
        fields = [
            'data_atendimento', 'tempo_atendimento', 'setor_atendimento',
            'atendimento', 'agressores_atendidos', 'avaliacao',
        ]
        widgets = {
            'data_atendimento': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-teal-500 focus:border-teal-500 transition-all duration-200',
            }),
            'tempo_atendimento': forms.TextInput(attrs={
                'type': 'time',
                'pattern': '[0-9]{2}:[0-9]{2}',
                'placeholder': 'Ex: 01:30',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-teal-500 focus:border-teal-500 transition-all duration-200',
            }),
            'setor_atendimento': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-teal-500 focus:border-teal-500 transition-all duration-200',
            }),
            'atendimento': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-teal-500 focus:border-teal-500 transition-all duration-200',
            }),
            'agressores_atendidos': forms.CheckboxSelectMultiple(attrs={
                'class': 'grid grid-cols-2 gap-2 mt-2',
            }),
            'avaliacao': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Digite a descrição do atendimento...',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-teal-500 focus:border-teal-500 transition-all duration-200',
            }),
        }

    def __init__(self, *args, instituicao=None, **kwargs):
        """Filtra tipo_atendimento pela instituição."""
        super().__init__(*args, **kwargs)
        if instituicao:
            self.fields['atendimento'].queryset = (
                tipo_atendimento.objects.filter(
                    instituicao_responsavel=instituicao
                )
            )