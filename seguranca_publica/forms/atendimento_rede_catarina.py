"""Formulário para cadastro/edição de atendimentos da Rede Catarina."""
from django import forms
from seguranca_publica.models.militar import AtendimentosRedeCatarina, AnexoAtendimento
from sistema_justica.django_toggle_switch import ToggleSwitchWidget

INPUT_CSS = (
    'w-full px-3 py-2 text-sm border border-gray-300 rounded-lg '
    'focus:ring-2 focus:ring-red-400 focus:border-red-400 outline-none'
)

EXTENSOES_IMAGEM = ['jpg', 'jpeg', 'png', 'webp', 'gif']
EXTENSOES_VIDEO = ['mp4', 'avi', 'mov', 'mkv', 'webm']
MAX_TAMANHO_IMAGEM = 10 * 1024 * 1024   # 10 MB
MAX_TAMANHO_VIDEO = 100 * 1024 * 1024    # 100 MB


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
                'class': INPUT_CSS, 'rows': 3,
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
                'class': INPUT_CSS, 'rows': 3,
                'placeholder': 'Providências adotadas no local...',
            }),
            'data_atendimento': forms.DateTimeInput(attrs={
                'class': INPUT_CSS, 'type': 'datetime-local',
            }),
            'descricao_atendimento': forms.Textarea(attrs={
                'class': INPUT_CSS, 'rows': 4,
                'placeholder': 'Descrição geral do atendimento...',
            }),
        }


def validar_anexos(request):
    """
    Valida arquivos de imagem e vídeo enviados via request.FILES.
    Retorna (imagens_validas, videos_validos, erros).
    """
    erros = []
    imagens_validas = []
    videos_validos = []

    for arq in request.FILES.getlist('imagens'):
        ext = arq.name.rsplit('.', 1)[-1].lower() if '.' in arq.name else ''
        if ext not in EXTENSOES_IMAGEM:
            erros.append(f'"{arq.name}" — extensão .{ext} não permitida. Use: {", ".join(EXTENSOES_IMAGEM)}')
            continue
        if arq.size > MAX_TAMANHO_IMAGEM:
            erros.append(f'"{arq.name}" excede o limite de 10MB.')
            continue
        imagens_validas.append(arq)

    for arq in request.FILES.getlist('videos'):
        ext = arq.name.rsplit('.', 1)[-1].lower() if '.' in arq.name else ''
        if ext not in EXTENSOES_VIDEO:
            erros.append(f'"{arq.name}" — extensão .{ext} não permitida. Use: {", ".join(EXTENSOES_VIDEO)}')
            continue
        if arq.size > MAX_TAMANHO_VIDEO:
            erros.append(f'"{arq.name}" excede o limite de 100MB.')
            continue
        videos_validos.append(arq)

    return imagens_validas, videos_validos, erros