from django import forms
from sistema_justica.models.base import Vitima_dados, Agressor_dados, Filhos_dados, Municipio, Estado
from sistema_justica.models.defensoria_publica import FormularioMedidaProtetiva, default_periodo_mp

from sistema_justica.django_toggle_switch import ToggleSwitchWidget
from django.forms.widgets import DateTimeInput, DateInput, SelectDateWidget, CheckboxInput
from sistema_justica.forms.utils import validar_eproc

cor_ativa_toggle = '#9333ea'  # Roxo
cor_inativa_toggle = '#4a4343'  # Cinza

class CadastroMedidaProtetiva(forms.ModelForm):
    class Meta:
        model = FormularioMedidaProtetiva
        fields = '__all__'
        exclude = ['medida_protetiva_concedida',]
        widgets = {
            'data_solicitacao': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'periodo_mp': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control form-control-sm border border-gray-400 rounded-xl',
                },
                format='%Y-%m-%d',
            ),
            
            'tipo_de_violencia': forms.CheckboxSelectMultiple(
                attrs={'class': 'form-check-input'}
            ),

            'solicitada_mpu': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Solicitada',
                inactive_text='Não Solicitada'
            ),  # Widget personalizado
            'eproc': forms.TextInput(attrs={
                'inputmode': 'numeric',
                'maxlength': '20',
                'placeholder': 'Ex: 80000764420228240042',
                'class': 'form-control form-control-sm border border-gray-400 rounded-xl',
            }),
            #parte 1: Condutas de violência psicológica
            'critica_aparencia': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'proibia_make_roupas': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'constrangia_frente_outras_pessoas': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'obrigava_pedir_desculpas': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'fazer_nao_gosta': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'comentario_situacao': forms.Textarea(attrs={
                'class': 'form-control form-control-sm border border-gray-400 rounded-xl',
                'rows': 2
            }),
            # relacionado a parte 1: Condutas de humiliação e ridicularizaçÃO
            'ridicularizava_sozinha': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'ridicularizava_terceiros': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'humiliava_frente_filhos' : ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'piadas_familia': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'xingava_louca_burra': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'apelidos_tristes': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'relato_constrangida': forms.Textarea(attrs={
                'class': 'form-control form-control-sm border border-gray-400 rounded-xl',
                'rows': 2
            }),

            # Condutas de Manipulação
            'perdia_cabeca_culpava': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'culpava_ruim_voce': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ), 
            'insegurancas_capza': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'boa_dona_casa': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'ameaca_se_matar': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'invertia_fatos': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),

            'detalhes_coisas': forms.Textarea(attrs={
                'class': 'form-control form-control-sm border border-gray-400 rounded-xl',
                'rows': 2
            }),
            # Condutas de isolamento ou limitacao
            'dificula_contato_familia': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'telefone_familia_viva_voz': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'reclama_saia_sozinha': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'reclama_sozinha_estudar_trabalhar': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'bravo_conversa_homem': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'escolhia_amizade': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'controlava_distancia': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'senhas_redes_sociais': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'ciumes_atencao_proximidade': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'info_situa_isola': forms.Textarea(attrs={
                'class': 'form-control form-control-sm border border-gray-400 rounded-xl',
                'rows': 2
            }),

            # CONDUTAS AMEAÇADORAS
            'gritava_qualquer_coisa' : ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'amante_paquera': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'escondia_coisas_pessoais': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'destruia_moveis_casa': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'maltratava_animal_estimacao': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'contar_segredo': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'deixar_sem_nada': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'exibia_armas': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'detalhes_medo': forms.Textarea(attrs={
                'class': 'form-control form-control-sm border border-gray-400 rounded-xl',
                'rows': 2
            }),

            # VIOLÊNCIA PSICOLÓGICA DIGITAL Q35
            'manipulado_IA_BOOL': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'manipula_IA': forms.Textarea(attrs={
                'class': 'form-control form-control-sm border border-gray-400 rounded-xl',
                'rows': 2
            }), 
            # (violência vicária) Q36
            'guarda_filhos' : ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'ameaca_filho_desiste_proc': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'agia_agre_filhos_punir' : ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'deixava_remedio_filhos': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'filhos_riscos': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'recusava_pagar_pensao': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'outras_condutas_vicaria': forms.Textarea(attrs={
                'class': 'form-control form-control-sm border border-gray-400 rounded-xl',
                'rows': 2
            }),
            # Parte 2: Dano Emocional
            'evita_pessoas_locais': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'medo_sozinha_casa': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'pesadelo_dormir': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'tristeza_profunda': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'constante_estado_alerta': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'dificuldade_fazer_atividades': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'afastamento_trabalho': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'afastamento_fami_ami': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'deixou_relacionar_afetiva_sexu': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'deixou_relacionar_afetiva_sexu_mesAgressor': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'desenvolveu_fobia': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'alteracao_apetite': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'doente_frequente': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ), 
            'tremores_lembras': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'coracao_ace_sexo_oposto': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'estado_desanimo': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'sentir_incapaz': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'olha_mundo_perigoso': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'irritabilidade_constante': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'perdeu_vontade_viver_suicida': ToggleSwitchWidget(size='xs',
                active_color=cor_ativa_toggle,
                inactive_color=cor_inativa_toggle,
                active_text='Sim',
                inactive_text='Não'
            ),
            'sintomas_persistem': forms.Textarea(attrs={
                'class': 'form-control form-control-sm border border-gray-400 rounded-xl',
                'rows': 3
            }),
            'observacoes_profissional': forms.Textarea(attrs={
                'class': 'form-control form-control-sm border border-gray-400 rounded-xl',
                'rows': 4
            }),

        }
    
    def __init__(self, *args, **kwargs):
        super(CadastroMedidaProtetiva, self).__init__(*args, **kwargs)
        
        # Aplicar classes padrão para todos os campos, EXCETO o toggle switch
        for field_name, field in self.fields.items():
            if field_name != 'solicitada_mpu':  # Não modificar o ToggleSwitchWidget
                field.widget.attrs.update({'class': 'form-control form-control-sm border border-gray-400 rounded-xl'})
        
        # Customizações específicas para campos (exceto solicitada_mpu)
        self.fields['data_solicitacao'].widget.attrs.update({'type': 'datetime-local'})
        if not self.instance.pk:
            self.initial['periodo_mp'] = default_periodo_mp().strftime('%Y-%m-%d')  # Define a data padrão para o campo período_mp

        
        self.fields['comarca_competente'].widget.attrs.update({
            'id': 'id_comarca_competente',
            'class': 'form-control form-control-sm border border-gray-400 rounded-xl'
        })
        self.fields['municipio_mp'].widget.attrs.update({
            'id': 'id_municipio_mp',
            'class': 'form-control form-control-sm border border-gray-400 rounded-xl'
        })
    
    def clean_eproc(self):
        """Valida que o campo eproc contém exatamente 20 dígitos numéricos."""
        return validar_eproc(self.cleaned_data.get('eproc'))