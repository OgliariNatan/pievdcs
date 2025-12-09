from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Notificacao, StatusNotificacao
from django.utils import timezone

@login_required
def listar_notificacoes(request):
    """Lista todas as notificações do usuário"""
    
    # Buscar todas as notificações do usuário (individuais e de grupo)
    notificacoes = Notificacao.get_todas_usuario(request.user)
    
    # Paginação
    paginator = Paginator(notificacoes, 20)  # 20 notificações por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Notificações',
        'notificacoes': page_obj,
        'total_nao_lidas': Notificacao.contar_nao_lidas_usuario(request.user)
    }
    return render(request, 'mensageria/notificacoes.html', context)

@login_required
@require_POST
def marcar_notificacao_lida(request, notificacao_id):
    """Marca uma notificação como lida"""
    try:
        notificacao = Notificacao.objects.get(id=notificacao_id)
        
        # Verificar se o usuário tem acesso a esta notificação
        if notificacao.destinatario_usuario == request.user:
            # Notificação individual
            notificacao.marcar_como_lida()
        elif notificacao.destinatario_grupo and request.user.groups.filter(id=notificacao.destinatario_grupo.id).exists():
            # Notificação de grupo
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
        
        # Verificar se o usuário tem acesso a esta notificação
        if notificacao.destinatario_usuario == request.user:
            # Notificação individual
            notificacao.arquivar()
        elif notificacao.destinatario_grupo and request.user.groups.filter(id=notificacao.destinatario_grupo.id).exists():
            # Notificação de grupo
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
    return JsonResponse({'status': 'success', 'message': 'Todas as notificações foram marcadas como lidas'})

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