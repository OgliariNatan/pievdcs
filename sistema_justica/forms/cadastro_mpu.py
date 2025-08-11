from django import forms
from sistema_justica.models.base import Vitima_dados, Agressor_dados, Filhos_dados, Municipio, Estado
from sistema_justica.models.defensoria_publica import FormularioMedidaProtetiva
from sistema_justica.widgets import ToggleSwitchWidget
from sistema_justica.django_toggle_switch import ToggleSwitchWidget
from django.forms.widgets import DateTimeInput, DateInput, SelectDateWidget, CheckboxInput

class CadastroMedidaProtetiva(forms.ModelForm):
    class Meta:
        model = FormularioMedidaProtetiva
        fields = '__all__'
        widgets = {
            'data_solicitacao': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'periodo_mp': forms.SelectDateWidget(attrs={
                'type': 'date',
                'class': 'form-control form-control-sm border border-gray-400 rounded-xl'
            }),
            'solicitada_mpu': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#ccc',
                active_text='Solicitada',
                inactive_text='Não Solicitada'
            ),  # Widget personalizado
            #'agressor':
        }
    
    def __init__(self, *args, **kwargs):
        super(CadastroMedidaProtetiva, self).__init__(*args, **kwargs)
        
        # Aplicar classes padrão para todos os campos, EXCETO o toggle switch
        for field_name, field in self.fields.items():
            if field_name != 'solicitada_mpu':  # Não modificar o ToggleSwitchWidget
                field.widget.attrs.update({'class': 'form-control form-control-sm border border-gray-400 rounded-xl'})
        
        # Customizações específicas para campos (exceto solicitada_mpu)
        self.fields['data_solicitacao'].widget.attrs.update({'type': 'datetime-local'})
        self.fields['periodo_mp'].widget.attrs.update({
            'type': 'date',
            'class': 'form-control form-control-sm border border-gray-400 rounded-xl'
        })
        
        self.fields['comarca_competente'].widget.attrs.update({
            'id': 'id_comarca_competente',
            'class': 'form-control form-control-sm border border-gray-400 rounded-xl'
        })
        self.fields['municipio_mp'].widget.attrs.update({
            'id': 'id_municipio_mp',
            'class': 'form-control form-control-sm border border-gray-400 rounded-xl'
        })