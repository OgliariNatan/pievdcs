# -*- coding: utf-8 -*-
#import openai #Precisa PAGAR
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



@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Poder Judiciário',])
def poder_judiciario(request):
    contexto = {
        'title': 'Poder Judiciário',
        'description': 'This page provides information about the judicial power.',
        'encaminhamentos': 5,
        'notificacoes': 4,
        'user': request.user,

    }
    return render(request, "judiciario_IA.html", contexto)

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


# @csrf_exempt
# def chat_ia(request):
#     if request.method == "POST":
#         msg = request.POST.get("mensagem", "")
#         resposta = f"Simulação de resposta jurídica para: '{msg}'"
#         html = f"""
#         <div class='flex justify-end'>
#             <div class='bg-purple-600 text-white rounded-xl p-3 max-w-xs'>{msg}</div>
#         </div>
#         <div class='flex items-start gap-2'>
#             <div class='w-7 h-7 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center'>
#                 <i class='fas fa-robot text-xs'></i>
#             </div>
#             <div class='bg-gray-100 rounded-xl p-3 max-w-xs'>{resposta}</div>
#         </div>
#         """
#         return HttpResponse(html)
    
@csrf_exempt
@login_required(login_url=reverse_lazy('login'))
def chat_ia(request):
    if request.method == "POST":
        pergunta = request.POST.get("mensagem", "").strip()
        
        if not pergunta:
            return HttpResponse("")
        
        # Modo de demonstração com respostas pré-definidas
        USE_DEMO_MODE = True  # Mude para False quando tiver a API key configurada
        
        if USE_DEMO_MODE:
            # Respostas simuladas baseadas em palavras-chave
            pergunta_lower = pergunta.lower()
            
            if "medida protetiva" in pergunta_lower or "medidas protetivas" in pergunta_lower:
                resposta_formatada = """A medida protetiva é um instrumento jurídico previsto na Lei Maria da Penha (Lei 11.340/2006) para proteger mulheres em situação de violência.
                <br><br><strong>Como solicitar:</strong>
                <br>• Procure uma Delegacia da Mulher ou delegacia comum
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
                resposta_formatada = """Para registrar uma denúncia de violência doméstica, você pode levar:
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
                resposta_formatada = """O acolhimento de vítimas de violência doméstica funciona através de uma rede de proteção:
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
                resposta_formatada = """Para denunciar violência doméstica:
                <br><br><strong>Onde denunciar:</strong>
                <br>• <strong>Emergência:</strong> Ligue 190
                <br>• <strong>Central da Mulher:</strong> Ligue 180 (24h, gratuito)
                <br>• <strong>Delegacia da Mulher:</strong> Atendimento especializado
                <br>• <strong>Delegacia comum:</strong> Na ausência de delegacia especializada
                <br>• <strong>Ministério Público:</strong> Denúncias diretas
                <br>• <strong>Online:</strong> Alguns estados têm delegacia virtual
                <br><br><strong>Importante:</strong>
                <br>• A denúncia pode ser anônima pelo 180
                <br>• Vizinhos e familiares também podem denunciar
                <br>• Em caso de flagrante, a polícia deve prender o agressor"""
            
            elif "tipo" in pergunta_lower and "violência" in pergunta_lower:
                resposta_formatada = """A Lei Maria da Penha reconhece 5 tipos de violência doméstica:
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
                resposta_formatada = """As vítimas de violência doméstica têm diversos direitos garantidos:
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
                resposta_formatada = f"""Entendo sua pergunta sobre: "<em>{pergunta}</em>"
                <br><br>Posso ajudar com informações sobre:
                <br>• <strong>Medidas protetivas</strong> - Como solicitar proteção judicial
                <br>• <strong>Documentos necessários</strong> - O que levar para denunciar
                <br>• <strong>Acolhimento</strong> - Rede de apoio disponível
                <br>• <strong>Tipos de violência</strong> - Física, psicológica, sexual, etc.
                <br>• <strong>Direitos da vítima</strong> - Garantias legais
                <br>• <strong>Como denunciar</strong> - Passo a passo
                <br><br>Por favor, seja mais específica ou escolha um dos tópicos acima."""
        
        else:
            # Código original com API (quando configurada)
            try:
                headers = {
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                }

                system_prompt = """Você é um assistente jurídico especializado em casos de violência doméstica contra a mulher no Brasil.
                
                Suas responsabilidades incluem:
                - Fornecer informações sobre a Lei Maria da Penha (Lei 11.340/2006)
                - Orientar sobre medidas protetivas de urgência
                - Explicar direitos das vítimas de violência doméstica
                - Informar sobre procedimentos de denúncia
                - Indicar redes de apoio e acolhimento
                - Esclarecer sobre tipos de violência (física, psicológica, sexual, patrimonial e moral)
                
                Responda de forma clara, empática e acolhedora. Use linguagem simples e evite jargões jurídicos complexos.
                Sempre priorize a segurança da vítima e indique buscar ajuda profissional quando necessário.
                
                NÃO forneça conselhos médicos ou psicológicos específicos.
                Em casos urgentes, sempre recomende ligar para 180 (Central de Atendimento à Mulher) ou 190 (Polícia)."""

                body = {
                    "model": "mistral/mistral-7b-instruct",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": pergunta}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500
                }

                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions", 
                    headers=headers, 
                    json=body,
                    timeout=30
                )
                
                if response.status_code != 200:
                    raise Exception(f"Erro na API: {response.status_code}")
                
                resposta_json = response.json()
                resposta = resposta_json['choices'][0]['message']['content']
                
                resposta_formatada = resposta.replace('\n', '<br>')

            except Exception as e:
                print(f"Erro no chat_ia: {str(e)}")
                resposta_formatada = """Desculpe, ocorreu um erro ao processar sua pergunta.
                <br><br>Enquanto isso, você pode:
                <br>• Ligar para <strong>180</strong> (Central de Atendimento)
                <br>• Em emergências, ligue <strong>190</strong>
                <br>• Procurar a Delegacia da Mulher mais próxima"""

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