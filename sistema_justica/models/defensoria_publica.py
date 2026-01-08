# -*- coding: utf-8 -*-
"""  
    Modelo pertinente a defensoria publica
    dir: sistema_justica/models/defensoria_publica.py
    @author: OgliariNatan
"""

from django.db import models
from datetime import datetime, timedelta, timezone
from usuarios.models import CustomUser
from sistema_justica.models.base import Vitima_dados, Agressor_dados, Filhos_dados, Municipio, Estado, TipoDeViolencia
from seguranca_publica.models.base import grau_parentesco_agressor_choices
from smart_selects.db_fields import ChainedForeignKey, ChainedManyToManyField, GroupedForeignKey
from sistema_justica.models.poder_judiciario import ComarcasPoderJudiciario



def default_periodo_mp():
    '''
    Função para definir o período padrão da medida protetiva
    que será de 120 dias a partir da data atual
    '''
    return datetime.now().date()  + timedelta(days=120)



class FormularioMedidaProtetiva(models.Model):
    '''
    Formulario para preencimento da Defensoria Pública
    solicitando a Medida Protetiva
    '''
    ID = models.AutoField(
        primary_key=True,
        #auto_created=True,
    )

    data_solicitacao = models.DateTimeField(
        default=datetime.now, 
        verbose_name='Data de Solicitação'
    )
        
    vitima = models.ForeignKey(
        Vitima_dados,
        on_delete=models.CASCADE,
        verbose_name='Vitima',
        null=True, blank=True
    )

    agressor = models.ForeignKey(
        Agressor_dados,
        on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name='Agressor'
    )

    periodo_mp = models.DateField(
        default=default_periodo_mp,
        verbose_name='Período da Medida Protetiva'
    )

    solicitada_mpu = models.BooleanField(
        default=True,
        verbose_name='Medida Protetiva de Urgência'
    )
    
    tipo_de_violencia = models.ManyToManyField(
        TipoDeViolencia,
        verbose_name= "Tipo de Violência",
        related_name="%(class)s_formulario_mp",
        related_query_name="%(class)s_formulario_mp",
        blank=True,
    )

    relacionamento_familiar = models.CharField(
        max_length=1,
        choices=[
            ('1', 'Pessoa que reside no mesmo lar '),
            ('2', 'Ex-residente do lar'),
            ('3', 'Empregado(a) doméstico(a)'),
            ('4', 'Cuidador(a)'),
            ('5', 'Outro'),
        ],
        verbose_name="Relacionamento Familiar",
        null=True, blank=True
    )

    comarca_competente = models.ForeignKey(
        ComarcasPoderJudiciario,
        on_delete=models.CASCADE,
        verbose_name='Comarca Competente',
        null=True, 
        blank=True
    )
    municipio_mp = ChainedForeignKey(
        Municipio,
        chained_field="comarca_competente",
        chained_model_field="comarcas_abrangentes",
        show_all=False,  # Altere para True para garantir que todos os municípios sejam exibidos
        auto_choose=True, 
        sort=True,
        verbose_name="Município do Fato",
        null=True,
        blank=True  # Permita campo em branco para evitar erro de validação
    )
    
    bairro_mp = models.CharField(
        max_length=100,
        verbose_name='Bairro:',
        null=True, 
        blank=False
    )
    rua_mp = models.CharField(
        max_length=100,
        verbose_name='Rua:',
        null=True, 
        blank=False
    )
    n_casa_mp = models.CharField(
        max_length=5,
        verbose_name='Nº:',
        null=True, 
        blank=False
    )
    grau_parentesco_agressor = models.CharField(
        max_length=15,
        choices=grau_parentesco_agressor_choices,
        default='Conjuge',
        verbose_name="Grau de Parentesco com o Agressor"
    )

    possivel_causa = models.CharField(
        max_length=250,
        verbose_name='Possível Causa da Violência:',
    )

    filhos = ChainedManyToManyField(
        Filhos_dados,
        chained_field="agressor",
        chained_model_field="agressor",
        verbose_name='Filhos',
        blank=True,
        #null=True
    )

    #Relacionado a parte 1: Condutas de violência psicológica
    critica_aparencia = models.BooleanField(
        default=False,
        verbose_name='1. Criticava sua aparência (corpo, cabelo, roupas)?'
    )

    proibia_make_roupas = models.BooleanField(
        default=False,
        verbose_name='2. Proibia você de usar roupas ou maquiagem?'
    )
    constrangia_frente_outras_pessoas = models.BooleanField(
        default=False,
        verbose_name='3. Constrangia você na frente de outras pessoas?'
    )
    obrigava_pedir_desculpas = models.BooleanField(
        default=False,
        verbose_name='4. Obrigava você a pedir desculpas, mesmo quando não era sua culpa?'
    )

    fazer_nao_gosta = models.BooleanField(
        default=False,
        verbose_name='5. Constrangia você a fazer coisas que não gostava?'
    )

    comentario_situacao = models.TextField(
        verbose_name='Você gostaria de contar detalhes ou outra situação de constrangimento?',
        null=True,
        blank=True
    )

    # relacionado a parte 1: Condutas de humiliação e ridicularizaçÃO
    ridicularizava_sozinha = models.BooleanField(
        verbose_name='6. Ofendia, envergonhava ou ridicularizava você quando estavam sozinhos?',
        default=False
    )
    ridicularizava_terceiros = models.BooleanField(
        verbose_name='7. Ofendia, envergonhava ou ridicularizava você quando estavam na frente de outras pessoas?',
        default=False
    )

    humiliava_frente_filhos = models.BooleanField(
        verbose_name='8. Humilhava você na frente de seus filhos?',
        default=False
    )

    piadas_familia = models.BooleanField(
        verbose_name='9. Fazia piadas sobre ou você sua familia?',
        default=False
    )

    xingava_louca_burra = models.BooleanField(
        verbose_name='10. Xingava você de louca, burra, incapaz ou que não fazia nada direito?',
        default=False
    )

    apelidos_tristes= models.BooleanField(
        verbose_name='11. Criava apelidos para você, que a deixavam constrangida ou triste?',
        default=False
    )

    relato_constrangida = models.TextField(
        verbose_name='Você gostaria de contar mais detalhes ou mencionar alguma situação de humilhação ou ridicularização?',
        null=True,
        blank=True
    )

    # Condutas de Manipulação
    perdia_cabeca_culpava = models.BooleanField(
        verbose_name='12. Alegava que "perdia a cabeça" e culpava você?',
        default=False
    )

    culpava_ruim_voce = models.BooleanField(
        verbose_name='13. Culpava você por tudo de ruim que acontecia (desempego, dívidas e outros)?',
        default=False
    )

    insegurancas_capza = models.BooleanField(
        verbose_name='14. Usava seus medos e inseguranças dizendo que você não era capaz?',
        default=False
    )

    boa_dona_casa = models.BooleanField(
        verbose_name='15. Afirmava que você era uma boa "dona de casa", "boa mãe" e "esposa" para justificar o comportamento abusivo?',
        default=False
    )
    
    ameaca_se_matar = models.BooleanField(
        verbose_name='16. Ameaçava que ia se matar ou matar seus filhos quando você tentava terminar a relação?',
        default=False
    )
    
    invertia_fatos = models.BooleanField(
        verbose_name='17. Escondia, coisas invertia fatos e dizia que você estava louca?',
        default=False,
    )

    detalhes_coisas = models.TextField(
        verbose_name='Você gostaria de contar mais detalhes ou alguma situação específica?',
        null=True,
        blank=True
    )

    # Condutas de isolamento ou limitacao
    dificula_contato_familia = models.BooleanField(
        verbose_name='18. Dificultava seu contato com familiares?',
        default=False,
    )
    telefone_familia_viva_voz = models.BooleanField(
        verbose_name='19. Quando seus familiares ligavam, obrigava você a colocar em viva voz?',
        default=False,
    )

    reclama_saia_sozinha = models.BooleanField(
        verbose_name='20. Reclamava quando você saía sozinha?',
        default=False
    )

    reclama_sozinha_estudar_trabalhar = models.BooleanField(
        verbose_name='21. Reclamava quando você saía para estudar ou trabalhar?',
        default=False,
    )

    bravo_conversa_homem = models.BooleanField(
        verbose_name='22. Ficava aborrecido ou bravo se você conversava com homens que não eram da família?',
        default=False
    )

    escolhia_amizade = models.BooleanField(
        verbose_name='23. Escolhia suas amizades?',
        default=False
    )

    controlava_distancia = models.BooleanField(
        verbose_name='24. Controlava você por mensagens, ligações ou de outro modo?',
        default=False
    )

    senhas_redes_sociais = models.BooleanField(
        verbose_name='25. Exigia que você lhe desse suas senhas em redes sociais?',
        default=False
    )

    ciumes_atencao_proximidade = models.BooleanField(
        verbose_name='26. Tinha ciúmes se alguma pessoa lhe desse atenção ou se aproximasse de você?',
        default=False
    )

    info_situa_isola = models.TextField(
        verbose_name='Você gostaria de contar mais detalhes ou outra situação de isolamento?',
        null=True,
        blank=True
    )

    # CONDUTAS AMEAÇADORAS Q27
    gritava_qualquer_coisa = models.BooleanField(
        verbose_name='27. Gritava ou explodia por qualquer coisa?',
        default=False
    )

    amante_paquera = models.BooleanField(
        verbose_name='28. Explodia por ciúmes, dizia que você tinha amantes ou estava paquerando?',
        default=False
    )

    escondia_coisas_pessoais = models.BooleanField(
        verbose_name='29. Destruía ou escondia suas coisas pessoais?',
        default=False
    )
    destruia_moveis_casa = models.BooleanField(
        verbose_name='30. Destruía móveis ou utensílios da casa?',
        default=False,
    )

    maltratava_animal_estimacao = models.BooleanField(
        verbose_name='31. Maltratava ou ameaçava seus animais de estimação?',
        default=False
    )

    contar_segredo = models.BooleanField(
        verbose_name='32. Ameaçava contar seus segredos pessoais ou divulgar fotos suas para outras pessoas?',
        default=False
    )

    deixar_sem_nada = models.BooleanField(
        verbose_name='33.   Dizia que, se o deixasse, entraria com vários processos e ficaria sem nada?',
        default=False
    )

    exibia_armas = models.BooleanField(
        verbose_name='34. Exibia armas de fogo, facas ou objetos como forma de intimação?',
        default=False
    )

    detalhes_medo = models.TextField(
        verbose_name='Você gostaria de contar mais detalhes ou outra situação que lhe causava medo?',
        null=True,
        blank=True
    )

    # VIOLÊNCIA PSICOLÓGICA DIGITAL Q35

    manipulado_IA_BOOL = models.BooleanField(
        verbose_name='35. Para alguma das condutas anteriores, foi utilizada Inteligência Artificial (como programas ou aplicativos) ou outro recurso tecnológico para alterar imagem pessoal ou voz (fotos ou vídeos montados com sua imagem ou voz)?',
        default=False
    )
    manipula_IA = models.TextField(
        verbose_name='',
        null=True,
        blank=True
    )

    # (violência vicária) Q36
    guarda_filhos = models.BooleanField(
        verbose_name='36. Ameaçava pedir a guarda dos filhos?',
        default=False
    )

    ameaca_filho_desiste_proc = models.BooleanField(
        verbose_name='37. Ameaçava seus filhos para você desistir de algum processo?',
        default=False
    )

    agia_agre_filhos_punir = models.BooleanField(
        verbose_name='38. Agia com agressividade com os filhos como forma de puni-la?',
        default=False
    )

    deixava_remedio_filhos = models.BooleanField(
        verbose_name='39. Deixava de dar remédios para filhos doentes ou que necessitavam de cuidados especiais como forma de puni-la?',
        default=False
    )

    filhos_riscos = models.BooleanField(
        verbose_name='40. Colocava seus filhos em situações de riscos como forma de punila?',
        default=False
    )

    recusava_pagar_pensao = models.BooleanField(
        verbose_name='41. Recusava-se a pegar pensão para os filhos como forma de chantagem ou punição?',
        default=False
    )

    outras_condutas_vicaria = models.TextField(
        verbose_name='Outras situações',
        null=True,
        blank=True
    )
    # FREQUENCIAS_DAS_CONDUTAS

    frequencia_condutas = models.CharField(
        verbose_name='As condutas de constrangimento, humilhação, manipulação, de isolamento ou ameaçadoras que você descreveu aconteciam com que frequência',
        max_length=15,
        null=True,
        blank=True,
        choices=[
            ('no_descreveu', 'Não Descreveu'),
            ('pou_vezes', 'Poucas Vezes'),
            ('as_vezes', 'Muitas Vezes'),
            ('sempre', 'Sempre'),
        ],
        #default='no_descreveu'
    )

    #Parte 2: DANO EMOCIONAL
    # Inserir texto fixo com instruções
    evita_pessoas_locais = models.BooleanField(
        verbose_name='42. Passou a evitar pessoas ou lugares que relembram os fatos?',
        default=False
    )
    medo_sozinha_casa = models.BooleanField(
        verbose_name='43. Medo de ficar sozinha em casa ou sair desacompanhada?',
        default=False
    )
    pesadelo_dormir = models.BooleanField(
        verbose_name='44. Pesadelos ou dificuldade para dormir?',
        default=False
    )
    tristeza_profunda = models.BooleanField(
        verbose_name='45. Tristeza profunda ou crises de choro?',
        default=False
    )
    constante_estado_alerta = models.BooleanField(
        verbose_name='46. Constante estado de alerta (atenção e medo)?',
        default=False
    )
    dificuldade_fazer_atividades = models.BooleanField(
        verbose_name='47. Dificuldade para realizar as atividades do dia a dia, que antes você fazia normalmente?',
        default=False
    )
    afastamento_trabalho = models.BooleanField(
        verbose_name='48. Afastamento do trabalho ou estudos?',
        default=False
    )
    afastamento_fami_ami = models.BooleanField(
        verbose_name='49. Afastamento de familiares ou amigos/as?',
        default=False
    )
    deixou_relacionar_afetiva_sexu = models.BooleanField(
        verbose_name='50. Deixou de se relacionar sexualmente ou afetivamente com outras pessoas (por medo ou desconfiança)?',
        default=False
    )
    deixou_relacionar_afetiva_sexu_mesAgressor = models.BooleanField(
        verbose_name='51. Deixou de se relacionar com pessoas do mesmo sexo do agressor (por medo ou desconfiança)?',
        default=False
    )
    desenvolveu_fobia = models.BooleanField(
        verbose_name='52. Desenvolveu alguma fobia ou medo específico (altura, animais, pessoas, sangue)?',
        default=False
    )
    alteracao_apetite = models.BooleanField(
        verbose_name='53. Teve alterações do apetite com aumento ou perda de peso?',
        default=False
    )
    doente_frequente = models.BooleanField(
        verbose_name='54. Passou a ficar doente com frequência (dores crônicas, lesões ou doenças de pele, alterações hormonais, pressão alta, queda de cabelo, alterações da visão, ou outro sintoma físico)?',
        default=False
    )
    tremores_lembras = models.BooleanField(
        verbose_name='55. Tremores ao relembrar dos fatos?',
        default=False
    )
    coracao_ace_sexo_oposto = models.BooleanField(
        verbose_name='56. Coração acelerado (taquicardia) ou falta de ar quando alguém do sexo oposto chega próximo?',
        default=False
    )
    estado_desanimo = models.BooleanField(
        verbose_name='57. Estado de desânimo, apatia ou indiferença em ambientes de lazer?',
        default=False
    )
    sentir_incapaz = models.BooleanField(
        verbose_name='58. Passou a se sentir incapaz, fracassada ou sem valor?',
        default=False
    )
    olha_mundo_perigoso = models.BooleanField(
        verbose_name='59. Passou a ver o mundo como um lugar perigoso e não consegue confiar nas pessoas?',
        default=False
    )
    irritabilidade_constante = models.BooleanField(
        verbose_name='60. Passou a ter irritabilidade constante?',
        default=False
    )
    perdeu_vontade_viver_suicida = models.BooleanField(
        verbose_name='61. Perdeu a vontade de viver ou teve ideação suicida?',
        default=False
    )

    # Persistencia dos sintomas
    sintomas_persistem = models.TextField(
        verbose_name='Os sintomas ainda persistem? Descreva, apontando se há necessidade de atendimento ou encaminhamento da vítima.',
        null=True,
        blank=True,        
    )
    observacoes_profissional = models.TextField(
        verbose_name='Observações profissionais',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Formulario MP'
        verbose_name_plural = 'Formularios MP'
        ordering = ['data_solicitacao']
    def __str__(self):
        return f'Solicitação: {self.vitima} - ID: {self.ID}'