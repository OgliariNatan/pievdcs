from django import forms
from sistema_justica.models.base import Vitima_dados, Agressor_dados, Filhos_dados, Municipio, Estado
from sistema_justica.models.defensoria_publica import FormularioMedidaProtetiva

class CadastroMedidaProtetiva(forms.ModelForm):
    class Meta:
        model = FormularioMedidaProtetiva
        fields = '__all__'
        widgets = {
            'data_solicitacao': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'periodo_mp': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control form-control-sm border border-gray-400 rounded-xl'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super(CadastroMedidaProtetiva, self).__init__(*args, **kwargs)
        
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control form-control-sm border border-gray-400 rounded-xl'})
        
        # Customizing specific fields if needed
    
        self.fields['data_solicitacao'].widget.attrs.update({'type': 'datetime-local'})
        self.fields['periodo_mp'].widget.attrs.update({
            'type': 'date',
            'class': 'form-control form-control-sm border border-gray-400 rounded-xl'
        })
        self.fields['solicitada_mpu'].widget.attrs.update({
            'type' : 'checkbox',
            'class': 'form-check-input form-control-sm',
        })
        self.fields['comarca_competente'].widget.attrs.update({
            'id' : 'id_comarca_competente',
            'class': 'form-control-sm'
        })
        self.fields['municipio_mp'].widget.attrs.update({
            'id' : 'id_municipio_mp',
            'class': 'form-control-sm'
        })