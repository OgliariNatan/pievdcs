# -*- coding: utf-8 -*-
"""
Script para adicionar 1000 vítimas com dados aleatórios ao banco de dados do PIEVDCS.

Para uso em ambiente de desenvolvimento para popular o banco com dados fictícios para testes.

@comando:
    python manage.py shell
    >>> from automacoes.gera_vitimas import criar_vitimas_aleatorias
    >>> criar_vitimas_aleatorias()

@autor: ogliarinatan
@data: 19/07/2025
"""

import random
from datetime import date, timedelta
from sistema_justica.models.base import Vitima_dados, Estado, Municipio, classeEconomica_choices


def gerar_cpf_ficticio():
    """Gera um CPF fictício válido para testes."""
    # Gera os primeiros 9 dígitos
    cpf_digits = [random.randint(0, 9) for _ in range(9)]
    
    # Calcula o primeiro dígito verificador
    sum1 = sum(cpf_digits[i] * (10 - i) for i in range(9))
    digit1 = (sum1 * 10 % 11) % 10
    cpf_digits.append(digit1)
    
    # Calcula o segundo dígito verificador
    sum2 = sum(cpf_digits[i] * (11 - i) for i in range(10))
    digit2 = (sum2 * 10 % 11) % 10
    cpf_digits.append(digit2)
    
    # Formata como 000.000.000-00
    cpf_str = ''.join(map(str, cpf_digits))
    return f"{cpf_str[:3]}.{cpf_str[3:6]}.{cpf_str[6:9]}-{cpf_str[9:]}"


def gerar_data_nascimento():
    """Gera uma data de nascimento aleatória entre 10 e 80 anos."""
    hoje = date.today()
    idade_min = 10
    idade_max = 80
    
    # Calcula as datas limites
    data_max = date(hoje.year - idade_min, hoje.month, hoje.day)
    data_min = date(hoje.year - idade_max, hoje.month, hoje.day)
    
    # Gera data aleatória no intervalo
    delta = data_max - data_min
    dias_aleatorios = random.randint(0, delta.days)
    return data_min + timedelta(days=dias_aleatorios)


def gerar_telefone():
    """Gera um telefone fictício no formato brasileiro."""
    ddd = random.choice([11, 21, 31, 41, 47, 48, 49, 51, 61, 62, 71, 81, 85])
    numero = f"9{random.randint(1000, 9999)}{random.randint(1000, 9999)}"
    return f"({ddd:02d}) {numero[:5]}-{numero[5:]}"


# Lista de nomes femininos brasileiros comuns
NOMES_FEMININOS = [
    "Ana", "Maria", "Antônia", "Francisca", "Adriana", "Juliana", "Márcia", "Fernanda",
    "Patricia", "Aline", "Sandra", "Camila", "Amanda", "Bruna", "Jessica", "Leticia",
    "Luciana", "Vanessa", "Mariana", "Gabriela", "Rafaela", "Larissa", "Tatiana", "Simone",
    "Priscila", "Caroline", "Cristiane", "Elisângela", "Rosana", "Luciene", "Karina", "Viviane",
    "Claudia", "Renata", "Monica", "Angela", "Sonia", "Regina", "Daniela", "Carla",
    "Rosangela", "Edna", "Eliana", "Joana", "Vera", "Lúcia", "Rita", "Rosa",
    "Helena", "Alice", "Beatriz", "Clara", "Eduarda", "Isadora", "Vitória", "Sofia",
    "Manuela", "Giovanna", "Laura", "Melissa", "Nicole", "Isabella", "Stephanie", "Yasmin",
    "Raquel", "Sabrina", "Natália", "Roberta", "Michele", "Andréa", "Jaqueline", "Patrícia",
    "Débora", "Cristina", "Kelly", "Monique", "Bianca", "Adriane", "Fabiana", "Denise",
    "Rejane", "Solange", "Terezinha", "Aparecida", "Conceição", "Fátima", "Iracema", "Marlene",
    "Silvana", "Sueli", "Tânia", "Valdirene", "Zelia", "Carmem", "Doris", "Eunice"
]

# Lista de sobrenomes brasileiros comuns
SOBRENOMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira",
    "Lima", "Gomes", "Costa", "Ribeiro", "Martins", "Carvalho", "Almeida", "Lopes",
    "Soares", "Fernandes", "Vieira", "Barbosa", "Rocha", "Dias", "Monteiro", "Mendes",
    "Ramos", "Moreira", "Azevedo", "Nascimento", "Correia", "Castro", "Pinto", "Araujo",
    "Cardoso", "Cunha", "Teixeira", "Miranda", "Fonseca", "Reis", "Campos", "Gonçalves",
    "Freitas", "Cruz", "Cavalcanti", "Nunes", "Moura", "Tavares", "Machado", "Nogueira",
    "Paiva", "Borges", "Leite", "Duarte", "Morais", "Andrade", "Barros", "Sales",
    "Melo", "Magalhães", "Bezerra", "Coelho", "Macedo", "Fogaça", "Porto", "Siqueira"
]

