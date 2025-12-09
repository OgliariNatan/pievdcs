# Gerador de Vítimas - PIEVDCS

Este script cria dados fictícios de vítimas para popular o banco de dados do sistema PIEVDCS durante o desenvolvimento e testes.

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

### Criar 1000 vítimas (padrão)
```bash
python manage.py shell
>>> from automacoes.gera_vitimas import criar_vitimas_aleatorias
>>> criar_vitimas_aleatorias()
```

### Criar quantidade específica
```bash
>>> criar_vitimas_aleatorias(500)  # Cria 500 vítimas
```

### Ver estatísticas
```bash
>>> from automacoes.gera_vitimas import estatisticas_vitimas
>>> estatisticas_vitimas()
```

### Limpar todas as vítimas (CUIDADO!)
```bash
>>> from automacoes.gera_vitimas import limpar_vitimas_teste
>>> limpar_vitimas_teste()
```

## 📊 Dados gerados

O script cria vítimas com dados realísticos incluindo:

### 👤 Informações pessoais
- **Nome completo**: Combinações de nomes femininos brasileiros comuns
- **CPF**: Gerado automaticamente com dígitos verificadores válidos
- **Data de nascimento**: Idades entre 18 e 80 anos
- **Sexo**: F (Feminino), M (Masculino), O (Outro)
- **Etnia**: Branca, Preta, Parda, Amarela, Indígena
- **Estado civil**: Solteira, Casada, Divorciada, Viúva, etc.

### 📞 Contato
- **Telefone**: Formato brasileiro com DDD real: (XX) XXXXX-XXXX
- **Email**: 50% das vítimas têm email gerado automaticamente

### 🏠 Endereço
- **Estado/Município**: Selecionados aleatoriamente dos cadastrados
- **Bairro**: Lista de bairros fictícios comuns
- **Rua**: Nomes de ruas típicos brasileiros
- **Número**: Números de 1 a 9999

### 💼 Informações socioeconômicas
- **Escolaridade**: Desde "Não Alfabetizado" até "Pós-Graduação"
- **Classe econômica**: 6 faixas de renda conforme padrão brasileiro
- **Profissão**: Lista de profissões comuns femininas

## 🎯 Características do algoritmo

- **CPFs únicos**: Algoritmo gera CPFs válidos e únicos
- **Dados realísticos**: Nomes, telefones e endereços brasileiros
- **Distribuição geográfica**: Vítimas espalhadas pelos municípios cadastrados
- **Diversidade**: Variação em idade, etnia, classe social, etc.
- **Performance**: Relatórios de progresso a cada 100 registros

## 📈 Exemplo de saída

```
🚀 Iniciando criação de 1000 vítimas aleatórias...
📊 Estados disponíveis: 27
📊 Municípios disponíveis: 5570
📝 Progresso: 100/1000 vítimas criadas...
📝 Progresso: 200/1000 vítimas criadas...
...
📝 Progresso: 1000/1000 vítimas criadas...

============================================================
📊 RELATÓRIO FINAL - GERAÇÃO DE VÍTIMAS
============================================================
✅ Vítimas criadas com sucesso: 1000
❌ Erros encontrados: 0
📈 Taxa de sucesso: 100.0%
📋 Total de vítimas no sistema: 1000

🎯 ESTATÍSTICAS DOS DADOS GERADOS:
📍 Estados com mais vítimas:
   SP: 187 vítimas
   MG: 134 vítimas
   RJ: 89 vítimas
   RS: 76 vítimas
   PR: 63 vítimas

💰 Distribuição por classe econômica:
   De R$1.518,01 a R$3.636,00: 201 vítimas
   Sem Renda: 183 vítimas
   De R$3.636,01 a R$7.017,63: 167 vítimas
   ...
```

## ⚠️ Importante

- **Apenas para desenvolvimento**: Estes são dados fictícios para testes
- **Não usar em produção**: CPFs são válidos mas fictícios
- **Backup**: Faça backup antes de usar `limpar_vitimas_teste()`
- **Performance**: Para muitas vítimas (>5000), considere executar em lotes

## 🔗 Integração com o dashboard

Após executar o script, os dados estarão disponíveis em:
- **Dashboard**: http://localhost:8000/relatorios/
- **Admin Django**: http://localhost:8000/admin/sistema_justica/vitima_dados/
- **Gráficos e mapas**: Automaticamente populados com os novos dados

## 🛠️ Customização

Para personalizar os dados gerados, edite as listas no arquivo:
- `NOMES_FEMININOS`: Adicionar/remover nomes
- `SOBRENOMES`: Modificar sobrenomes disponíveis  
- `PROFISSOES`: Ajustar profissões conforme necessário
- `BAIRROS` e `RUAS`: Personalizar endereços fictícios

---
**Desenvolvido para o projeto PIEVDCS**
*Script de automação para ambiente de desenvolvimento*
