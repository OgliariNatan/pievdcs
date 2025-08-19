from django import forms
from sistema_justica.models.base import Vitima_dados, Agressor_dados, Filhos_dados, Municipio, Estado
from sistema_justica.models.defensoria_publica import FormularioMedidaProtetiva

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
                inactive_color='#4a4343',
                active_text='Solicitada',
                inactive_text='Não Solicitada'
            ),  # Widget personalizado
            #Relacionado a parte 1: Condutas de violência psicológica
            'critica_aparencia': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'proibia_make_roupas': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'obrigava_pedir_desculpas': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'fazer_nao_gosta': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'comentario_situacao': forms.Textarea(attrs={
                'class': 'form-control form-control-sm border border-gray-400 rounded-xl',
                'rows': 2
            }),
            # relacionado a parte 1: Condutas de humiliação e ridicularizaçÃO
            'ridicularizava_sozinha': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'ridicularizava_terceiros': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'humiliava_frente_filhos' : ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'piadas_familia': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'xingava_louca_burra': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'apelidos_tristes': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'relato_constrangida': forms.Textarea(attrs={
                'class': 'form-control form-control-sm border border-gray-400 rounded-xl',
                'rows': 2
            }),

            # Condutas de Manipulação
            'perdia_cabeca_culpava': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'culpava_ruim_voce': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ), 
            'insegurancas_capza': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'boa_dona_casa': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'ameacava_se_matar': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'invertia_fatos': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),

            'detalhes_coisas': forms.Textarea(attrs={
                'class': 'form-control form-control-sm border border-gray-400 rounded-xl',
                'rows': 2
            }),
            # Condutas de isolamento ou limitacao
            'dificula_contato_familia': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'telefone_familia_viva_voz': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'reclama_saia_sozinha': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'reclama_sozinha_estudar_trabalhar': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'bravo_conversa_homem': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'escolhia_amizade': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'controlava_distancia': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'senhas_redes_sociais': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'ciumes_atencao_proximidade': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'info_situa_isola': forms.Textarea(attrs={
                'class': 'form-control form-control-sm border border-gray-400 rounded-xl',
                'rows': 2
            }),

            # CONDUTAS AMEAÇADORAS
            'gritava_qualquer_coisa' : ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'amante_paquera': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'escondia_coisas_pessoais': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'destruia_moveis_casa': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'maltratava_animal_estimacao': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'contar_segredo': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'deixar_sem_nada': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'exibia_armas': ToggleSwitchWidget(size='xs',
                active_color='#9333ea',
                inactive_color='#4a4343',
                active_text='Sim',
                inactive_text='Não'
            ),
            'detalhes_medo': forms.Textarea(attrs={
                'class': 'form-control form-control-sm border border-gray-400 rounded-xl',
                'rows': 2
            }),

            # VIOLÊNCIA PSICOLÓGICA DIGITAL Q35

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