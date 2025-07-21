# Script de Criação de Estados no Banco de Dados

Este script (`cria_estados.py`) automatiza o cadastro dos estados brasileiros no banco de dados do sistema PIEVDCS.

## O que o script faz?

- Cria todos os estados oficiais do Brasil, incluindo o Distrito Federal e a opção "Estrangeiro".
- Garante que não haja duplicidade: se o estado já existe, não será criado novamente.
- Pode ser usado para inicializar ou corrigir o banco de dados em ambientes de desenvolvimento ou produção.

## Estados cadastrados

O script inclui as seguintes siglas e nomes:

| Sigla | Nome                |
| ----- | ------------------- |
| AC    | Acre                |
| AL    | Alagoas             |
| AP    | Amapá               |
| AM    | Amazonas            |
| BA    | Bahia               |
| CE    | Ceará               |
| DF    | Distrito Federal    |
| ES    | Espírito Santo      |
| GO    | Goiás               |
| MA    | Maranhão            |
| MT    | Mato Grosso         |
| MS    | Mato Grosso do Sul  |
| MG    | Minas Gerais        |
| PA    | Pará                |
| PB    | Paraíba             |
| PR    | Paraná              |
| PE    | Pernambuco          |
| PI    | Piauí               |
| RJ    | Rio de Janeiro      |
| RN    | Rio Grande do Norte |
| RS    | Rio Grande do Sul   |
| RO    | Rondônia            |
| RR    | Roraima             |
| SC    | Santa Catarina      |
| SP    | São Paulo           |
| SE    | Sergipe             |
| TO    | Tocantins           |
| EX    | Estrangeiro         |

## Como utilizar

### 1. Via Django Shell
Abra o shell do Django:
```bash
python manage.py shell
```

No shell, execute:
```python
from automacoes.cria_estados import criar_estados
criar_estados()
```

### 2. Execução direta
Você pode executar o script diretamente no shell do Django, sem precisar editar o código:
```bash
python manage.py shell -c "from automacoes.cria_estados import criar_estados; criar_estados()"
```

## Observações
- O script pode ser executado quantas vezes quiser, pois utiliza `get_or_create` para evitar duplicidade.
- Ideal para inicialização de banco de dados ou correção de dados em ambientes de desenvolvimento.
- Após criar os estados, recomenda-se utilizar o script de municípios para completar o cadastro territorial.

## Exemplo de resultado

```
>>> criar_estados()
# Estados criados ou já existentes no banco de dados
```

---

**Autor:** [@OgliariNatan](https://github.com/OgliariNatan)
