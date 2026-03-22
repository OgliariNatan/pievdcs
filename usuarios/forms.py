# -*- coding: utf-8 -*-
"""
dir: usuarios/forms.py
Formulários de configuração da conta do usuário.
"""
from django import forms
from django.contrib.auth.forms import PasswordChangeForm

from .models import CustomUser

INPUT_CSS = (
    'w-full px-4 py-3 text-sm border border-gray-300 rounded-xl '
    'focus:ring-2 focus:ring-purple-400 focus:border-purple-400 outline-none'
)

FILE_CSS = (
    'w-full px-4 py-3 text-sm border border-dashed border-gray-300 rounded-xl '
    'focus:ring-2 focus:ring-purple-400 focus:border-purple-400 outline-none bg-white'
)


class ContaDadosForm(forms.ModelForm):
    """Formulário para edição dos dados cadastrais do usuário."""
    data_nascimento = forms.DateField(
        required=False,
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'class': INPUT_CSS,
                'type': 'date',
            },
        ),
    )

    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name',
            'email',
            'data_nascimento',
            'telefone',
            'genero',
            'cpf',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': INPUT_CSS,
                'placeholder': 'Digite o primeiro nome',
            }),
            'last_name': forms.TextInput(attrs={
                'class': INPUT_CSS,
                'placeholder': 'Digite o sobrenome',
            }),
            'email': forms.EmailInput(attrs={
                'class': INPUT_CSS,
                'placeholder': 'Digite o e-mail',
            }),
            'telefone': forms.TextInput(attrs={
                'class': INPUT_CSS,
                'placeholder': '(00) 00000-0000',
                'maxlength': '15',
            }),
            'genero': forms.Select(attrs={
                'class': INPUT_CSS,
            }),
            'cpf': forms.TextInput(attrs={
                'class': INPUT_CSS,
                'placeholder': '000.000.000-00',
                'maxlength': '14',
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            return ''

        qs = CustomUser.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Já existe outro usuário com este e-mail.')
        return email

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if not cpf:
            return None

        qs = CustomUser.objects.filter(cpf=cpf).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Já existe outro usuário com este CPF.')
        return cpf


class ContaArquivosForm(forms.ModelForm):
    """Formulário para atualização da foto e comprovante de vínculo."""

    class Meta:
        model = CustomUser
        fields = ['foto', 'comprovante_vinculo']
        widgets = {
            'foto': forms.ClearableFileInput(attrs={
                'class': FILE_CSS,
                'accept': 'image/*',
            }),
            'comprovante_vinculo': forms.ClearableFileInput(attrs={
                'class': FILE_CSS,
                'accept': '.pdf,application/pdf',
            }),
        }


class ContaSenhaForm(PasswordChangeForm):
    """Formulário de alteração de senha."""

    old_password = forms.CharField(
        label='Senha atual',
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CSS,
            'placeholder': 'Digite a senha atual',
        }),
    )
    new_password1 = forms.CharField(
        label='Nova senha',
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CSS,
            'placeholder': 'Digite a nova senha',
        }),
    )
    new_password2 = forms.CharField(
        label='Confirmar nova senha',
        widget=forms.PasswordInput(attrs={
            'class': INPUT_CSS,
            'placeholder': 'Repita a nova senha',
        }),
    )