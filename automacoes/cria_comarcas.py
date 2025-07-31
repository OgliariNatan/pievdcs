# -*- coding: utf-8 -*-

"""Script para cadastrar as comarcas do Poder Judiciário de Santa Catarina e vincular seus municípios.
    Cadastrado com base nas informações do site do TJSC (https://www.tjsc.jus.br/paginas-das-comarcas).

    Para uso em ambiente de desenvolvimento ou para inicializar o banco de dados com as comarcas.

    @comando:
      python manage.py shell
      >>> from automacoes.cria_comarcas import cadastrar_comarcas_judiciario_sc
      >>> cadastrar_comarcas_judiciario_sc()
"""

from sistema_justica.models.base import Estado, Municipio
from sistema_justica.models.poder_judiciario import ComarcasPoderJudiciario


# Dicionário com as comarcas de SC e seus respectivos municípios abrangentes
comarcas_sc = {
    "Abelardo Luz": ["Abelardo Luz", "Ouro Verde"],
    "Anchieta": ["Anchieta", "Romelândia", "Palma Sola"],
    "Anita Garibaldi": ["Anita Garibaldi", "Celso Ramos", "Abdon Batista"],
    "Araquari": ["Araquari", "Balneário Barra do Sul"],
    "Araranguá": ["Araranguá", "Balneário Arroio do Silva", "Maracajá"],
    "Armazém": ["Armazém", "Gravatal", "São Martinho"],
    "Ascurra": ["Ascurra", "Rodeio", "Apiúna"],
    "Balneário Camboriú": ["Balneário Camboriú"],
    "Balneário Piçarras": ["Balneário Piçarras"],
    "Barra Velha": ["Barra Velha", "São João do Itaperiú"],
    "Biguaçu": ["Biguaçu", "Antônio Carlos", "Governador Celso Ramos"],
    "Blumenau": ["Blumenau"],
    "Bom Retiro": ["Bom Retiro", "Alfredo Wagner"],
    "Braço do Norte": ["Braço do Norte", "Grão Pará", "Rio Fortuna", "Santa Rosa de Lima", "São Ludgero"],
    "Brusque": ["Brusque", "Botuverá", "Guabiruba"],
    "Caçador": ["Caçador", "Rio das Antas", "Calmon", "Macieira"],
    "Camboriú": ["Camboriú"],
    "Campo Belo do Sul": ["Campo Belo do Sul", "Cerro Negro", "Capão Alto"],
    "Campo Erê": ["Campo Erê", "Saltinho", "São Bernardino"],
    "Campos Novos": ["Campos Novos", "Brunópolis", "Zortéa", "Vargem"],
    "Canoinhas": ["Canoinhas", "Bela Vista do Toldo", "Major Vieira", "Três Barras"],
    "Capinzal": ["Capinzal", "Lacerdópolis", "Ouro", "Piratuba", "Lacerdópolis"],
    "Capivari de Baixo": ["Capivari de Baixo"],
    "Catanduvas": ["Catanduvas", "Jaborá", "Vargem Bonita"],
    "Chapecó": ["Chapecó", "Caxambu do Sul", "Nova Itaberaba", "Cordilheira Alta", "Guatambú", "Paial", "Planalto Alegre"], 
    "Concórdia": ["Concórdia", "Irani", "Alto Bela Vista", "Peritiba", "Presidente Castelo Branco"],
    "Coronel Freitas": ["Coronel Freitas", "União do Oeste", "Águas Frias", "Jardinópolis"],
    "Correia Pinto": ["Correia Pinto", "Ponte Alta"],
    "Criciúma": ["Criciúma", "Siderópolis", "Treviso", "Nova Veneza"],
    "Cunha Porã": ["Cunha Porã"],
    "Curitibanos": ["Curitibanos", "Frei Rogério", "Ponte Alta do Norte", "São Cristóvão do Sul"],
    "Descanso": ["Descanso", "Belmonte", "Santa Helena"],
    "Dionísio Cerqueira": ["Dionísio Cerqueira"],
    "Capital": ["Florianópolis"],
    "Forquilhinha": ["Forquilhinha"],
    "Fraiburgo": ["Fraiburgo", "Monte Carlo"],
    "Garopaba": ["Garopaba", "Paulo Lopes"],
    "Garuva": ["Garuva"],
    "Gaspar": ["Gaspar", "Ilhota"],
    "Guaramirim": ["Guaramirim", "Massaranduba", "Schroeder"],
    "Herval d'Oeste": ["Herval d'Oeste", "Erval Velho"],
    "Ibirama": ["Ibirama", "José Boiteux"],
    "Içara": ["Içara"],
    "Imaruí": ["Imaruí"],
    "Imbituba": ["Imbituba"],
    "Indaial": ["Indaial"],
    "Ipumirim": ["Ipumirim", "Arabutã", "Lindóia do Sul"],
    "Itá": ["Itá"],
    "Itaiópolis": ["Itaiopolis"],
    "Itajaí": ["Itajaí"],
    "Itapema": ["Itapema"],
    "Itapiranga": ["Itapiranga", "São João do Oeste", "Tunápolis"],
    "Itapoá": ["Itapoá"],
    "Ituporanga": ["Ituporanga", "Leoberto Leal", "Atalanta", "Chapadão do Lageado", "Imbuia", "Petrolândia", "Vidal Ramos"],
    "Jaguaruna": ["Jaguaruna", "Treze de Maio", "Sangão"],
    "Jaraguá do Sul": ["Jaraguá do Sul", "Corupá"],
    "Joaçaba": ["Joaçaba", "Água Doce", "Ibicaré", "Luzerna", "Treze Tílias"],
    "Joinville": ["Joinville"],
    "Lages": ["Lages", "Bocaina do Sul", "São José do Cerrito", "Painel"], 
    "Laguna": ["Laguna", "Pescaria Brava"],
    "Lauro Müller": ["Lauro Muller"],
    "Lebon Régis": ["Lebon Régis"],
    "Mafra": ["Mafra"],
    "Maravilha": ["Maravilha", "Flor do Sertão", "Iraceminha", "São Miguel da Boa Vista", "Tigrinhos"],
    "Meleiro": ["Meleiro", "Morro Grande"],
    "Modelo": ["Modelo", "Serra Alta", "Sul Brasil", "Bom Jesus do Oeste"],
    "Mondaí": ["Mondaí", "Iporã do Oeste", "Riqueza"],
    "Navegantes": ["Navegantes", "Luiz Alves"],
    "Orleans": ["Orleans"],
    "Otacílio Costa": ["Otacílio Costa", "Palmeira"],
    "Palhoça": ["Palhoça"],
    "Palmitos": ["Palmitos", "Caibi"],
    "Papanduva": ["Papanduva", "Monte Castelo"],
    "Penha": ["Penha"],
    "Pinhalzinho": ["Pinhalzinho", "Nova Erechim", "Saudades"],
    "Pomerode": ["Pomerode"],
    "Ponte Serrada": ["Ponte Serrada", "Passos Maia", "Vargeão"],
    "Porto Belo": ["Porto Belo", "Bombinhas"],
    "Porto União": ["Porto União", "Matos Costa", "Irineópolis"],
    "Presidente Getúlio": ["Presidente Getúlio", "Dona Emma", "Witmarsum", "Vitor Meireles"],
    "Quilombo": ["Quilombo",  "Formosa do Sul", "Santiago do Sul", "Irati"],
    "Rio do Campo": ["Rio do Campo", "Santa Terezinha"],
    "Rio do Oeste": ["Rio do Oeste", "Laurentino"],
    "Rio do Sul": ["Rio do Sul", "Agronômica", "Aurora", "Lontras", "Presidente Nereu"],
    "Rio Negrinho": ["Rio Negrinho"],
    "Santa Cecília": ["Santa Cecília", "Timbó Grande"],
    "Santa Rosa do Sul": ["Santa Rosa do Sul", "São João do Sul", "Praia Grande", "Passo de Torres"],
    "Santo Amaro da Imperatriz": ["Santo Amaro da Imperatriz", "Angelina", "Rancho Queimado", "Águas Mornas", "Anitápolis", "São Bonifácio"],
    "São Bento do Sul": ["São Bento do Sul", "Campo Alegre"],
    "São Carlos": ["São Carlos", "Águas de Chapecó", "Cunhataí"],
    "São Domingos": ["São Domingos", "Galvão", "Coronel Martins", "Ipuaçu", "Entre Rios"],
    "São Francisco do Sul": ["São Francisco do Sul"],
    "São João Batista": ["São João Batista", "Major Gercino", "Nova Trento"],
    "São Joaquim": ["São Joaquim", "Bom Jardim da Serra", "Urupema"],
    "São José": ["São José", "São Pedro de Alcântara"],
    "São José do Cedro": ["São José do Cedro", "Guarujá do Sul", "Princesa"],
    "São Lourenço do Oeste": ["São Lourenço do Oeste", "Jupiá", "Novo Horizonte"],
    "São Miguel do Oeste": ["São Miguel do Oeste", "Bandeirante", "Barra Bonita", "Paraíso", "Guaraciaba"],
    "Seara": ["Seara", "Arvoredo", "Xavantina"],
    "Sombrio": ["Sombrio", "Balneário Gaivota"],
    "Taió": ["Taió", "Mirim Doce", "Salete"],
    "Tangará": ["Tangará", "Ibiam", "Pinheiro Preto"],
    "Tijucas": ["Tijucas", "Canelinha"],
    "Timbó": ["Timbó", "Benedito Novo", "Rio dos Cedros", "Doutor Pedrinho"],
    "Trombudo Central": ["Trombudo Central", "Agrolândia", "Braço do Trombudo", "Pouso Redondo"],
    "Tubarão": ["Tubarão", "Pedras Grandes"],
    "Turvo": ["Turvo", "Ermo", "Jacinto Machado", "Timbé do Sul"],
    "Urubici": ["Urubici", "Rio Rufino"],
    "Urussanga": ["Urussanga", "Balneário Rincão", "Pedras Grandes", "Treze de Maio"],
    "Videira": ["Videira", "Arroio Trinta", "Iomerê", "Salto Veloso"],
    "Xanxerê": ["Xanxerê", "Bom Jesus", "Faxinal dos Guedes"],
    "Xaxim": ["Xaxim", "Marema", "Lajeado Grande"]
}