# Lista de nomes de pais comuns
NOMES_PAIS = [
    "José", "João", "Antonio", "Francisco", "Carlos", "Paulo", "Pedro", "Lucas", "Luiz",
    "Marcos", "Luis", "Gabriel", "Rafael", "Daniel", "Marcelo", "Bruno", "Eduardo", "Felipe",
    "Raimundo", "Rodrigo", "Manoel", "Nelson", "Roberto", "Edson", "Anderson", "Ricardo",
    "Fernando", "Fabio", "Sergio", "Claudio", "Alexandre", "Miguel", "Renato", "Diego"
]

# Lista de profissões comuns
PROFISSOES = [
    "Doméstica", "Auxiliar de Limpeza", "Vendedora", "Cozinheira", "Recepcionista", 
    "Auxiliar Administrativo", "Professora", "Enfermeira", "Costureira", "Cabeleireira",
    "Manicure", "Garçonete", "Operadora de Caixa", "Secretária", "Estudante",
    "Auxiliar de Produção", "Técnica em Enfermagem", "Coordenadora", "Gerente",
    "Farmacêutica", "Psicóloga", "Advogada", "Contadora", "Arquiteta", "Engenheira",
    "Do Lar", "Aposentada", "Desempregada", "Autônoma", "Empresária"
]

# Lista de bairros fictícios comuns
BAIRROS = [
    "Centro", "Vila Nova", "Jardim das Flores", "Santa Helena", "São Pedro", "Vila São João",
    "Jardim América", "Centro Norte", "Bela Vista", "Parque Industrial", "Vila Operária",
    "Jardim Europa", "Santa Maria", "São Francisco", "Vila Santos", "Jardim Brasil",
    "Centro Sul", "Vila Rica", "Parque das Águas", "Santa Rita", "São José",
    "Vila Esperança", "Jardim Primavera", "Centro Oeste", "Bom Jesus", "Santa Luzia"
]

# Lista de ruas fictícias comuns  
RUAS = [
    "Rua das Flores", "Rua São João", "Rua Santa Maria", "Rua XV de Novembro",
    "Rua Tiradentes", "Rua Dom Pedro II", "Rua Getúlio Vargas", "Rua Presidente Vargas",
    "Rua José de Alencar", "Rua Santos Dumont", "Rua Castro Alves", "Rua Rui Barbosa",
    "Rua Marechal Deodoro", "Rua Benjamin Constant", "Rua Sete de Setembro",
    "Rua Coronel Oliveira", "Rua Major Silva", "Rua Capitão Santos", "Rua Doutor Lima",
    "Rua Professor Almeida", "Avenida Brasil", "Avenida Independência", "Avenida Liberdade",
    "Travessa das Palmeiras", "Travessa São José", "Alameda dos Ipês"
]


