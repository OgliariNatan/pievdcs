# Gerador de Agressores - PIEVDCS

Este script cria dados fictícios de agressores para popular o banco de dados do sistema PIEVDCS durante o desenvolvimento e testes.

## 📋 Pré-requisitos

Antes de executar o script, certifique-se de que:

1. **Estados e municípios estão carregados:**
   ```bash
   python manage.py shell
   >>> from automacoes.cria_estados import criar_estados
   >>> criar_estados()
   >>> from automacoes.cria_municipios import cadastrar_municipios_por_estado  
   >>> cadastrar_municipios_por_estado()
   ```

2. **Banco de dados está configurado:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

## 🚀 Como usar

### Criar 1000 agressores (padrão)
```bash
python manage.py shell
>>> from automacoes.gera_agressores import criar_agressores_aleatorios
>>> criar_agressores_aleatorios()
```

### Criar quantidade específica
```bash
>>> criar_agressores_aleatorios(500)  # Cria 500 agressores
```

### Ver estatísticas
```bash
>>> from automacoes.gera_agressores import estatisticas_agressores
>>> estatisticas_agressores()
```

### Limpar todos os agressores (CUIDADO!)
```bash
>>> from automacoes.gera_agressores import limpar_agressores_teste
>>> limpar_agressores_teste()
```

## 📊 Dados gerados

O script cria agressores com dados realísticos incluindo:

### 👤 Informações pessoais
- **Nome completo**: Combinações de nomes masculinos brasileiros comuns (80% masculino, 15% feminino, 5% outro)
- **CPF**: Gerado automaticamente com dígitos verificadores válidos
- **Data de nascimento**: Idades entre 18 e 85 anos
- **Sexo**: M (Masculino - predominante), F (Feminino), O (Outro)
- **Etnia**: Branca, Preta, Parda, Amarela, Indígena
- **Estado civil**: Solteiro, Casado, Divorciado, Viúvo, etc.

### 📞 Contato
- **Telefone**: Formato brasileiro com DDD real: (XX) XXXXX-XXXX
- **Email**: 30% dos agressores têm email gerado automaticamente

### 🏠 Endereço
- **Estado/Município**: Selecionados aleatoriamente dos cadastrados
- **Bairro**: Lista de bairros fictícios comuns
- **Rua**: Nomes de ruas típicos brasileiros
- **Número**: Números de 1 a 9999

### 💼 Informações socioeconômicas
- **Escolaridade**: Desde "Não Alfabetizado" até "Pós-Graduação"
- **Classe econômica**: 6 faixas de renda conforme padrão brasileiro
- **Profissão**: Lista de profissões comuns masculinas e femininas

## 🎯 Características específicas dos agressores

- **Distribuição de gênero realística**: 80% masculino, 15% feminino, 5% outros
- **Profissões típicas masculinas**: Pedreiro, Motorista, Mecânico, Soldador, Segurança, etc.
- **Profissões femininas**: Para agressoras mulheres - Doméstica, Professora, Vendedora, etc.
- **Menor taxa de email**: Apenas 30% têm email (vs. 50% das vítimas)
- **Faixa etária ampliada**: Até 85 anos para refletir agressores mais velhos

## 📈 Exemplo de saída

```
🚀 Iniciando criação de 1000 agressores aleatórios...
📊 Estados disponíveis: 27
📊 Municípios disponíveis: 5570
📝 Progresso: 100/1000 agressores criados...
📝 Progresso: 200/1000 agressores criados...
...
📝 Progresso: 1000/1000 agressores criados...

============================================================
📊 RELATÓRIO FINAL - GERAÇÃO DE AGRESSORES
============================================================
✅ Agressores criados com sucesso: 1000
❌ Erros encontrados: 0
📈 Taxa de sucesso: 100.0%
📋 Total de agressores no sistema: 1000

🎯 ESTATÍSTICAS DOS DADOS GERADOS:
👥 Distribuição por sexo:
   Masculino: 798 agressores
   Feminino: 152 agressores
   Outro: 50 agressores

📍 Estados com mais agressores:
   SP: 189 agressores
   MG: 137 agressores
   RJ: 91 agressores
   RS: 74 agressores
   PR: 67 agressores

💰 Distribuição por classe econômica:
   De R$1.518,01 a R$3.636,00: 203 agressores
   Abaixo de R$1.518,00: 187 agressores
   Sem Renda: 165 agressores
   ...
```

## 🔍 Diferenças em relação às vítimas

| Aspecto                 | Vítimas               | Agressores                   |
| ----------------------- | --------------------- | ---------------------------- |
| **Gênero predominante** | 100% feminino         | 80% masculino                |
| **Nomes**               | Lista feminina        | Lista masculina/feminina     |
| **Profissões**          | Tipicamente femininas | Predominantemente masculinas |
| **Email**               | 50% têm email         | 30% têm email                |
| **Faixa etária**        | 18-80 anos            | 18-85 anos                   |

## ⚠️ Importante

- **Apenas para desenvolvimento**: Estes são dados fictícios para testes
- **Não usar em produção**: CPFs são válidos mas fictícios
- **Backup**: Faça backup antes de usar `limpar_agressores_teste()`
- **Performance**: Para muitos agressores (>5000), considere executar em lotes
- **Realismo estatístico**: Distribuição de gênero baseada em dados reais

## 🔗 Integração com o dashboard

Após executar o script, os dados estarão disponíveis em:
- **Dashboard**: http://localhost:8000/relatorios/
- **Admin Django**: http://localhost:8000/admin/sistema_justica/agressor_dados/
- **Relatórios de parentesco**: Dados para análises de relação agressor-vítima

## 🛠️ Customização

Para personalizar os dados gerados, edite as listas no arquivo:
- `NOMES_MASCULINOS`: Adicionar/remover nomes masculinos
- `NOMES_FEMININOS`: Nomes para agressoras mulheres
- `PROFISSOES_MASCULINAS`: Ajustar profissões masculinas
- `BAIRROS` e `RUAS`: Personalizar endereços fictícios

## 📊 Estatísticas detalhadas

O script `estatisticas_agressores()` fornece:
- Distribuição por estado
- Análise por faixa etária
- Top 10 profissões mais comuns
- Distribuição por classe econômica
- Análise de gênero detalhada

## 🔄 Uso em conjunto com vítimas

Recomenda-se executar ambos os scripts para ter dados completos:
```bash
# 1. Gerar vítimas
>>> from automacoes.gera_vitimas import criar_vitimas_aleatorias
>>> criar_vitimas_aleatorias(1000)

# 2. Gerar agressores
>>> from automacoes.gera_agressores import criar_agressores_aleatorios
>>> criar_agressores_aleatorios(1000)
```

---
**Desenvolvido para o projeto PIEVDCS**
*Script de automação para ambiente de desenvolvimento*