def cadastrar_comarcas_judiciario_sc():
    """Cadastra as comarcas do Poder Judiciário de SC e vincula os municípios abrangentes."""
    
    try:
        # Busca o estado de Santa Catarina
        estado_sc = Estado.objects.get(sigla='SC')
        print(f"\n[INFO] Estado {estado_sc.nome} encontrado.")
        
        comarcas_criadas = 0
        comarcas_atualizadas = 0
        erros = []
        
        for nome_comarca, municipios_nomes in comarcas_sc.items():
            try:
                # Cria ou busca a comarca
                comarca, created = ComarcasPoderJudiciario.objects.get_or_create(
                    nome=nome_comarca,
                    estado=estado_sc
                )
                
                if created:
                    comarcas_criadas += 1
                    print(f"[CRIADA] Comarca '{nome_comarca}' cadastrada.")
                else:
                    comarcas_atualizadas += 1
                    print(f"[ATUALIZADA] Comarca '{nome_comarca}' já existe.")
                
                # Vincula os municípios abrangentes
                municipios_vinculados = []
                municipios_nao_encontrados = []
                
                for nome_municipio in municipios_nomes:
                    try:
                        # Busca o município no banco
                        municipio = Municipio.objects.get(
                            nome__iexact=nome_municipio,
                            estado=estado_sc
                        )
                        comarca.municipios_abrangentes.add(municipio)
                        municipios_vinculados.append(nome_municipio)
                    except Municipio.DoesNotExist:
                        municipios_nao_encontrados.append(nome_municipio)
                    except Municipio.MultipleObjectsReturned:
                        print(f"  [AVISO] Múltiplos municípios encontrados para '{nome_municipio}'")
                        # Pega o primeiro encontrado
                        municipio = Municipio.objects.filter(
                            nome__iexact=nome_municipio,
                            estado=estado_sc
                        ).first()
                        comarca.municipios_abrangentes.add(municipio)
                        municipios_vinculados.append(nome_municipio)
                
                if municipios_vinculados:
                    print(f"  [OK] {len(municipios_vinculados)} municípios vinculados: {', '.join(municipios_vinculados)}")
                
                if municipios_nao_encontrados:
                    print(f"  [ERRO] {len(municipios_nao_encontrados)} municípios não encontrados: {', '.join(municipios_nao_encontrados)}")
                    erros.append({
                        'comarca': nome_comarca,
                        'municipios_nao_encontrados': municipios_nao_encontrados
                    })
                    
            except Exception as e:
                print(f"[ERRO] Erro ao processar comarca '{nome_comarca}': {str(e)}")
                erros.append({
                    'comarca': nome_comarca,
                    'erro': str(e)
                })
        
        # Resumo final
        print("\n" + "="*60)
        print("RESUMO DA IMPORTAÇÃO")
        print("="*60)
        print(f"Comarcas criadas: {comarcas_criadas}")
        print(f"Comarcas atualizadas: {comarcas_atualizadas}")
        print(f"Total de comarcas processadas: {len(comarcas_sc)}")
        
        if erros:
            print(f"\n[ATENÇÃO] {len(erros)} erros encontrados:")
            for erro in erros:
                if 'municipios_nao_encontrados' in erro:
                    print(f"  - Comarca '{erro['comarca']}': Municípios não encontrados: {', '.join(erro['municipios_nao_encontrados'])}")
                else:
                    print(f"  - Comarca '{erro['comarca']}': {erro['erro']}")
        
        print("\n[CONCLUÍDO] Processo de cadastramento de comarcas finalizado.")
        
    except Estado.DoesNotExist:
        print("[ERRO] Estado de Santa Catarina (SC) não encontrado no banco de dados.")
        print("Execute primeiro: from automacoes.cria_estados import criar_estados; criar_estados()")
        return
    except Exception as e:
        print(f"[ERRO CRÍTICO] Erro ao executar script: {str(e)}")
        return


