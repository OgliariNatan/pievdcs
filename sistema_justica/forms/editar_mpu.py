# sistema_justica/forms/editar_mpu.py
"""Formulário leve para edição posterior da avaliação de violência psicológica."""

from django import forms
from sistema_justica.models.defensoria_publica import FormularioMedidaProtetiva
from sistema_justica.django_toggle_switch import ToggleSwitchWidget
from sistema_justica.forms.utils import validar_eproc

cor_ativa = '#d97706'   # Âmbar
cor_inativa = '#4a4343'  # Cinza


def _toggle(active='Sim', inactive='Não'):
    """Atalho para criar ToggleSwitchWidget padrão."""
    return ToggleSwitchWidget(
        size='xs',
        active_color=cor_ativa,
        inactive_color=cor_inativa,
        active_text=active,
        inactive_text=inactive,
    )


class EditarFormularioMPU(forms.ModelForm):
    """
    Formulário para edição posterior das partes de avaliação de violência psicológica
    e dano emocional de uma Medida Protetiva já cadastrada.
    """
    class Meta:
        model = FormularioMedidaProtetiva
        # Somente campos editáveis pós-cadastro
        fields = [
            'eproc',  # Campo de processo judicial eletrônico
            # Parte 1: Condutas de Violência Psicológica — Gerais
            'critica_aparencia', 'proibia_make_roupas',
            'constrangia_frente_outras_pessoas', 'obrigava_pedir_desculpas',
            'fazer_nao_gosta', 'comentario_situacao',
            # Humilhação e Ridicularização
            'ridicularizava_sozinha', 'ridicularizava_terceiros',
            'humiliava_frente_filhos', 'piadas_familia',
            'xingava_louca_burra', 'apelidos_tristes', 'relato_constrangida',
            # Manipulação
            'perdia_cabeca_culpava', 'culpava_ruim_voce',
            'insegurancas_capza', 'boa_dona_casa',
            'ameaca_se_matar', 'invertia_fatos', 'detalhes_coisas',
            # Isolamento ou Limitação
            'dificula_contato_familia', 'telefone_familia_viva_voz',
            'reclama_saia_sozinha', 'reclama_sozinha_estudar_trabalhar',
            'bravo_conversa_homem', 'escolhia_amizade',
            'controlava_distancia', 'senhas_redes_sociais',
            'ciumes_atencao_proximidade', 'info_situa_isola',
            # Condutas Ameaçadoras
            'gritava_qualquer_coisa', 'amante_paquera',
            'escondia_coisas_pessoais', 'destruia_moveis_casa',
            'maltratava_animal_estimacao', 'contar_segredo',
            'deixar_sem_nada', 'exibia_armas', 'detalhes_medo',
            # Violência Psicológica Digital
            'manipulado_IA_BOOL', 'manipula_IA',
            # Violência Vicária
            'guarda_filhos', 'ameaca_filho_desiste_proc',
            'agia_agre_filhos_punir', 'deixava_remedio_filhos',
            'filhos_riscos', 'recusava_pagar_pensao', 'outras_condutas_vicaria',
            # Frequência
            'frequencia_condutas',
            # Parte 2: Dano Emocional
            'evita_pessoas_locais', 'medo_sozinha_casa',
            'pesadelo_dormir', 'tristeza_profunda',
            'constante_estado_alerta', 'dificuldade_fazer_atividades',
            'afastamento_trabalho', 'afastamento_fami_ami',
            'deixou_relacionar_afetiva_sexu',
            'deixou_relacionar_afetiva_sexu_mesAgressor',
            'desenvolveu_fobia', 'alteracao_apetite',
            'doente_frequente', 'tremores_lembras',
            'coracao_ace_sexo_oposto', 'estado_desanimo',
            'sentir_incapaz', 'olha_mundo_perigoso',
            'irritabilidade_constante', 'perdeu_vontade_viver_suicida',
            # Persistência e Observações
            'sintomas_persistem', 'observacoes_profissional',
        ]
        widgets = {
            'eproc': forms.TextInput(attrs={
                'inputmode': 'numeric',
                'maxlength': '20',
                'placeholder': 'Ex: 20000764420548240002',
                'class': 'form-control form-control-sm border border-gray-400 rounded-xl',
            }),
            # Condutas Gerais
            'critica_aparencia': _toggle(),
            'proibia_make_roupas': _toggle(),
            'constrangia_frente_outras_pessoas': _toggle(),
            'obrigava_pedir_desculpas': _toggle(),
            'fazer_nao_gosta': _toggle(),
            'comentario_situacao': forms.Textarea(attrs={'rows': 2}),
            # Humilhação
            'ridicularizava_sozinha': _toggle(),
            'ridicularizava_terceiros': _toggle(),
            'humiliava_frente_filhos': _toggle(),
            'piadas_familia': _toggle(),
            'xingava_louca_burra': _toggle(),
            'apelidos_tristes': _toggle(),
            'relato_constrangida': forms.Textarea(attrs={'rows': 2}),
            # Manipulação
            'perdia_cabeca_culpava': _toggle(),
            'culpava_ruim_voce': _toggle(),
            'insegurancas_capza': _toggle(),
            'boa_dona_casa': _toggle(),
            'ameaca_se_matar': _toggle(),
            'invertia_fatos': _toggle(),
            'detalhes_coisas': forms.Textarea(attrs={'rows': 2}),
            # Isolamento
            'dificula_contato_familia': _toggle(),
            'telefone_familia_viva_voz': _toggle(),
            'reclama_saia_sozinha': _toggle(),
            'reclama_sozinha_estudar_trabalhar': _toggle(),
            'bravo_conversa_homem': _toggle(),
            'escolhia_amizade': _toggle(),
            'controlava_distancia': _toggle(),
            'senhas_redes_sociais': _toggle(),
            'ciumes_atencao_proximidade': _toggle(),
            'info_situa_isola': forms.Textarea(attrs={'rows': 2}),
            # Ameaçadoras
            'gritava_qualquer_coisa': _toggle(),
            'amante_paquera': _toggle(),
            'escondia_coisas_pessoais': _toggle(),
            'destruia_moveis_casa': _toggle(),
            'maltratava_animal_estimacao': _toggle(),
            'contar_segredo': _toggle(),
            'deixar_sem_nada': _toggle(),
            'exibia_armas': _toggle(),
            'detalhes_medo': forms.Textarea(attrs={'rows': 2}),
            # Digital
            'manipulado_IA_BOOL': _toggle(),
            'manipula_IA': forms.Textarea(attrs={'rows': 2}),
            # Vicária
            'guarda_filhos': _toggle(),
            'ameaca_filho_desiste_proc': _toggle(),
            'agia_agre_filhos_punir': _toggle(),
            'deixava_remedio_filhos': _toggle(),
            'filhos_riscos': _toggle(),
            'recusava_pagar_pensao': _toggle(),
            'outras_condutas_vicaria': forms.Textarea(attrs={'rows': 2}),
            # Dano Emocional
            'evita_pessoas_locais': _toggle(),
            'medo_sozinha_casa': _toggle(),
            'pesadelo_dormir': _toggle(),
            'tristeza_profunda': _toggle(),
            'constante_estado_alerta': _toggle(),
            'dificuldade_fazer_atividades': _toggle(),
            'afastamento_trabalho': _toggle(),
            'afastamento_fami_ami': _toggle(),
            'deixou_relacionar_afetiva_sexu': _toggle(),
            'deixou_relacionar_afetiva_sexu_mesAgressor': _toggle(),
            'desenvolveu_fobia': _toggle(),
            'alteracao_apetite': _toggle(),
            'doente_frequente': _toggle(),
            'tremores_lembras': _toggle(),
            'coracao_ace_sexo_oposto': _toggle(),
            'estado_desanimo': _toggle(),
            'sentir_incapaz': _toggle(),
            'olha_mundo_perigoso': _toggle(),
            'irritabilidade_constante': _toggle(),
            'perdeu_vontade_viver_suicida': _toggle(),
            # Texto
            'sintomas_persistem': forms.Textarea(attrs={'rows': 3}),
            'observacoes_profissional': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Classe padrão nos TextAreas e Selects (sem tocar nos toggles)
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, (forms.Textarea, forms.Select)):
                widget.attrs.setdefault('class', '')
                widget.attrs['class'] += ' form-control form-control-sm border border-gray-400 rounded-xl'
                widget.attrs['class'] = widget.attrs['class'].strip()
        
        def clean_eproc(self):
            return validar_eproc(self.cleaned_data.get('eproc'))