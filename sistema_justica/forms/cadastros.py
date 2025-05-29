from django import forms
from sistema_justica.models.base import Vitima_dados, Agressor_dados, Filhos_dados, Municipio

class CadastroVitimaForm(forms.ModelForm):
    class Meta:
        model = Vitima_dados
        fields = '__all__'

    
class CadastroAgressorForm(forms.ModelForm):
    class Meta:
        model = Agressor_dados
        fields = '__all__'      