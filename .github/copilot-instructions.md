# PIEVDCS - Instruções do Copilot

## Visão Geral do Projeto
**PIEVDCS** (Plataforma Integrada de Enfrentamento à Violência Doméstica e Crimes Sexuais) é uma plataforma SaaS baseada em Django para combater violência doméstica e crimes sexuais no Brasil. Integra forças de segurança pública, núcleos municipais de atenção à família, Ministério Público, Defensoria Pública e Poder Judiciário.

## Arquitetura e Organização

### Estrutura Principal dos Apps Django
- `MAIN/` - App central com dashboard, relatórios, autenticação e modelos compartilhados
- `sistema_justica/` - Sistema de justiça (Judiciário, Ministério Público, Defensoria Pública)
- `seguranca_publica/` - Segurança pública (Polícia Militar, Polícia Civil, Polícia Penal)
- `municipio/` - Serviços municipais (CRAS, CAPS, Conselhos Municipais)
- `usuarios/` - Gerenciamento de usuários e permissões

### Padrões de Design do Banco de Dados
- **PostgreSQL** com locale brasileiro UTF-8 (`pt_BR.UTF-8`)
- Modelos orientados por domínio em arquivos separados (ex: `sistema_justica/models/base.py`, `poder_judiciario.py`)
- Chaves estrangeiras encadeadas usando `smart_selects` para relacionamentos Estado→Município
- Tuplas de escolhas padronizadas: `sexo_choices`, `escolaridade_choices`, `etnia_choices`, `classeEconomica_choices`

### Modelos de Dados Principais
```python
# Estrutura principal de dados da vítima em sistema_justica/models/base.py
class Vitima_dados(models.Model):  # Nomenclatura em português brasileiro
    nome = models.CharField(max_length=250, verbose_name="Nome Completo*")
    cpf = models.CharField(max_length=14, verbose_name="CPF*")
    data_nascimento = models.DateField(verbose_name="Data de Nascimento*")
    # Usa ForeignKeys encadeadas Estado/Município
```

## Fluxos de Desenvolvimento

### Configuração do Ambiente
```bash
# Criar ambiente virtual
python -m venv virtual_pievdcs
# Atualizar requirements após novos pacotes
pip freeze > requirements.txt
```

### Operações do Banco de Dados
```bash
python manage.py makemigrations
python manage.py migrate
# Carregar dados iniciais usando scripts de automação
python manage.py shell
>>> from automacoes.cria_estados import criar_estados
>>> criar_estados()
>>> from automacoes.cria_municipios import cadastrar_municipios_por_estado
>>> cadastrar_municipios_por_estado()
```

### Servidor de Desenvolvimento*
```bash
python manage.py runserver 10.40.22.110:8000 # Padrão: http://127.0.0.1:8000
```

## Convenções Específicas do Projeto

### Localização Brasileira
- Todos os modelos usam nomes de campos em português brasileiro (`nome`, `cpf`, `data_nascimento`)
- Nomes verbosos em português: `verbose_name="Nome Completo*"`
- Fuso horário: `America/Sao_Paulo`
- Locale: `pt_BR.UTF-8`

### Estrutura de Templates
- Estende padrão `base/base.html`
- Usa TailwindCSS para estilização com configuração customizada nos templates
- Interações dinâmicas com jQuery
- Gráficos JavaScript com Chart.js e mapas Leaflet.js
- Herança de templates: `{% extends "base/base.html" %}` → `{% block main_content %}`

### Organização de Arquivos Estáticos
```
staticfiles/
├── admin/
├── css/
├── estados_municipio/  # Dados geográficos
├── img/
├── js/
└── rest_framework/
```

### Segurança e Configuração
- Usa `python-decouple` para variáveis de ambiente
- Middleware personalizado de logging em `MAIN/middleware/logs_pers.py`
- Gerenciamento de sessão: timeout de 150min, expiração ao fechar navegador
- Proteção CSRF com `CSRF_COOKIE_HTTPONLY = True`

### Padrões de Visualização de Dados
- Dashboard em `relatorios.html` com múltiplas visualizações Chart.js
- Mapas Leaflet.js com marcadores coloridos por tipo de violência
- Funções personalizadas de cor: `getCorPorTipoViolencia()`, `criarIconeColorido()`
- Geração de cores para gráficos: `gerarCoresHSL(qtd)` para paletas dinâmicas

## Pontos de Integração

### Fluxo de Dados Geográficos
- Estados/Municípios carregados via scripts de automação a partir de GeoJSON
- Smart selects para dropdowns dependentes (Estado→Município)
- Coordenadas de mapa armazenadas para visualizações do dashboard

### Comunicação Entre Aplicações
- Modelos compartilhados em `sistema_justica.models.base`
- Roteamento de URL delegado para `urls.py` específicos de cada app
- Diretórios de templates configurados por app em `TEMPLATES.DIRS`

### Endpoints da API
- Django REST Framework configurado com renderização apenas JSON
- CORS habilitado para requisições cross-domain
- Logging personalizado de API via middleware

## Arquivos Críticos para Compreensão da IA
- `sistema_justica/models/base.py` - Modelos de domínio principais e escolhas
- `MAIN/templates/relatorios.html` - Dashboard com visualizações complexas
- `MAIN/settings.py` - Configuração completa do Django
- `automacoes/` - Scripts de carregamento de dados para configuração inicial
- `requirements.txt` - Dependências da pilha tecnológica

## Notas de Desenvolvimento
- Projeto usa GitHub Projects para rastreamento de issues
- Desenvolvimento baseado em branches (sem commits diretos na main)
- Cada instituição deve ter sua própria aplicação Django
- Todos os apps devem incluir um `README.md`
- Autenticação personalizada de usuário com permissões baseadas em instituição
