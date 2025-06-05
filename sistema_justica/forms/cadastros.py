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

class CadastroMunicipioForm(forms.ModelForm):
    class Meta:
        model = Municipio
        fields = '__all__'

class CadastroFilhosForm(forms.ModelForm):
    """
    Formulário para cadastrar os filhos da vítima e do agressor.
    """
    class Meta:
        model = Filhos_dados
        fields = '__all__'



class CadastroVitimaUpdateForm(forms.ModelForm):
            """
            Formulário para atualizar os dados da vítima.
            """
            class Meta:
                model = Vitima_dados
                fields = '__all__'
                widgets = {
                    'nome': forms.TextInput(attrs={'readonly': 'readonly'}),
                    'cpf': forms.TextInput(attrs={'readonly': 'readonly'}),
                }

class CadastroAgressorUpdateForm(forms.ModelForm):
            class Meta:
                model = Agressor_dados
                fields = '__all__'
                widgets = {
                    'nome': forms.TextInput(attrs={'readonly': 'readonly'}),
                    'cpf': forms.TextInput(attrs={'readonly': 'readonly'}),
                }

class CadastroFilhosUpdateForm(forms.ModelForm):
            class Meta:
                model = Filhos_dados
                fields = '__all__'
                widgets = {
                    'nome': forms.TextInput(attrs={'readonly': 'readonly'}),
                    'cpf': forms.TextInput(attrs={'readonly': 'readonly'}),
                }

class CadastroMunicipioUpdateForm(forms.ModelForm):
            class Meta:
                model = Municipio
                fields = '__all__'
                