def listar_municipios_sem_comarca():
    """Lista todos os municípios de SC que não estão vinculados a nenhuma comarca."""
    try:
        estado_sc = Estado.objects.get(sigla='SC')
        municipios_sem_comarca = Municipio.objects.filter(
            estado=estado_sc,
            comarcas_abrangentes__isnull=True
        ).order_by('nome')
        
        if municipios_sem_comarca:
            print(f"\n[INFO] {municipios_sem_comarca.count()} municípios de SC sem comarca:")
            for municipio in municipios_sem_comarca:
                print(f"  - {municipio.nome}")
        else:
            print("\n[OK] Todos os municípios de SC estão vinculados a pelo menos uma comarca.")
            
    except Estado.DoesNotExist:
        print("[ERRO] Estado de Santa Catarina (SC) não encontrado.")


if __name__ == "__main__":
    print("Para executar este script, use:")
    print("  python manage.py shell")
    print("  >>> from automacoes.cria_comarcas_judiciario import cadastrar_comarcas_judiciario_sc")
    print("  >>> cadastrar_comarcas_judiciario_sc()")
    print("\nPara listar municípios sem comarca:")
    print("  >>> from automacoes.cria_comarcas_judiciario import listar_municipios_sem_comarca")
    print("  >>> listar_municipios_sem_comarca()")