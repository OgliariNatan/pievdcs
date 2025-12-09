# -*- coding: utf-8 -*-
"""
Script para adicionar 1000 agressores com dados aleatórios ao banco de dados do PIEVDCS.

Para uso em ambiente de desenvolvimento para popular o banco com dados fictícios para testes.

@comando:
    python manage.py shell
    >>> from automacoes.gera_agressores import criar_agressores_aleatorios
    >>> criar_agressores_aleatorios()

@autor: OgliariNatan
@data: 19/07/2025
"""

import random
from datetime import date, timedelta
from sistema_justica.models.base import Agressor_dados, Estado, Municipio


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
    """Gera uma data de nascimento aleatória entre 18 e 85 anos."""
    hoje = date.today()
    idade_min = 18
    idade_max = 85
    
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


# Lista de nomes masculinos brasileiros comuns
NOMES_MASCULINOS = [
    "José", "João", "Antonio", "Francisco", "Carlos", "Paulo", "Pedro", "Lucas", "Luiz",
    "Marcos", "Luis", "Gabriel", "Rafael", "Daniel", "Marcelo", "Bruno", "Eduardo", "Felipe",
    "Raimundo", "Rodrigo", "Manoel", "Nelson", "Roberto", "Edson", "Anderson", "Ricardo",
    "Fernando", "Fabio", "Sergio", "Claudio", "Alexandre", "Miguel", "Renato", "Diego",
    "Adriano", "Gustavo", "Leonardo", "Thiago", "Mateus", "Vinicius", "Leandro", "Andre",
    "Wagner", "Julio", "Cesar", "Cristiano", "Alan", "Renan", "Henrique", "Everton",
    "Ivan", "Robson", "Jeferson", "Luciano", "Mauricio", "Willian", "Gilson", "Ronaldo",
    "Junior", "Josue", "Valmir", "Valdeci", "Wanderson", "Wesley", "Wilson", "Yuri",
    "Alexsandro", "Benedito", "Cláudio", "Domingos", "Edilson", "Francisco", "Geraldo", "Helio",
    "Ivo", "Jaime", "Kleber", "Laercio", "Mario", "Nivaldo", "Osmar", "Patrick"
]

# Lista de sobrenomes brasileiros comuns (reutilizando)
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

# Lista de nomes femininos para mães
NOMES_FEMININOS = [
    "Maria", "Ana", "Francisca", "Antônia", "Adriana", "Juliana", "Márcia", "Fernanda",
    "Patricia", "Sandra", "Camila", "Jessica", "Vanessa", "Mariana", "Gabriela", "Larissa",
    "Simone", "Cristiane", "Monica", "Angela", "Sonia", "Regina", "Daniela", "Carla",
    "Rosangela", "Eliana", "Joana", "Vera", "Lúcia", "Rita", "Rosa", "Helena"
]

# Lista de profissões masculinas comuns
PROFISSOES_MASCULINAS = [
    "Pedreiro", "Motorista", "Mecânico", "Soldador", "Pintor", "Eletricista", "Marceneiro",
    "Segurança", "Porteiro", "Vigilante", "Operador de Máquina", "Auxiliar de Produção",
    "Vendedor", "Técnico", "Engenheiro", "Advogado", "Contador", "Administrador",
    "Professor", "Médico", "Enfermeiro", "Farmacêutico", "Policial", "Bombeiro",
    "Caminhoneiro", "Taxista", "Uber", "Garçom", "Cozinheiro", "Barbeiro",
    "Comerciante", "Empresário", "Autônomo", "Aposentado", "Desempregado", "Agricultor",
    "Pecuarista", "Pescador", "Carpinteiro", "Encanador", "Jardineiro", "Frentista",
    "Cobrador", "Operário", "Técnico em Informática", "Programador"
]

# Lista de bairros fictícios comuns (reutilizando)
BAIRROS = [
    "Centro", "Vila Nova", "Jardim das Flores", "Santa Helena", "São Pedro", "Vila São João",
    "Jardim América", "Centro Norte", "Bela Vista", "Parque Industrial", "Vila Operária",
    "Jardim Europa", "Santa Maria", "São Francisco", "Vila Santos", "Jardim Brasil",
    "Centro Sul", "Vila Rica", "Parque das Águas", "Santa Rita", "São José",
    "Vila Esperança", "Jardim Primavera", "Centro Oeste", "Bom Jesus", "Santa Luzia"
]

# Lista de ruas fictícias comuns (reutilizando)
RUAS = [
    "Rua das Flores", "Rua São João", "Rua Santa Maria", "Rua XV de Novembro",
    "Rua Tiradentes", "Rua Dom Pedro II", "Rua Getúlio Vargas", "Rua Presidente Vargas",
    "Rua José de Alencar", "Rua Santos Dumont", "Rua Castro Alves", "Rua Rui Barbosa",
    "Rua Marechal Deodoro", "Rua Benjamin Constant", "Rua Sete de Setembro",
    "Rua Coronel Oliveira", "Rua Major Silva", "Rua Capitão Santos", "Rua Doutor Lima",
    "Rua Professor Almeida", "Avenida Brasil", "Avenida Independência", "Avenida Liberdade",
    "Travessa das Palmeiras", "Travessa São José", "Alameda dos Ipês"
]


