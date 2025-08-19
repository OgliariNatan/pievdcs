from django.db import models
from datetime import datetime, timedelta, timezone
from usuarios.models import CustomUser
from sistema_justica.models.base import Vitima_dados, Agressor_dados, Filhos_dados, Municipio, Estado
from seguranca_publica.models.base import grau_parentesco_agressor_choices, status_MP_choices, tipo_de_violencia_choices
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
    
    tipo_de_violencia = models.CharField(
        max_length= 50, 
        choices= tipo_de_violencia_choices, 
        verbose_name= "Tipo de Violência",
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
        blank=True,  # Permita campo em branco para evitar erro de validação
        
    )
    
    bairro_mp = models.CharField(
        max_length=100,
        verbose_name='Bairro:',
        null=True, 
        blank=False
    )

    grau_parentesco_agressor = models.CharField(
        max_length=15,
        choices=grau_parentesco_agressor_choices,
        default='Conjuge',
        verbose_name="Grau de Parentesco com o Agressor"
    )

    filhos = ChainedManyToManyField(
        Filhos_dados,
        chained_field="agressor",
        chained_model_field="agressor",
        verbose_name='Filhos',
        blank=True,
        null=True
    )

    #Relacionado a parte 1: Condutas de violência psicológica
    critica_aparencia = models.BooleanField(
        default=False,
        verbose_name='Criticava sua aparência (corpo, cabelo, roupas)?'
    )

    proibia_make_roupas = models.BooleanField(
        default=False,
        verbose_name='Proibia você de usar roupas ou maquiagem?'
    )

    obrigava_pedir_desculpas = models.BooleanField(
        default=False,
        verbose_name='Obrigava você a pedir desculpas, mesmo quando não era sua culpa?'
    )

    fazer_nao_gosta = models.BooleanField(
        default=False,
        verbose_name='Constrangia você a fazer coisas que não gostava?'
    )

    comentario_situacao = models.TextField(
        verbose_name='Você gostaria de contar detalhes ou outra situação de constrangimento?',
        null=True,
        blank=True
    )

    # relacionado a parte 1: Condutas de humiliação e ridicularizaçÃO
    ridicularizava_sozinha = models.BooleanField(
        verbose_name='Ofendia, envergonhava ou ridicularizava você quando estavam sozinhos?',
        default=False
    )
    ridicularizava_terceiros = models.BooleanField(
        verbose_name='Ofendia, envergonhava ou ridicularizava você quando estavam na frente de outras pessoas?',
        default=False
    )

    humiliava_frente_filhos = models.BooleanField(
        verbose_name='Humilhava você na frente de seus filhos?',
        default=False
    )

    piadas_familia = models.BooleanField(
        verbose_name='Fazia piadas sobre ou você sua familia?',
        default=False
    )

    xingava_louca_burra = models.BooleanField(
        verbose_name='Xingava você de louca, burra, incapaz ou que não fazia nada direito?',
        default=False
    )

    apelidos_tristes= models.BooleanField(
        verbose_name='Criava apelidos para você, que a deixavam constrangida ou triste?',
        default=False
    )

    relato_constrangida = models.TextField(
        verbose_name='Você gostaria de contar mais detalhes ou mencionar alguma situação de humilhação ou ridicularização?',
        null=True,
        blank=True
    )

    # Condutas de Manipulação
    perdia_cabeca_culpava = models.BooleanField(
        verbose_name='Alegava que "perdia a cabeça" e culpava você?',
        default=False
    )

    culpava_ruim_voce = models.BooleanField(
        verbose_name='Culpava você por tudo de ruim que acontecia (desempego, dívidas e outros)?',
        default=False
    )

    insegurancas_capza = models.BooleanField(
        verbose_name='Usava seus medos e inseguranças dizendo que você não era capaz?',
        default=False
    )

    boa_dona_casa = models.BooleanField(
        verbose_name='Afirmava que você era uma boa "dona de casa", "boa mãe" e "esposa" para justificar o comportamento abusivo?',
        default=False
    ),
    
    ameaca_se_matar = models.BooleanField(
        verbose_name='Ameaçava que ia se matar ou matar seus filhos quando você tentava terminar a relação?',
        default=False
    ),
    
    invertia_fatos = models.BooleanField(
        verbose_name='Escondia, coisas invertia fatos e dizia que você estava louca?',
        default=False,
    ),

    detalhes_coisas = models.TextField(
        verbose_name='Você gostaria de contar mais detalhes ou alguma situação específica?',
        null=True,
        blank=True
    )

    # Condutas de isolamento ou limitacao
    dificula_contato_familia = models.BooleanField(
        verbose_name='Dificultava seu contato com familiares?',
        default=False,
    )
    telefone_familia_viva_voz = models.BooleanField(
        verbose_name='Quando seus familiares ligavam, obrigava você a colocar em viva voz?',
        default=False,
    )

    reclama_saia_sozinha = models.BooleanField(
        verbose_name='Reclamava quando você saía sozinha?',
        default=False
    )

    reclama_sozinha_estudar_trabalhar = models.BooleanField(
        verbose_name='Reclamava quando você saía para estudar ou trabalhar?',
        default=False,
    )

    bravo_conversa_homem = models.BooleanField(
        verbose_name='Ficava aborrecido ou bravo se você conversava com homens que não eram da família?',
        default=False
    )

    escolhia_amizade = models.BooleanField(
        verbose_name='Escolhia suas amizades?',
        default=False
    )

    controlava_distancia = models.BooleanField(
        verbose_name='Controlava você por mensagens, ligações ou de outro modo?',
        default=False
    )

    senhas_redes_sociais = models.BooleanField(
        verbose_name='Exigia que você lhe desse suas senhas em redes sociais?',
        default=False
    )

    ciumes_atencao_proximidade = models.BooleanField(
        verbose_name='Tinha ciúmes se alguma pessoa lhe desse atenção ou se aproximasse de você?',
        default=False
    )

    info_situa_isola = models.TextField(
        verbose_name='Você gostaria de contar mais detalhes ou outra situação de isolamento?',
        null=True,
        blank=True
    )

    # CONDUTAS AMEAÇADORAS Q27
    gritava_qualquer_coisa = models.BooleanField(
        verbose_name='Gritava ou explodia por qualquer coisa?',
        default=False
    )

    amante_paquera = models.BooleanField(
        verbose_name='Explodia por ciúmes, dizia que você tinha amantes ou estava paquerando?',
        default=False
    )

    escondia_coisas_pessoais = models.BooleanField(
        verbose_name='Destruía ou escondia suas coisas pessoais?',
        default=False
    )
    destruia_moveis_casa = models.BooleanField(
        verbose_name='Destruía móveis ou utensílios da casa?',
        default=False,
    )

    maltratava_animal_estimacao = models.BooleanField(
        verbose_name='Maltratava ou ameaçava seus animais de estimação?',
        default=False
    )

    contar_segredo = models.BooleanField(
        verbose_name='Ameaçava contar seus segredos pessoais ou divulgar fotos suas para outras pessoas?',
        default=False
    )

    deixar_sem_nada = models.BooleanField(
        verbose_name='Dizia que, se o deixasse, entraria com vários processos e ficaria sem nada?',
        default=False
    )

    exibia_armas = models.BooleanField(
        verbose_name='Exibia armas de fogo, facas ou objetos como forma de intimação?',
        default=False
    )

    detalhes_medo = models.TextField(
        verbose_name='Você gostaria de contar mais detalhes ou outra situação que lhe causava medo?',
        null=True,
        blank=True
    )

    # VIOLÊNCIA PSICOLÓGICA DIGITAL Q35






    class Meta:
        verbose_name = 'Formulario MP'
        verbose_name_plural = 'Formularios MP'
        ordering = ['data_solicitacao']
    def __str__(self):
        return f'Solicitação: {self.vitima} - ID: {self.ID}'