def criar_vitimas_aleatorias(quantidade=1000):
    """
    Cria vítimas com dados aleatórios para o sistema PIEVDCS.
    
    Args:
        quantidade (int): Número de vítimas a serem criadas (padrão: 1000)
    """
    print(f"🚀 Iniciando criação de {quantidade} vítimas aleatórias...")
    
    # Verificar se existem estados e municípios
    estados = list(Estado.objects.all())
    if not estados:
        print("❌ ERRO: Não foram encontrados estados no banco. Execute primeiro:")
        print(">>> from automacoes.cria_estados import criar_estados")
        print(">>> criar_estados()")
        return
    
    municipios = list(Municipio.objects.all())
    if not municipios:
        print("❌ ERRO: Não foram encontrados municípios no banco. Execute primeiro:")
        print(">>> from automacoes.cria_municipios import cadastrar_municipios_por_estado")
        print(">>> cadastrar_municipios_por_estado()")
        return
    
    print(f"📊 Estados disponíveis: {len(estados)}")
    print(f"📊 Municípios disponíveis: {len(municipios)}")
    
    vitimas_criadas = 0
    erros = 0
    cpfs_gerados = set()  # Para evitar CPFs duplicados
    
    # Choices disponíveis
    sexo_opcoes = ["F",]
    etnia_opcoes = ["BR", "PR", "PA", "AM", "IN"]
    escolaridade_opcoes = ["AN", "FI", "FC", "EI", "EC", "SU", "SS", "PO"]
    classe_economica_opcoes = ["SR", "AB", "BA", "BC", "BD", "AC"]
    estado_civil_opcoes = ["S", "C", "D", "V", "A", "U", "O"]
    nacionalidade_opcoes = ["BR",]
    
    for i in range(quantidade):
        try:
            # Gerar CPF único
            cpf = gerar_cpf_ficticio()
            while cpf in cpfs_gerados or Vitima_dados.objects.filter(cpf=cpf).exists():
                cpf = gerar_cpf_ficticio()
            cpfs_gerados.add(cpf)
            
            # Gerar nome completo
            nome_principal = random.choice(NOMES_FEMININOS)
            sobrenome1 = random.choice(SOBRENOMES)
            sobrenome2 = random.choice(SOBRENOMES)
            nome_completo = f"{nome_principal} {sobrenome1} {sobrenome2}"
            
            # Gerar nomes dos pais
            nome_pai = f"{random.choice(NOMES_PAIS)} {random.choice(SOBRENOMES)} {random.choice(SOBRENOMES)}"
            nome_mae_primeiro = random.choice(NOMES_FEMININOS)
            nome_mae = f"{nome_mae_primeiro} {random.choice(SOBRENOMES)} {random.choice(SOBRENOMES)}"
            
            # Selecionar município aleatório
            municipio = random.choice(municipios)
            
            # Gerar email (opcional)
            email = None
            if random.choice([True, False]):  # 50% chance de ter email
                nome_email = nome_principal.lower().replace(" ", "")
                dominio = random.choice(["gmail.com", "hotmail.com", "yahoo.com", "outlook.com"])
                numero = random.randint(1, 999)
                email = f"{nome_email}{numero}@{dominio}"
            
            # Criar a vítima
            vitima = Vitima_dados.objects.create(
                nome=nome_completo,
                cpf=cpf,
                nome_social=None,  # Maioria não tem nome social
                nome_do_pai=nome_pai,
                nome_da_mae=nome_mae,
                data_nascimento=gerar_data_nascimento(),
                sexo=random.choice(sexo_opcoes),
                etnia=random.choice(etnia_opcoes),
                estado_civil=random.choice(estado_civil_opcoes),
                telefone=gerar_telefone(),
                nacionalidade=random.choice(nacionalidade_opcoes),
                estado=municipio.estado,
                municipio=municipio,
                bairro=random.choice(BAIRROS),
                endereco_rua=random.choice(RUAS),
                endereco_numero=random.randint(1, 9999),
                email=email,
                escolaridade=random.choice(escolaridade_opcoes),
                classeEconomica=random.choice(classe_economica_opcoes),
                profissao=random.choice(PROFISSOES)
            )
            
            vitimas_criadas += 1
            
            # Mostrar progresso a cada 100 registros
            if (i + 1) % 100 == 0:
                print(f"📝 Progresso: {vitimas_criadas}/{quantidade} vítimas criadas...")
                
        except Exception as e:
            erros += 1
            print(f"❌ Erro ao criar vítima {i+1}: {str(e)}")
            continue
    
    # Relatório final
    print("\n" + "="*60)
    print("📊 RELATÓRIO FINAL - GERAÇÃO DE VÍTIMAS")
    print("="*60)
    print(f"✅ Vítimas criadas com sucesso: {vitimas_criadas}")
    print(f"❌ Erros encontrados: {erros}")
    print(f"📈 Taxa de sucesso: {(vitimas_criadas/quantidade)*100:.1f}%")
    print(f"📋 Total de vítimas no sistema: {Vitima_dados.objects.count()}")
    
    if vitimas_criadas > 0:
        print("\n🎯 ESTATÍSTICAS DOS DADOS GERADOS:")
        
        # Estatísticas por estado
        vitimas_por_estado = {}
        for vitima in Vitima_dados.objects.all():
            estado = vitima.estado.sigla
            vitimas_por_estado[estado] = vitimas_por_estado.get(estado, 0) + 1
        
        print(f"📍 Estados com mais vítimas:")
        for estado, count in sorted(vitimas_por_estado.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {estado}: {count} vítimas")
        
        # Estatísticas por classe econômica
        classes = Vitima_dados.objects.values_list('classeEconomica', flat=True)
        classe_nomes = dict(classeEconomica_choices)
        print(f"\n💰 Distribuição por classe econômica:")
        for classe in set(classes):
            count = list(classes).count(classe)
            print(f"   {classe_nomes.get(classe, classe)}: {count} vítimas")
        
    print("\n✨ Script executado com sucesso!")
    print("💡 Para visualizar os dados, acesse:")
    print("   - Dashboard: /relatorios/")
    print("   - Admin: /admin/sistema_justica/vitima_dados/")


def limpar_vitimas_teste():
    """
    Remove todas as vítimas do banco de dados.
    CUIDADO: Esta função apaga TODOS os registros de vítimas!
    """
    resposta = input("⚠️  ATENÇÃO: Deseja realmente APAGAR TODAS as vítimas? (digite 'CONFIRMO' para continuar): ")
    
    if resposta == "CONFIRMO":
        count = Vitima_dados.objects.count()
        Vitima_dados.objects.all().delete()
        print(f"🗑️  {count} vítimas foram removidas do banco de dados.")
    else:
        print("❌ Operação cancelada.")


if __name__ == "__main__":
    print("🚀 Script de Geração de Vítimas - PIEVDCS")
    print("Para executar, use o Django shell:")
    print("python manage.py shell")
    print(">>> from automacoes.gera_vitimas import criar_vitimas_aleatorias")
    print(">>> criar_vitimas_aleatorias(1000)")
