# -*- coding: utf-8 -*-
#import openai #Precisa PAGAR
import ollama
from django.conf import settings
from django.shortcuts import render, redirect
import requests
import traceback
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .permission_group import grupos_permitidos
from ..forms.cadastros import CadastroVitimaForm, CadastroAgressorForm, CadastroMunicipioForm
from ..models.base import Vitima_dados, Agressor_dados, Filhos_dados, Municipio, Estado
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from mensageria.models import Notificacao, StatusNotificacao
from mensageria.utils import enviar_notificacao_usuario, enviar_notificacao_grupo
# 
from MAIN.decoradores.calcula_tempo import calcula_tempo

""" Configuraçao de decoradores para debug """
import os

var_debug = os.getenv('DEBUG')

if var_debug == 'True':
    from MAIN.decoradores.calcula_tempo import calcula_tempo, calcula_tempo_fun
    checked_debug_decorador = calcula_tempo
    checked_debug_decorador_fun = calcula_tempo_fun
    
else:
    checked_debug_decorador = None
    checked_debug_decorador_fun = None

""" Fim da configuraçao de decoradores para debug """




# Configuração do Ollama
OLLAMA_HOST = getattr(settings, 'OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_MODEL = getattr(settings, 'OLLAMA_MODEL', 'qwen2.5:7B')  # ou 'mixtral:latest', 'gemma3:27b', 'llama3.1:70b', 'llama3.1:latest', 'qwen3-vl:latest', 'gpt-oss:120b'


@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Poder Judiciário',])
def poder_judiciario(request):

    notificacoes_nao_lidas = Notificacao.contar_nao_lidas_usuario(request.user)
    #print(f'Notificações não lidas: {notificacoes_nao_lidas}')
    contexto = {
        'title': 'Poder Judiciário',
        'description': 'Informações e ações pertinentes ao poder Judiciário.',
        'encaminhamentos': 5,
        'notificacoes': notificacoes_nao_lidas,
        'user': request.user,

    }
    return render(request, "judiciario_IA.html", contexto)

@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
def cadastro_vitima_form(request):
    form = CadastroVitimaForm()
    return render(request, 'parcial/cadastro_vitima_form.html', {'form': form})


@login_required(login_url=reverse_lazy('login'))
def cadastro_vitima_submit(request):
    if request.method == 'POST':
        form = CadastroVitimaForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse(
                """
                    <script>
                        exibirPopupSucesso('Vítima cadastrada com sucesso!', 'feminino');
                        document.getElementById('modal-vitima').innerHTML = '';
                    </script>
                """
            )
    else:
        return render(request, "parcial/cadastro_vitima_form.html", {"form": form})
    return HttpResponse(status=405)

@checked_debug_decorador
@login_required(login_url=reverse_lazy('login'))
def cadastro_agressor_form(request):
    form = CadastroAgressorForm()
    return render(request, 'parcial/cadastro_agressor_form.html', {'form': form})

@login_required(login_url=reverse_lazy('login'))
def cadastro_agressor_submit(request):
    if request.method == 'POST':
        form = CadastroAgressorForm(request.POST)
        if form.is_valid():
            agressor = form.save()
            # Retorne um script para fechar o modal e recarregar o campo agressor do formulário de vítima
            return HttpResponse(
                """
                    <script>
                        exibirPopupSucesso('Agressor cadastrado com sucesso!', 'masculino');
                        document.getElementById('modal-agressor').innerHTML = '';
                        htmx.trigger(htmx.find('#id_agressor'), 'change');
                    </script>
                """
            )
        else:
            return render(request, 'parcial/cadastro_agressor_form.html', {'form': form})
    return HttpResponse(status=405)

@login_required(login_url=reverse_lazy('login'))
def cadastro_municipio_form(request):
    form = CadastroMunicipioForm()
    return render(request, 'parcial/cadastro_municipio_form.html', {'form': form})

@login_required(login_url=reverse_lazy('login'))
def cadastro_municipio_submit(request):
    if request.method == 'POST':
        form = CadastroMunicipioForm(request.POST)
        if form.is_valid():
            municipio = form.save()
            return HttpResponse("""
                <script>
                    document.getElementById('modal-municipio').innerHTML = '';
                    // Opcional: recarregar o campo municipio via HTMX
                    htmx.trigger(htmx.find('#id_municipio'), 'change');
                </script>
                <div class="alert alert-success">Município cadastrado com sucesso! Selecione-o na lista.</div>
            """)
        else:
            return render(request, 'parcial/cadastro_municipio_form.html', {'form': form})
    return HttpResponse(status=405)



def verificar_ollama_disponivel():
    """Verifica se o Ollama está rodando e acessível"""
    try:
        client = ollama.Client(host=OLLAMA_HOST)
        # Tenta listar modelos para verificar conexão
        models = client.list()
        if var_debug:
            nomes_modelos = [model['model'] for model in models['models']]
            print(f"Ollama está disponível. Modelos: {', '.join(nomes_modelos)}")
        return True
    except Exception as e:
        print(f"Ollama não está disponível: {e}")
        return False

def obter_resposta_ollama(pergunta):
    """Obtém resposta do modelo Ollama"""
    try:
        client = ollama.Client(host=OLLAMA_HOST)
        #print(f'cliente {client.list()}')
        # System prompt especializado para violência doméstica
        system_prompt = """Você é uma assistente especializada em casos de violência doméstica contra a mulher no Brasil.
        
        Suas responsabilidades incluem:
        - Fornecer informações sobre a Lei Maria da Penha (Lei 11.340/2006)
        - Orientar sobre medidas protetivas de urgência
        - Explicar direitos das vítimas de violência doméstica
        - Informar sobre procedimentos de denúncia
        - Indicar redes de apoio e acolhimento
        - Esclarecer sobre tipos de violência (física, psicológica, sexual, patrimonial e moral)
        - Indicar caso necessário denuncia via Defensoria Publica ou na Delegacia Virtual(https://delegaciavirtual.sc.gov.br/nova-ocorrencia)

        Responda de forma clara, empática e acolhedora. Use linguagem simples e evite jargões jurídicos complexos.
        Sempre priorize a segurança da vítima e indique buscar ajuda profissional quando necessário.
        
        Não forneça conselhos médicos ou psicológicos específicos.
        Em casos urgentes, sempre recomende ligar para 190 (Polícia) ou 180 (Central de Atendimento à Mulher).
        Se tiver lesionada informe assistência médica, através do SAMU 192 ou no hospital mais próximo.
        Denúncias on-line no site da [Delegacia Virtual (Registro de BO)](https://delegaciavirtual.sc.gov.br/nova-ocorrencia).

        Quando solicitar uma conversa oriente a entrar em contato através do whatsapp para o número [554832872635](https://api.whatsapp.com/send?phone=554832872635), serviço do Tribunal de Justiça de Santa Catarina.

        [
        Quando citado o corte da pensão alimentícia, informe que se encaixa na violência vicária.
        Conceito de Violência Vicária:
        A violência vicária (ou violência por procuração) é uma forma grave de violência doméstica e de gênero, na qual o agressor (geralmente o ex-parceiro) utiliza uma terceira pessoa — predominantemente os filhos, mas também outros entes queridos ou animais de estimação — como "instrumento" ou "arma" para causar sofrimento e dano psicológico à vítima principal (a mulher).
        Pontos-chave a considerar:
        Objetivo Principal: O objetivo central não é a agressão direta à vítima principal, mas sim infligir a dor mais profunda e duradoura possível, atingindo o que ela mais ama ou valoriza.
        Instrumentalização: A vítima secundária (ex: o filho) é vista como um objeto ou meio para atingir a vítima principal.
        Contexto: Frequentemente ocorre em processos de separação litigiosa, disputas de guarda e após o término do relacionamento, quando o agressor perde o controle direto sobre a vítima.
        ]

        Formate suas respostas usando HTML básico:
        - Use <a href=""> para links
        - Use <strong> para destacar informações importantes
        - Use <br> para quebras de linha
        - Use <p> para parágrafos
        - Organize listas com • seguido de espaço
        - Evite usar listas numeradas

        Porque o nome de LaelIA?
        Laelia é um tipo de orquídea conhecida por sua beleza e resiliência, simbolizando a força e a delicadeza das mulheres que enfrentam a violência doméstica e simbolo oficial do estado de Santa Catarina. O nome LaelIA reflete a missão da assistente virtual de oferecer apoio, informação e empoderamento às vítimas, ajudando-as a florescer apesar das adversidades que enfrentam.
        """
        
        # Cria o prompt completo
        prompt_completo = f"{system_prompt}\n\nUsuário: {pergunta}\n\nLaelIA:"
        
        # Faz a chamada ao Ollama
        response = client.generate(
            model=OLLAMA_MODEL,
            prompt=prompt_completo,
            system='Seu nome é Lael<b>IA</b>, uma assistente virtual especializada em violência doméstica contra a mulher no Brasil.',
            context=[1, 2, 3],  # Mantém o contexto das últimas interações
            stream=False,# Se True, recebe a resposta em partes (streaming)

            options={
                'temperature': 0.4,  # Baixo para respostas mais focadas 
                'num_predict': 800,  # tamanho da resposta
                'seed': None,
                'top_p': 0.7, # Inicial 0.9
                'top_k': 20,
                'repeat_penalty': 1.2,
                'num_ctx': 4096,
                #'stop': ['\n\nUsuário:', '\n\Laelia:', 'FIM'],
                'num_gpu':1,
                'mirostat': 2,
                'mirostat_tau': 5.0,
            },
            keep_alive='5m',
        )
        
        # Extrai a resposta
        resposta = response['response']
        
        # Formata a resposta para HTML
        resposta_formatada = resposta.replace('\n\n', '<br><br>').replace('\n', '<br>')
        
        # Adiciona formatação para listas
        linhas = resposta_formatada.split('<br>')
        linhas_formatadas = []
        for linha in linhas:
            if linha.strip().startswith('- '):
                linha = '• ' + linha.strip()[2:]
            linhas_formatadas.append(linha)
        resposta_formatada = '<br>'.join(linhas_formatadas)
        
        return resposta_formatada
        
    except Exception as e:
        print(f"Erro ao chamar Ollama: {e}")
        return None

def obter_resposta_demo(pergunta):
    """Respostas demo quando Ollama não está disponível"""
    pergunta_lower = pergunta.lower()
    
    if "medida protetiva" in pergunta_lower or "medidas protetivas" in pergunta_lower:
        return """A medida protetiva é um instrumento jurídico previsto na Lei Maria da Penha (Lei 11.340/2006) para proteger mulheres em situação de violência.
        <br><br><strong>Como solicitar:</strong>
        <br>• Procure a Defensoria Pública ou;
        <br>• Procure uma Delegacia da Mulher, Delegacia comum ou [Delegacia Virtual](https://delegaciavirtual.sc.gov.br/nova-ocorrencia).
        <br>• Relate os fatos e peça a medida protetiva
        <br>• Não é necessário advogado
        <br>• O juiz tem 48h para decidir
        <br><br><strong>O que pode incluir:</strong>
        <br>• Afastamento do agressor do lar
        <br>• Proibição de aproximação (mínimo 200m)
        <br>• Proibição de contato por qualquer meio
        <br>• Suspensão de porte de arma
        <br>• Prestação de alimentos provisórios"""
    
    elif "documento" in pergunta_lower or "documentos" in pergunta_lower:
        return """Para registrar uma denúncia de violência doméstica, você pode levar:
        <br><br><strong>Documentos úteis:</strong>
        <br>• RG e CPF (seus e do agressor, se tiver)
        <br>• Comprovante de residência
        <br>• Certidão de nascimento dos filhos
        <br>• Fotos de lesões ou danos
        <br>• Mensagens, e-mails ou áudios ameaçadores
        <br>• Laudos médicos (se houver)
        <br>• Boletins de ocorrência anteriores
        <br><br><strong>Importante:</strong> Mesmo sem documentos, você pode e deve denunciar! A palavra da vítima tem valor especial nos casos de violência doméstica."""
    
    elif "acolhimento" in pergunta_lower:
        return """O acolhimento de vítimas de violência doméstica funciona através de uma rede de proteção:
        <br><br><strong>Serviços disponíveis:</strong>
        <br>• <strong>Casa-abrigo:</strong> Local sigiloso e seguro para vítimas em risco
        <br>• <strong>Centro de Referência da Mulher:</strong> Atendimento psicológico, social e jurídico
        <br>• <strong>CRAS/CREAS:</strong> Assistência social e encaminhamentos
        <br>• <strong>Defensoria Pública:</strong> Assistência jurídica gratuita
        <br><br><strong>Como acessar:</strong>
        <br>• Ligue 180 (Central de Atendimento à Mulher)
        <br>• Procure a Delegacia da Mulher
        <br>• Vá ao CREAS mais próximo
        <br>• Busque o Centro de Referência da sua cidade"""
    
    elif "denunc" in pergunta_lower or "denúncia" in pergunta_lower:
        return """Para denunciar violência doméstica:
        <br><br><strong>Onde denunciar:</strong>
        <br>• <strong>Emergência:</strong> Ligue 190
        <br>• <strong>Central da Mulher:</strong> Ligue 180 (24h, gratuito)
        <br>• <strong>Delegacia da Mulher:</strong> Atendimento especializado
        <br>• <strong>Delegacia comum:</strong> Na ausência de delegacia especializada
        <br>• <strong>Delegacia Virtual:</strong> Registro de BO online
        <br>• <strong>Defensoria Pública:</strong> Assistência jurídica gratuita
        <br>• <strong>Ministério Público:</strong> Denúncias diretas
        <br>• <strong>Online:</strong> Alguns estados têm delegacia virtual
        <br><br><strong>Importante:</strong>
        <br>• A denúncia pode ser anônima pelo 180
        <br>• Vizinhos e familiares também podem denunciar
        <br>• Em caso de flagrante, a polícia deve prender o agressor"""
    
    elif "tipo" in pergunta_lower and "violência" in pergunta_lower:
        return """A Lei Maria da Penha reconhece 5 tipos de violência doméstica:
        <br><br><strong>1. Violência Física:</strong>
        <br>• Tapas, socos, empurrões, chutes
        <br>• Arremesso de objetos, queimaduras
        <br>• Uso de armas
        <br><br><strong>2. Violência Psicológica:</strong>
        <br>• Humilhações, xingamentos, ameaças
        <br>• Isolamento de amigos e familiares
        <br>• Controle excessivo
        <br><br><strong>3. Violência Sexual:</strong>
        <br>• Relação sexual forçada
        <br>• Impedir uso de contraceptivos
        <br>• Forçar aborto ou gravidez
        <br><br><strong>4. Violência Patrimonial:</strong>
        <br>• Destruir objetos pessoais
        <br>• Reter documentos
        <br>• Controlar dinheiro
        <br><br><strong>5. Violência Moral:</strong>
        <br>• Calúnia, difamação, injúria
        <br>• Expor a vida íntima"""
    
    elif "direito" in pergunta_lower:
        return """As vítimas de violência doméstica têm diversos direitos garantidos:
        <br><br><strong>Direitos principais:</strong>
        <br>• Atendimento prioritário e especializado
        <br>• Medidas protetivas de urgência
        <br>• Assistência jurídica gratuita
        <br>• Atendimento médico e psicológico
        <br>• Abrigamento sigiloso quando em risco
        <br>• Afastamento do trabalho por até 6 meses
        <br>• Prioridade para transferir matrícula escolar dos filhos
        <br>• Inclusão em programas sociais
        <br><br><strong>Na delegacia:</strong>
        <br>• Ser atendida por policial mulher (quando possível)
        <br>• Registrar ocorrência em local reservado
        <br>• Não ser questionada sobre sua vida íntima
        <br>• Receber cópia do B.O. imediatamente"""
    
    else:
        return f"""Entendo sua pergunta sobre: "<em>{pergunta}</em>"
        <br><br>Posso ajudar com informações sobre:
        <br>• <strong>Medidas protetivas</strong> - Como solicitar proteção judicial
        <br>• <strong>Documentos necessários</strong> - O que levar para denunciar
        <br>• <strong>Acolhimento</strong> - Rede de apoio disponível
        <br>• <strong>Tipos de violência</strong> - Física, psicológica, sexual, etc.
        <br>• <strong>Direitos da vítima</strong> - Garantias legais
        <br>• <strong>Como denunciar</strong> - Passo a passo
        <br><br>Por favor, seja mais específica ou escolha um dos tópicos acima."""

@checked_debug_decorador
@csrf_exempt
@login_required(login_url=reverse_lazy('login'))
def chat_ia(request):
    if request.method == "POST":
        pergunta = request.POST.get("mensagem", "").strip()
        
        if not pergunta:
            return HttpResponse("")
        
        # Configuração para usar Ollama ou modo demo
        USE_OLLAMA = getattr(settings, 'USE_OLLAMA', True)
        
        resposta_formatada = None
        usando_ollama = False
        
        # Tenta usar Ollama primeiro
        if USE_OLLAMA and verificar_ollama_disponivel():
            resposta_formatada = obter_resposta_ollama(pergunta)
            if resposta_formatada:
                usando_ollama = True
        
        # Se Ollama falhou ou não está configurado, usa respostas demo
        if not resposta_formatada:
            resposta_formatada = obter_resposta_demo(pergunta)
        
        # Adiciona indicador de qual sistema está sendo usado (opcional)
        fonte_resposta = ""
        if settings.DEBUG:
            if usando_ollama:
                fonte_resposta = f"""
                <div class='text-xs text-green-600 mt-2'>
                    <i class='fas fa-robot mr-1'></i>
                    Resposta gerada por IA local (Ollama - {OLLAMA_MODEL})
                </div>
                """
            else:
                fonte_resposta = """
                <div class='text-xs text-orange-600 mt-2'>
                    <i class='fas fa-info-circle mr-1'></i>
                    Resposta pré-definida (Ollama indisponível)
                </div>
                """
        
        # Retorna HTML com as mensagens formatadas
        html_response = f"""
            <!-- Mensagem do usuário -->
            <div class='flex justify-end mb-3'>
                <div class='bg-purple-600 text-white rounded-xl p-3 max-w-[80%] shadow-md'>
                    <p class='text-sm'>{pergunta}</p>
                </div>
            </div>
            
            <!-- Resposta do assistente -->
            <div class='flex items-start gap-2 mb-3'>
                <div class='w-8 h-8 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center flex-shrink-0'>
                    <i class='fas fa-robot text-sm'></i>
                </div>
                <div class='bg-white rounded-xl p-4 max-w-[80%] shadow-md border border-gray-100'>
                    <p class='text-sm text-gray-700 leading-relaxed'>{resposta_formatada}</p>
                    
                    {fonte_resposta}
                    
                    <!-- Números de emergência sempre visíveis -->
                    <div class='mt-3 pt-3 border-t border-gray-200'>
                        <p class='text-xs text-gray-500'>
                            <i class='fas fa-phone-alt mr-1'></i>
                            Emergência: <strong>190</strong> | 
                            Central da Mulher: <strong>180</strong>
                        </p>
                    </div>
                </div>
            </div>
        """
        
        return HttpResponse(html_response)
    
    return HttpResponse(status=405)