from django import forms
from sistema_justica.models.base import Vitima_dados, Agressor_dados, Filhos_dados, Municipio, Estado

class CadastroVitimaForm(forms.ModelForm):
    class Meta:
        model = Vitima_dados
        fields = '__all__'
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        super(CadastroVitimaForm, self).__init__(*args, **kwargs)
        fields = '__all__'

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control form-control-sm border border-gray-400 rounded-xl'})

       
class CadastroAgressorForm(forms.ModelForm):
    class Meta:
        model = Agressor_dados
        fields = '__all__'      
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }


    def __init__(self, *args, **kwargs):
        super(CadastroAgressorForm, self).__init__(*args, **kwargs)
        fields = '__all__'
            # self.fields['estado'].widget.attrs.update({'class': 'form-control, form-control-sm', 'type': 'text'})
            # self.fields['municipio'].widget.attrs.update({'class': 'form-control, form-control-sm', 'type': 'text'})
            # self.fields['data_nascimento'].widget.attrs.update({'class': 'form-control, form-control-sm', 'type': 'date'})

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control form-control-sm border border-gray-400 rounded-xl'})


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
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }

        def __init__(self, *args, **kwargs):
            super(CadastroFilhosForm, self).__init__(*args, **kwargs)
            self.fields['estado'].widget.attrs.update({'class': 'form-control, form-control-sm', 'type': 'text'})
            self.fields['municipio'].widget.attrs.update({'class': 'form-control, form-control-sm', 'type': 'text'})
            self.fields['data_nascimento'].widget.attrs.update({'class': 'form-control, form-control-sm', 'type': 'date'})



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