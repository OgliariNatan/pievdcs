# -*- coding: utf-8 -*-
"""
Views do sistema de mensageria/notificações
dir: mensageria/views.py
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Notificacao, StatusNotificacao


@login_required
def listar_notificacoes(request):
    """Lista todas as notificações do usuário com filtros"""
    filtro = request.GET.get('filtro', 'todas')

    if filtro == 'nao_lidas':
        notificacoes = Notificacao.get_nao_lidas_usuario(request.user)
    elif filtro == 'prioritarias':
        notificacoes = Notificacao.get_nao_lidas_usuario(request.user).filter(
            Q(prioridade='URGENTE') | Q(prioridade='ALTA') | Q(importante=True)
        )
    else:
        notificacoes = Notificacao.get_todas_usuario(request.user)

    for notif in notificacoes:
        notif.status = notif.get_status_para_usuario(request.user)

    paginator = Paginator(notificacoes, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'title': 'Notificações',
        'notificacoes': page_obj,
        'filtro': filtro,
        'total_nao_lidas': Notificacao.contar_nao_lidas_usuario(request.user),
    }
    return render(request, 'mensageria/notificacoes.html', context)


@login_required
@require_POST
def marcar_notificacao_lida(request, notificacao_id):
    """Marca uma notificação como lida"""
    try:
        notificacao = Notificacao.objects.get(id=notificacao_id)
        if notificacao.destinatario_usuario == request.user:
            notificacao.marcar_como_lida()
        elif notificacao.destinatario_grupo and request.user.groups.filter(
            id=notificacao.destinatario_grupo.id
        ).exists():
            notificacao.marcar_lida_por_usuario(request.user)
        else:
            return JsonResponse({'status': 'error', 'message': 'Sem permissão'}, status=403)
        return JsonResponse({'status': 'success'})
    except Notificacao.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Notificação não encontrada'}, status=404)


@login_required
@require_POST
def arquivar_notificacao(request, notificacao_id):
    """Arquiva uma notificação"""
    try:
        notificacao = Notificacao.objects.get(id=notificacao_id)
        if notificacao.destinatario_usuario == request.user:
            notificacao.arquivar()
        elif notificacao.destinatario_grupo and request.user.groups.filter(
            id=notificacao.destinatario_grupo.id
        ).exists():
            notificacao.arquivar_por_usuario(request.user)
        else:
            return JsonResponse({'status': 'error', 'message': 'Sem permissão'}, status=403)
        return JsonResponse({'status': 'success'})
    except Notificacao.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Notificação não encontrada'}, status=404)


@login_required
@require_POST
def marcar_todas_lidas(request):
    """Marca todas as notificações do usuário como lidas"""
    from .utils import marcar_todas_como_lidas
    marcar_todas_como_lidas(request.user)
    return JsonResponse({'status': 'success', 'message': 'Todas marcadas como lidas'})


@login_required
def api_contador_notificacoes(request):
    """API para obter o contador de notificações não lidas"""
    count = Notificacao.contar_nao_lidas_usuario(request.user)
    return JsonResponse({'count': count})


@login_required
def api_notificacoes_recentes(request):
    """API para obter notificações recentes"""
    notificacoes = Notificacao.get_nao_lidas_usuario(request.user)[:5]
    data = []
    for notif in notificacoes:
        data.append({
            'id': notif.id,
            'titulo': notif.titulo,
            'mensagem': notif.mensagem[:100] + '...' if len(notif.mensagem) > 100 else notif.mensagem,
            'tipo': notif.tipo,
            'prioridade': notif.prioridade,
            'icone': notif.get_icone_tipo(),
            'cor': notif.get_cor_prioridade(),
            'data_criacao': notif.data_criacao.isoformat(),
            'remetente': notif.remetente.get_full_name() if notif.remetente else 'Sistema'
        })
    return JsonResponse({'notificacoes': data})


@login_required
def popup_notificacoes(request):
    """Retorna o popup de notificações recentes via HTMX"""
    notificacoes_recentes = Notificacao.get_nao_lidas_usuario(request.user)[:8]
    for notif in notificacoes_recentes:
        notif.status = notif.get_status_para_usuario(request.user)

    context = {
        'notificacoes_recentes': notificacoes_recentes,
        'total_nao_lidas': Notificacao.contar_nao_lidas_usuario(request.user),
    }
    # Corrigido: path sem subpasta extra
    return render(request, 'parcial/popup_notificacoes.html', context)


@login_required
def enviar_notificacao_view(request):
    """Exibe popup e processa envio de notificação via HTMX"""
    from .forms import EnviarNotificacaoForm
    from .utils import enviar_notificacao_usuario, enviar_notificacao_grupo

    if request.method == 'POST':
        form = EnviarNotificacaoForm(request.POST)
        if form.is_valid():
            tipo_dest = form.cleaned_data['tipo_destinatario']
            kwargs = {
                'request': request,
                'titulo': form.cleaned_data['titulo'],
                'mensagem': form.cleaned_data['mensagem'],
                'tipo': form.cleaned_data['tipo'],
                'prioridade': form.cleaned_data['prioridade'],
                'importante': form.cleaned_data['importante'],
            }

            if tipo_dest == 'grupo':
                enviar_notificacao_grupo(
                    grupo_destinatario=form.cleaned_data['destinatario_grupo'],
                    **kwargs
                )
            else:
                enviar_notificacao_usuario(
                    usuario_destinatario=form.cleaned_data['destinatario_usuario'],
                    **kwargs
                )

            response = HttpResponse('<div id="modal-enviar-notificacao"></div>')
            response['HX-Trigger'] = '{"notificacaoEnviada": "Notificação enviada com sucesso!"}'
            return response

        return render(request, 'parcial/enviar_notificacao.html', {'form': form})

    form = EnviarNotificacaoForm()
    return render(request, 'parcial/enviar_notificacao.html', {'form': form})