def criar_agressores_aleatorios(quantidade=1000):
    """
    Cria agressores com dados aleatórios realísticos para o sistema PIEVDCS.
    
    Args:
        quantidade (int): Número de agressores a serem criados (padrão: 1000)
    """
    print(f"🚀 Iniciando criação de {quantidade} agressores aleatórios...")
    
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
    
    agressores_criados = 0
    erros = 0
    cpfs_gerados = set()  # Para evitar CPFs duplicados
    
    # Choices disponíveis para agressores
    sexo_opcoes = ["M",]  # Maioria masculino, mas pode ter outros
    etnia_opcoes = ["BR", "PR", "PA", "AM", "IN"]
    escolaridade_opcoes = ["AN", "FI", "FC", "EI", "EC", "SU", "SS", "PO"]
    classe_economica_opcoes = ["SR", "AB", "BA", "BC", "BD", "AC"]
    estado_civil_opcoes = ["S", "C", "D", "V", "A", "U", "O"]
    nacionalidade_opcoes = ["BR",]
    
    for i in range(quantidade):
        try:
            # Gerar CPF único
            cpf = gerar_cpf_ficticio()
            while cpf in cpfs_gerados or Agressor_dados.objects.filter(cpf=cpf).exists():
                cpf = gerar_cpf_ficticio()
            cpfs_gerados.add(cpf)
            
            # Determinar sexo (80% masculino, 15% feminino, 5% outro)
            sexo = random.choices(["M",], weights=[100,])[0]
            
            # Gerar nome completo baseado no sexo
            if sexo == "M":
                nome_principal = random.choice(NOMES_MASCULINOS)
            elif sexo == "F":
                nome_principal = random.choice(NOMES_FEMININOS)
            else:
                nome_principal = random.choice(NOMES_MASCULINOS + NOMES_FEMININOS)
            
            sobrenome1 = random.choice(SOBRENOMES)
            sobrenome2 = random.choice(SOBRENOMES)
            nome_completo = f"{nome_principal} {sobrenome1} {sobrenome2}"
            
            # Gerar nomes dos pais
            nome_pai = f"{random.choice(NOMES_MASCULINOS)} {random.choice(SOBRENOMES)} {random.choice(SOBRENOMES)}"
            nome_mae = f"{random.choice(NOMES_FEMININOS)} {random.choice(SOBRENOMES)} {random.choice(SOBRENOMES)}"
            
            # Selecionar município aleatório
            municipio = random.choice(municipios)
            
            # Gerar email (opcional) - 30% dos agressores têm email
            email = None
            if random.random() < 0.3:  # 30% chance de ter email
                nome_email = nome_principal.lower().replace(" ", "")
                dominio = random.choice(["gmail.com", "hotmail.com", "yahoo.com", "outlook.com"])
                numero = random.randint(1, 999)
                email = f"{nome_email}{numero}@{dominio}"
            
           
            profissao = random.choice(PROFISSOES_MASCULINAS)
           
            
            # Criar o agressor
            agressor = Agressor_dados.objects.create(
                nome=nome_completo,
                cpf=cpf,
                nome_social=None,  # Raramente tem nome social
                nome_do_pai=nome_pai,
                nome_da_mae=nome_mae,
                data_nascimento=gerar_data_nascimento(),
                sexo=sexo,
                etnia=random.choice(etnia_opcoes),
                estado_civil=random.choice(estado_civil_opcoes),
                telefone=gerar_telefone(),
                nacionalidade=random.choice(nacionalidade_opcoes),
                estado=municipio.estado,
                municipio=municipio,
                bairro=random.choice(BAIRROS),
                endereco=random.choice(RUAS),
                endereco_numero=random.randint(1, 99),
                email=email,
                escolaridade=random.choice(escolaridade_opcoes),
                classeEconomica=random.choice(classe_economica_opcoes),
                profissao=profissao
            )
            
            agressores_criados += 1
            
            # Mostrar progresso a cada 100 registros
            if (i + 1) % 100 == 0:
                print(f"📝 Progresso: {agressores_criados}/{quantidade} agressores criados...")
                
        except Exception as e:
            erros += 1
            print(f"❌ Erro ao criar agressor {i+1}: {str(e)}")
            continue
    
    # Relatório final
    print("\n" + "="*60)
    print("📊 RELATÓRIO FINAL - GERAÇÃO DE AGRESSORES")
    print("="*60)
    print(f"✅ Agressores criados com sucesso: {agressores_criados}")
    print(f"❌ Erros encontrados: {erros}")
    print(f"📈 Taxa de sucesso: {(agressores_criados/quantidade)*100:.1f}%")
    print(f"📋 Total de agressores no sistema: {Agressor_dados.objects.count()}")
    
    if agressores_criados > 0:
        print("\n🎯 ESTATÍSTICAS DOS DADOS GERADOS:")
        
        # Estatísticas por sexo
        agressores_por_sexo = {"M": 0, "F": 0, "O": 0}
        for agressor in Agressor_dados.objects.all():
            agressores_por_sexo[agressor.sexo] = agressores_por_sexo.get(agressor.sexo, 0) + 1
        
        print(f"👥 Distribuição por sexo:")
        sexo_nomes = {"M": "Masculino", "F": "Feminino", "O": "Outro"}
        for sexo, count in agressores_por_sexo.items():
            print(f"   {sexo_nomes[sexo]}: {count} agressores")
        
        # Estatísticas por estado
        agressores_por_estado = {}
        for agressor in Agressor_dados.objects.all():
            estado = agressor.estado.sigla
            agressores_por_estado[estado] = agressores_por_estado.get(estado, 0) + 1
        
        print(f"\n📍 Estados com mais agressores:")
        for estado, count in sorted(agressores_por_estado.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {estado}: {count} agressores")
        
        # Estatísticas por classe econômica
        from sistema_justica.models.base import classeEconomica_choices
        classes = Agressor_dados.objects.values_list('classeEconomica', flat=True)
        classe_nomes = dict(classeEconomica_choices)
        print(f"\n💰 Distribuição por classe econômica:")
        for classe in set(classes):
            count = list(classes).count(classe)
            print(f"   {classe_nomes.get(classe, classe)}: {count} agressores")
        
    print("\n✨ Script executado com sucesso!")
    print("💡 Para visualizar os dados, acesse:")
    print("   - Dashboard: /relatorios/")
    print("   - Admin: /admin/sistema_justica/agressor_dados/")


def limpar_agressores_teste():
    """
    Remove todos os agressores do banco de dados.
    CUIDADO: Esta função apaga TODOS os registros de agressores!
    """
    resposta = input("⚠️  ATENÇÃO: Deseja realmente APAGAR TODOS os agressores? (digite 'CONFIRMO' para continuar): ")
    
    if resposta == "CONFIRMO":
        count = Agressor_dados.objects.count()
        Agressor_dados.objects.all().delete()
        print(f"🗑️  {count} agressores foram removidos do banco de dados.")
    else:
        print("❌ Operação cancelada.")


def estatisticas_agressores():
    """Mostra estatísticas detalhadas dos agressores cadastrados."""
    total = Agressor_dados.objects.count()
    
    if total == 0:
        print("📊 Nenhum agressor encontrado no banco de dados.")
        return
    
    print(f"\n📊 ESTATÍSTICAS DOS AGRESSORES CADASTRADOS")
    print("="*50)
    print(f"Total de agressores: {total}")
    
    # Por estado
    print(f"\n📍 Por Estado:")
    agressores_estado = Agressor_dados.objects.values('estado__sigla', 'estado__nome').distinct()
    for item in agressores_estado:
        count = Agressor_dados.objects.filter(estado__sigla=item['estado__sigla']).count()
        print(f"   {item['estado__sigla']} - {item['estado__nome']}: {count}")
    
    # Por sexo
    print(f"\n👥 Por Sexo:")
    from sistema_justica.models.base import sexo_choices
    sexos = dict(sexo_choices)
    for sexo_key, sexo_nome in sexos.items():
        count = Agressor_dados.objects.filter(sexo=sexo_key).count()
        print(f"   {sexo_nome}: {count}")
    
    # Por faixa etária
    print(f"\n🎂 Por Faixa Etária:")
    idades = [a.idade for a in Agressor_dados.objects.all() if a.idade]
    if idades:
        faixas = {
            "18-25 anos": len([i for i in idades if 18 <= i <= 25]),
            "26-35 anos": len([i for i in idades if 26 <= i <= 35]),
            "36-45 anos": len([i for i in idades if 36 <= i <= 45]),
            "46-55 anos": len([i for i in idades if 46 <= i <= 55]),
            "56+ anos": len([i for i in idades if i > 55]),
        }
        for faixa, count in faixas.items():
            print(f"   {faixa}: {count}")
    
    # Por profissão (top 10)
    print(f"\n💼 Profissões mais comuns:")
    profissoes = Agressor_dados.objects.values_list('profissao', flat=True)
    profissoes_count = {}
    for prof in profissoes:
        profissoes_count[prof] = profissoes_count.get(prof, 0) + 1
    
    for prof, count in sorted(profissoes_count.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {prof}: {count}")


if __name__ == "__main__":
    print("🚀 Script de Geração de Agressores - PIEVDCS")
    print("Para executar, use o Django shell:")
    print("python manage.py shell")
    print(">>> from automacoes.gera_agressores import criar_agressores_aleatorios")
    print(">>> criar_agressores_aleatorios(1000)")
