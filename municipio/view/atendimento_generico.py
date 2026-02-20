# municipio/view/atendimento_generico.py
def _dashboard_instituicao(request, instituicao_nome, grupo_permissao, template):
    """View genérica de dashboard para qualquer instituição municipal."""
    # Filtra atendimentos pela instituição do tipo_atendimento
    atendimentos = ModeloPenal.objects.filter(
        atendimento__instituicao_responsavel=instituicao_nome,
        usuario=request.user
    ).select_related('atendimento').prefetch_related('agressores_atendidos')
    # ... mesma lógica do penal()

def _cadastro_atendimento(request, instituicao_nome):
    """Cadastro genérico filtrado por instituição."""
    form = MunicipioAtendimentoForm(
        request.POST or None,
        instituicao=instituicao_nome
    )
    # ... mesma lógica

def _gerar_relatorio_pdf(request, grupo_id, instituicao_nome):
    """PDF genérico com cabeçalho da instituição."""
    # ... mesma lógica do gerar_relatorio_atendimento