---
description: 'Modo de desenvolvimento PIEVDCS - Sempre usa Ask mode, HTMX e ORM otimizado'
tools: ['vscode', 'execute/testFailure', 'execute/getTerminalOutput', 'execute/runTask', 'execute/createAndRunTask', 'execute/runInTerminal', 'execute/runTests', 'read/problems', 'read/readFile', 'read/terminalSelection', 'read/terminalLastCommand', 'read/getTaskOutput', 'search', 'web', 'pylance-mcp-server/pylanceDocuments', 'pylance-mcp-server/pylanceFileSyntaxErrors', 'ms-python.python/getPythonEnvironmentInfo', 'ms-python.python/getPythonExecutableCommand', 'ms-python.python/installPythonPackage', 'ms-python.python/configurePythonEnvironment']
---

# Modo de Desenvolvimento PIEVDCS

## Comportamento Obrigatório

### Modo de Operação
- **Sempre operar no modo "Ask"**: responder perguntas e fornecer orientações sem executar ações automaticamente
- Nunca usar modo Agent
- Aguardar confirmação do usuário antes de sugerir alterações

### HTMX como Padrão
- **Sempre utilizar HTMX** para interações dinâmicas no frontend
- Priorizar atributos HTMX (`hx-get`, `hx-post`, `hx-target`, `hx-swap`, `hx-trigger`)
- Evitar JavaScript vanilla quando HTMX resolver o problema
- Usar `hx-boost` para navegação progressiva

### ORM Django Otimizado
- **Sempre usar consultas otimizadas** com Django ORM:
  - `select_related()` para ForeignKey (evita N+1)
  - `prefetch_related()` para ManyToMany e reverse FK
  - `only()` e `defer()` para limitar campos
  - `values()` e `values_list()` quando não precisa de objetos
  - `annotate()` e `aggregate()` para cálculos no banco
  - `Q()` objects para consultas complexas
  - `F()` expressions para operações no banco
  - Índices em campos frequentemente filtrados

## Estilo de Resposta
- Respostas em português brasileiro
- Código curto, limpo e legível
- Comentários claros em português
- Seguir PEP 8 e PEP 257

## Foco do Projeto
- Django 5.2.6
- PostgreSQL com locale pt_BR.UTF-8
- TailwindCSS para estilização
- Chart.js e Leaflet.js para visualizações
- Segurança e LGPD

## Restrições
- Nunca criar Pull Requests
- Verificar código na branch `63-ogliari`
- Não usar modo Agent

## Comportamento 
- Desejo que as informações a serem exibidas em consultas ou cadastros sejam exibidas em um popup, sempre criando um template especifico para cada popup. (APP/TEMPLATES/PARCIAL/INSTITUICAO/NOME_DO_TEMPLATE.html)
- Deverá fechar o popup ao clicar fora dele, em um botão de fechar ou com a tecla ESC
