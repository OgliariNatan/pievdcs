from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Notificacao, StatusNotificacaoUsuario, StatusNotificacao
from .utils import enviar_notificacao_usuario, enviar_notificacao_grupo

@login_required
def listar_notificacoes(request):
    """Lista todas as notificações do usuário"""
    filtro = request.GET.get('filtro', 'todas')
    
    query = StatusNotificacaoUsuario.objects.filter(
        usuario=request.user
    ).select_related('notificacao')
    
    if filtro == 'nao_lidas':
        query = query.filter(status=StatusNotificacao.NAO_LIDA)
    elif filtro == 'prioritarias':
        query = query.filter(
            notificacao__prioridade__in=['ALTA', 'URGENTE']
        )
    
    query = query.order_by('-notificacao__prioridade', '-notificacao__data_criacao')
    
    paginator = Paginator(query, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filtro': filtro,
        'total_nao_lidas': StatusNotificacaoUsuario.objects.filter(
            usuario=request.user,
            status=StatusNotificacao.NAO_LIDA
        ).count()
    }
    
    return render(request, 'mensageria/listar_notificacoes.html', context)

@login_required
@require_POST
def marcar_como_lida(request, notificacao_id):
    """Marca uma notificação como lida"""
    try:
        status = StatusNotificacaoUsuario.objects.get(
            notificacao_id=notificacao_id,
            usuario=request.user
        )
        status.marcar_como_lida()
        return JsonResponse({'success': True})
    except StatusNotificacaoUsuario.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notificação não encontrada'})

@login_required
@require_POST
def marcar_todas_lidas(request):
    """Marca todas as notificações como lidas"""
    from django.utils import timezone
    
    StatusNotificacaoUsuario.objects.filter(
        usuario=request.user,
        status=StatusNotificacao.NAO_LIDA
    ).update(
        status=StatusNotificacao.LIDA,
        data_leitura=timezone.now()
    )
    
    return JsonResponse({'success': True})

@login_required
def contador_nao_lidas(request):
    """API endpoint para obter contagem de notificações não lidas"""
    total = StatusNotificacaoUsuario.objects.filter(
        usuario=request.user,
        status=StatusNotificacao.NAO_LIDA
    ).count()
    
    return JsonResponse({'total': total})