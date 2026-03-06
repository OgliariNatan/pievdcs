# MAIN/forms.py
# dir: MAIN/forms.py
"""Formulários do app MAIN."""
from django import forms
from .models import ConteudoHome

INPUT_CSS = (
    'w-full px-3 py-2 text-sm border border-gray-300 rounded-lg '
    'focus:ring-2 focus:ring-purple-400 focus:border-purple-400 outline-none'
)


class ConteudoHomeForm(forms.ModelForm):
    """Formulário para inserção de notícias/conteúdo na página inicial."""

    class Meta:
        model = ConteudoHome
        fields = [
            'titulo', 'texto', 'secao', 'imagem',
            'video', 'link', 'data_expiracao', 'publicado',
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': INPUT_CSS,
                'placeholder': 'Título da notícia',
            }),
            'texto': forms.Textarea(attrs={
                'class': INPUT_CSS,
                'rows': 5,
                'placeholder': 'Conteúdo da notícia...',
            }),
            'secao': forms.Select(attrs={'class': INPUT_CSS}),
            'imagem': forms.ClearableFileInput(attrs={
                'class': INPUT_CSS,
                'accept': 'image/jpeg,image/png,image/gif',
            }),
            'video': forms.ClearableFileInput(attrs={
                'class': INPUT_CSS,
                'accept': 'video/mp4,video/avi,video/quicktime,video/x-ms-wmv',
            }),
            'link': forms.URLInput(attrs={
                'class': INPUT_CSS,
                'placeholder': 'https://exemplo.com',
            }),
            'data_expiracao': forms.DateTimeInput(attrs={
                'class': INPUT_CSS,
                'type': 'datetime-local',
            }),
            'publicado': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-purple-600 rounded focus:ring-purple-400',
            }),
        }