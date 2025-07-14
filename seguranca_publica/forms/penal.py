from django import forms
from django.forms import ModelForm
from ..models.penal import tipo_atendimento, ModeloPenal
from sistema_justica.models.base import Agressor_dados
from django.utils import timezone


class TipoAtendimentoForm(ModelForm):
    class Meta:
        model = tipo_atendimento
        fields = ['instituicao_responsavel', 'tematica']
        widgets = {
            'instituicao_responsavel': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200',
            }),
            'tematica': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200',
            }),
        }


class ModeloPenalForm(ModelForm):
    class Meta:
        model = ModeloPenal
        fields = ['data_atendimento', 'tempo_atendimento', 'setor_atendimento', 
                  'atendimento', 'agressores_atendidos', 'avaliacao', 'teste']
        widgets = {
            'data_atendimento': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200',
            }),
            'tempo_atendimento': forms.TextInput(attrs={
                'type': 'time',
                'pattern': '[0-9]{2}:[0-9]{2}',
                'placeholder': 'Ex: 01:30',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200',
            }),
            'setor_atendimento': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200',
            }),
            'atendimento': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200',
            }),
            # 'agressores_atendidos': forms.SelectMultiple(attrs={
            #     'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200',
            #     'size': '5',
            # }),
            'agressores_atendidos': forms.CheckboxSelectMultiple(attrs={
                'class': 'grid grid-cols-2 gap-2 mt-2 ',
            }),
            'teste': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-purple-600',
            }),
            'avaliacao': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Digite a descrição do atendimento...',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-200',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_atendimento'].initial = timezone.now()