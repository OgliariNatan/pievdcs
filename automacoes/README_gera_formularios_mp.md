# 📋 Script de Geração de Formulários de Medida Protetiva

Este script gera dados fictícios realistas para a tabela `FormularioMedidaProtetiva` do sistema PIEVDCS, simulando solicitações de medidas protetivas da Defensoria Pública.

## 📊 Funcionalidades

- **Geração de Dados Realistas**: Cria 500 formulários com dados estatisticamente plausíveis
- **Distribuições Baseadas em Dados Reais**: Segue padrões de violência doméstica no Brasil
- **Validação de Integridade**: Evita duplicatas e verifica dados relacionados
- **Relatórios Detalhados**: Fornece estatísticas completas dos dados gerados

## 🚀 Como Executar

### 1. Via Django Shell (Recomendado)
```bash
# Abrir o shell do Django
python manage.py shell

# Importar e executar a função
from automacoes.gera_formularios_mp import criar_formularios_mp_aleatorios
criar_formularios_mp_aleatorios()

# Para gerar quantidade específica
criar_formularios_mp_aleatorios(250)  # Gera 250 formulários
```

### 2. Execução Direta
```bash
# Executar o script diretamente
python automacoes/gera_formularios_mp.py
```

## 📋 Dados Gerados

### Campos do FormularioMedidaProtetiva:
- **data_solicitacao**: Entre 2 anos atrás e hoje
- **vitima**: Selecionada aleatoriamente dos registros existentes
- **agressor**: Selecionado aleatoriamente dos registros existentes
- **periodo_mp**: Data de validade (120-720 dias após solicitação)
- **solicitada_mpu**: 90% são medidas de urgência
- **tipo_de_violencia**: Distribuição baseada em estatísticas reais
- **comarca_competente**: 70% têm comarca definida
- **grau_parentesco_agressor**: Distribuição realista por parentesco

## 📊 Distribuições Estatísticas

### Tipos de Violência (baseado em dados reais):
- **Física**: 35% dos casos
- **Psicológica**: 30% dos casos
- **Sexual**: 15% dos casos
- **Patrimonial**: 12% dos casos
- **Moral**: 8% dos casos

### Grau de Parentesco (baseado em estatísticas):
- **Cônjuge**: 45% dos casos
- **Irmão**: 12% dos casos
- **Pai**: 10% dos casos
- **Filho**: 8% dos casos
- **Outros parentes**: 25% distribuídos

### Períodos de Validade:
- **120 dias**: 40% (padrão legal)
- **180 dias**: 20%
- **240 dias**: 15%
- **Outros**: 25% distribuídos (até 720 dias)

## 🔍 Funções Auxiliares

### Visualizar Estatísticas
```python
from automacoes.gera_formularios_mp import estatisticas_formularios
estatisticas_formularios()
```

### Limpar Dados de Teste (CUIDADO!)
```python
from automacoes.gera_formularios_mp import limpar_formularios_teste
limpar_formularios_teste()  # Apaga TODOS os formulários
```

## ⚠️ Pré-requisitos

### Dados Necessários:
1. **Vítimas**: Pelo menos 50 registros em `Vitima_dados`
2. **Agressores**: Pelo menos 50 registros em `Agressor_dados`
3. **Comarcas**: Recomenda-se ter registros em `ComarcasPoderJudiciario`

### Scripts Relacionados:
Execute primeiro estes scripts se não tiver dados suficientes:
```bash
# 1. Gerar vítimas
from automacoes.gera_vitimas import criar_vitimas_aleatorias
criar_vitimas_aleatorias()

# 2. Gerar agressores
from automacoes.gera_agressores import criar_agressores_aleatorios
criar_agressores_aleatorios()
```

## 📈 Relatório de Execução

O script fornece um relatório detalhado incluindo:

```
✅ Formulários criados com sucesso: 487
⚠️  Formulários já existentes (ignorados): 13
❌ Erros encontrados: 0
📈 Taxa de sucesso: 100.0%

📋 ESTATÍSTICAS DOS FORMULÁRIOS CRIADOS:

🔍 Distribuição por Tipo de Violência:
   • Física: 168 casos
   • Psicológica: 146 casos
   • Sexual: 73 casos
   • Patrimonial: 58 casos
   • Moral: 42 casos

👥 Distribuição por Grau de Parentesco:
   • Cônjuge: 219 casos
   • Irmão: 58 casos
   • Pai: 49 casos
   • Filho: 39 casos
   • [outros...]

⚡ Medidas de Urgência:
   • Urgentes: 438 (90.0%)
   • Não urgentes: 49 (10.0%)

📅 Período Médio de Validade: 184 dias
```

## 🎯 Casos de Uso

### Para Desenvolvimento:
- Teste de dashboards e relatórios
- Validação de formulários e views
- Simulação de cenários reais
- Desenvolvimento de funcionalidades de busca

### Para Demonstrações:
- Apresentações para stakeholders
- Treinamento de usuários
- Validação de fluxos de trabalho
- Testes de performance

## 🛡️ Segurança e Boas Práticas

### Validações Implementadas:
- ✅ Prevenção de duplicatas (vítima + agressor únicos)
- ✅ Verificação de dados relacionados existentes
- ✅ Tratamento de erros robusto
- ✅ Relatórios de integridade dos dados

### Dados Seguros:
- ✅ Nenhum dado real é usado
- ✅ CPFs ficticios com validação
- ✅ Nomes comuns brasileiros
- ✅ Datas realistas mas fictícias

## 🔧 Personalização

### Ajustar Quantidades:
```python
# Diferentes quantidades
criar_formularios_mp_aleatorios(100)   # 100 formulários
criar_formularios_mp_aleatorios(1000)  # 1000 formulários
```

### Modificar Distribuições:
Edite as variáveis no script para ajustar as distribuições estatísticas:

```python
# Exemplo: mais casos de violência psicológica
pesos_violencia = {
    'Fisica': 25,
    'Psicologica': 45,  # Aumentado
    'Sexual': 15,
    'Patrimonial': 10,
    'Moral': 5
}
```

## 📱 Integração com Sistema

### Admin Interface:
Acesse os dados gerados em:
- **URL**: `/admin/sistema_justica/formulariomedidaprotetiva/`
- **Filtros**: Por tipo de violência, urgência, comarca
- **Buscas**: Por nome da vítima, agressor, comarca

### Dashboard:
Os dados aparecerão automaticamente em:
- Gráficos de violência por tipo
- Mapas de distribuição geográfica
- Relatórios estatísticos
- Painéis de controle

## 🐛 Solução de Problemas

### Erro: "Não há vítimas ou agressores suficientes"
**Solução**: Execute primeiro os scripts de geração de vítimas e agressores.

### Erro: "django.db.utils.IntegrityError"
**Solução**: Provavelmente dados duplicados. O script ignora duplicatas automaticamente.

### Performance lenta:
**Solução**: Gere em lotes menores (100-200 registros por vez).

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs de erro no relatório
2. Confirme que os pré-requisitos estão atendidos
3. Teste com quantidades menores primeiro
4. Verifique se há conflitos de dados únicos

---
**Desenvolvido para PIEVDCS** - Plataforma Integrada de Enfrentamento à Violência Doméstica e Crimes Sexuais
