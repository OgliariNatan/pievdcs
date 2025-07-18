# -*- coding: utf-8 -*-
"""Script para atribuir municipios aos estados no banco de dados do sistema de justiça

    Para uso em ambiente de desenvolvimento ou para inicializar o banco de dados com os estados brasileiros.

    @comando:
      python manage.py shell
      >>> cadastrar_municipios_por_estado()
"""

from sistema_justica.models import Estado, Municipio

# Dicionário com siglas dos estados e seus respectivos municípios
municipios_por_estado = {
    "AC": {  # Acre
        "Rio Branco",
        "Cruzeiro do Sul",
        "Sena Madureira",
        "Tarauacá",
        "Feijó",
        "Brasiléia",
        "Plácido de Castro",
        "Xapuri",
        "Epitaciolândia",
        "Mâncio Lima",
        "Senador Guiomard",
        "Rodrigues Alves",
        "Capixaba",
        "Acrelândia",
        "Bujari",
        "Porto Walter",
        "Marechal Thaumaturgo",
        "Jordão",
        "Santa Rosa do Purus",
        "Manoel Urbano",
        "Assis Brasil",
        "Porto Acre"
    },
    "AL": {  # Alagoas
        "Maceió",
        "Arapiraca",
        "Palmeira dos Índios",
        "Rio Largo",
        "Penedo",
        "União dos Palmares",
        "São Miguel dos Campos",
        "Coruripe",
        "Delmiro Gouveia",
        "Marechal Deodoro",
        "Santana do Ipanema",
        "Campo Alegre",
        "Viçosa",
        "Murici",
        "Pilar",
        "Girau do Ponciano",
        "Água Branca",
        "São Sebastião",
        "Joaquim Gomes",
        "Atalaia"
    },
    "AP": {  # Amapá
        "Macapá",
        "Santana",
        "Laranjal do Jari",
        "Oiapoque",
        "Mazagão",
        "Porto Grande",
        "Tartarugalzinho",
        "Vitória do Jari",
        "Amapá",
        "Ferreira Gomes",
        "Pracuúba",
        "Calçoene",
        "Cutias",
        "Itaubal",
        "Pedra Branca do Amapari",
        "Serra do Navio"
    },
    "AM": {  # Amazonas
        "Manaus",
        "Parintins",
        "Itacoatiara",
        "Manacapuru",
        "Coari",
        "Tefé",
        "Tabatinga",
        "Maués",
        "São Gabriel da Cachoeira",
        "Humaitá",
        "Lábrea",
        "Iranduba",
        "Presidente Figueiredo",
        "Carauari",
        "Eirunepé",
        "Manicoré",
        "Careiro",
        "Benjamin Constant",
        "Fonte Boa",
        "Novo Airão"
    },
    # Adicione mais estados conforme necessário...
}



def cadastrar_municipios_por_estado():
    """
    Cadastra municípios para cada estado baseando-se na sigla do estado.
    Só cadastra municípios que ainda não existem no banco de dados.
    """
    municipios_cadastrados = 0
    municipios_existentes = 0
    
    print("Iniciando cadastro de municípios por estado...")
    
    for sigla_estado, lista_municipios in municipios_por_estado.items():
        try:
            # Busca o estado pela sigla
            estado = Estado.objects.get(sigla=sigla_estado)
            print(f"\nProcessando estado: {estado.nome} ({sigla_estado})")
            
            for nome_municipio in lista_municipios:
                # Verifica se o município já existe no estado
                municipio_existente = Municipio.objects.filter(
                    nome=nome_municipio,
                    estado=estado
                ).exists()
                
                if not municipio_existente:
                    # Cadastra o município se não existir
                    Municipio.objects.create(
                        nome=nome_municipio,
                        estado=estado
                    )
                    print(f"  ✓ Cadastrado: {nome_municipio}")
                    municipios_cadastrados += 1
                else:
                    print(f"  - Já existe: {nome_municipio}")
                    municipios_existentes += 1
                    
        except Estado.DoesNotExist:
            print(f"⚠️  Estado com sigla '{sigla_estado}' não encontrado no banco de dados!")
            continue
        except Exception as e:
            print(f"❌ Erro ao processar estado {sigla_estado}: {str(e)}")
            continue
    
    print(f"\n📊 Resumo:")
    print(f"   Municípios cadastrados: {municipios_cadastrados}")
    print(f"   Municípios já existentes: {municipios_existentes}")
    print(f"   Total processado: {municipios_cadastrados + municipios_existentes}")
    print("✅ Processo finalizado!")


def verificar_estados_cadastrados():
    """
    Verifica quais estados estão cadastrados no banco de dados
    """
    print("Estados cadastrados no banco de dados:")
    estados = Estado.objects.all().order_by('sigla')
    
    if not estados:
        print("❌ Nenhum estado encontrado no banco de dados!")
        return
    
    for estado in estados:
        count_municipios = Municipio.objects.filter(estado=estado).count()
        print(f"  {estado.sigla} - {estado.nome} ({count_municipios} municípios)")
    
    print(f"\nTotal de estados cadastrados: {estados.count()}")


def atribuir_municipios():
    """
    Função original (mantida para compatibilidade)
    """
    estados = Estado.objects.all()
    for estado in estados:
        municipios = Municipio.objects.filter(estado=estado)
        estado.municipios.set(municipios)


# Exemplo de uso:
if __name__ == "__main__":
    print("Script para cadastro de municípios por estado")
    print("=" * 50)
    print("\nFunções disponíveis:")
    print("1. verificar_estados_cadastrados() - Verifica estados no banco")
    print("2. cadastrar_municipios_por_estado() - Cadastra municípios")
    print("3. atribuir_municipios() - Função original")
    print("\nPara usar no Django shell:")
    print(">>> from automacoes.atribui_municipio import *")
    print(">>> verificar_estados_cadastrados()")
    print(">>> cadastrar_municipios_por_estado()")