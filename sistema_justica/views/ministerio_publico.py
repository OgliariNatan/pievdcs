from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.models import Group
from django.http import HttpResponseForbidden



def grupos_permitidos(Group):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.groups.filter(name__in=Group).exists():
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("Você não tem permissão para acessar esta página. <br> Entre em contato com o administrador do sistema.")
        _wrapped_view.__name__ = view_func.__name__
        return _wrapped_view
    return decorator

@login_required(login_url=reverse_lazy('login'))
@grupos_permitidos(['Ministério Público', 'Policia Penal', 'Poder Judiciário'])
def ministerio_publico(request):
    contexto = {
        'title': 'Ministério Público',
        'description': 'This page provides information about the public ministry.',
        'encaminhamentos': 5,
        'notificacoes': 2,
        'user': request.user,
    }
    return render(request, "ministerio_publico.html", contexto)