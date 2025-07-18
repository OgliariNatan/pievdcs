# Script de Cadastro de Municípios por Estado

Este script automatiza o processo de cadastro de municípios brasileiros no banco de dados do sistema PIEVDCS, organizados por estado através de suas siglas.

## Funcionalidades

### 1. `cadastrar_municipios_por_estado()`
**Função principal** que cadastra municípios para cada estado baseando-se na sigla do estado.

**Características:**
- Só cadastra municípios que ainda não existem no banco de dados
- Evita duplicações verificando existência prévia
- Fornece feedback detalhado do processo
- Trata erros graciosamente
- Exibe estatísticas de resumo

**Exemplo de uso:**
```python
python manage.py shell
>>> from automacoes.atribui_municipio import cadastrar_municipios_por_estado
>>> cadastrar_municipios_por_estado()
```

### 2. `verificar_estados_cadastrados()`
Verifica quais estados estão cadastrados no banco de dados e quantos municípios cada um possui.

**Exemplo de uso:**
```python
>>> from automacoes.atribui_municipio import verificar_estados_cadastrados
>>> verificar_estados_cadastrados()
```

### 3. `atribuir_municipios()`
Função original mantida para compatibilidade com versões anteriores.

## Estados e Municípios Disponíveis

O script atualmente inclui municípios para os seguintes estados:
- **AC** (Acre): 22 municípios principais
- **AL** (Alagoas): 20 municípios principais  
- **AP** (Amapá): 16 municípios
- **AM** (Amazonas): 20 municípios principais

### Expandindo a Lista de Municípios

Para adicionar mais estados ou municípios, edite o dicionário `municipios_por_estado` no arquivo:

```python
municipios_por_estado = {
    "BA": {  # Bahia
        "Salvador",
        "Feira de Santana", 
        "Vitória da Conquista",
        # ... mais municípios
    },
    # Adicionar mais estados...
}
```

## Como Usar

### Opção 1: Django Shell
```bash
python manage.py shell
```

```python
# Importar funções
from automacoes.atribui_municipio import *

# Verificar estados existentes
verificar_estados_cadastrados()

# Cadastrar municípios
cadastrar_municipios_por_estado()
```

### Opção 2: Comando Direto
```bash
# Verificar estados
python manage.py shell -c "from automacoes.atribui_municipio import verificar_estados_cadastrados; verificar_estados_cadastrados()"

# Cadastrar municípios  
python manage.py shell -c "from automacoes.atribui_municipio import cadastrar_municipios_por_estado; cadastrar_municipios_por_estado()"
```

## Estrutura do Banco de Dados

O script trabalha com os modelos:
- **Estado**: Contém sigla e nome do estado
- **Municipio**: Contém nome do município e referência ao estado

## Recursos de Segurança

1. **Verificação de Duplicação**: Evita cadastrar municípios já existentes
2. **Tratamento de Erros**: Continua processamento mesmo se um estado não existir
3. **Feedback Detalhado**: Mostra progresso e estatísticas
4. **Rollback Automático**: Django gerencia transações automaticamente

## Log de Exemplo

```
Iniciando cadastro de municípios por estado...

Processando estado: Acre (AC)
  ✓ Cadastrado: Rio Branco
  ✓ Cadastrado: Cruzeiro do Sul
  - Já existe: Sena Madureira
  ...

📊 Resumo:
   Municípios cadastrados: 78
   Municípios já existentes: 0
   Total processado: 78
✅ Processo finalizado!
```

## Manutenção

Para manter o script atualizado:
1. Adicionar novos estados ao dicionário `municipios_por_estado`
2. Incluir municípios faltantes nos estados existentes
3. Verificar e corrigir nomes de municípios conforme IBGE
4. Testar regularmente com `verificar_estados_cadastrados()`

## Troubleshooting

**Erro "Estado não encontrado"**: 
- Verifique se o estado está cadastrado no banco com a sigla correta
- Use `verificar_estados_cadastrados()` para listar estados disponíveis

**Municípios duplicados**:
- A função automaticamente evita duplicações
- Para forçar recriação, delete os municípios existentes antes de executar

**Problemas de encoding**:
- O arquivo usa UTF-8, certificar que o terminal/IDE suporte caracteres especiais
