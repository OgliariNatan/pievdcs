import requests
import time
import osm2geojson
from sistema_justica.models import Municipio, Bairro

def get_osm_city_id(nome_cidade, sigla_uf):
    """
    Usa o Nominatim para descobrir o ID da Relação da cidade no OSM.
    Isso evita ambiguidade (Pinhalzinho-SP vs Pinhalzinho-SC).
    """
    url = "https://nominatim.openstreetmap.org/search"
    headers = {'User-Agent': 'BuscadorID/1.0'}
    params = {
        'city': nome_cidade,
        'state': sigla_uf,
        'country': 'Brazil',
        'format': 'json',
        'limit': 1,
        'osm_type': 'R' # Queremos apenas Relações (Limites oficiais)
    }
    
    try:
        resp = requests.get(url, params=params, headers=headers)
        data = resp.json()
        if data:
            # Retorna o OSM ID (ex: 296616 para Videira)
            # Adicionamos 3600000000 para converter ID de Relação em ID de Área do Overpass
            osm_id = int(data[0]['osm_id'])
            return osm_id
    except Exception as e:
        print(f"   [x] Erro Nominatim: {e}")
    
    return None

def importar_bairros_por_cidade(nome_cidade, sigla_uf):
    # 1. Busca o município no banco local
    try:
        municipio = Municipio.objects.get(nome__iexact=nome_cidade, estado__sigla__iexact=sigla_uf)
    except Municipio.DoesNotExist:
        print(f"[!] Município não encontrado no BD: {nome_cidade}-{sigla_uf}")
        return

    print(f"\n>>> 1. Identificando ID do mapa para: {municipio.nome} - {sigla_uf}...")
    
    # 2. Obtém o ID exato da cidade via Nominatim
    osm_relation_id = get_osm_city_id(nome_cidade, sigla_uf)
    
    if not osm_relation_id:
        print("   [!] Não foi possível encontrar a cidade no OpenStreetMap.")
        return
        
    print(f"   > ID da Relação encontrado: {osm_relation_id}")
    print(f"   > Buscando bairros dentro desta área...")

    # 3. Query Overpass OTIMIZADA (Busca direta pelo ID)
    # Isso elimina o Timeout 504 e a ambiguidade
    overpass_query = f"""
    [out:json][timeout:90];
    
    // Pega a relação da cidade pelo ID
    rel({osm_relation_id});
    
    // Converte a relação em área de busca
    map_to_area -> .searchArea;
    
    (
      // Busca Bairros Oficiais (admin_level 9 ou 10)
      relation(area.searchArea)["admin_level"~"9|10"]["type"="boundary"];
      
      // Busca Bairros Desenhados como 'Place' (comum em SC)
      relation(area.searchArea)["place"~"suburb|neighbourhood|quarter"];
      way(area.searchArea)["place"~"suburb|neighbourhood|quarter"];
    );
    
    out geom;
    """

    url_overpass = "https://overpass-api.de/api/interpreter"

    try:
        response = requests.get(url_overpass, params={'data': overpass_query})
        
        if response.status_code != 200:
            print(f"   [x] Erro API Overpass: {response.status_code} (Provável sobrecarga momentânea)")
            return

        # 4. Processamento com osm2geojson (Lida com multipolígonos complexos)
        try:
            geojson_data = osm2geojson.json2geojson(response.json())
        except Exception as e:
            print(f"   [!] Erro ao converter resposta para GeoJSON: {e}")
            return

        features = geojson_data.get('features', [])
        
        if not features:
            print("   [!] Nenhum bairro desenhado encontrado dentro dos limites desta cidade.")
            return

        print(f"   [v] Encontrados {len(features)} limites. Salvando...")

        count_novos = 0
        count_atualizados = 0

        for feature in features:
            props = feature.get('properties', {})
            geom = feature.get('geometry', {})
            
            # Pega o nome de várias fontes possíveis
            nome_bairro = props.get('name')
            if not nome_bairro:
                tags = props.get('tags', {})
                nome_bairro = tags.get('name')
            
            if not nome_bairro:
                continue

            # Remove prefixo "Bairro" se quiser padronizar
            # if nome_bairro.startswith("Bairro "): nome_bairro = nome_bairro[7:]

            bairro_obj, created = Bairro.objects.update_or_create(
                municipio=municipio,
                nome=nome_bairro,
                defaults={
                    'limites': geom
                }
            )

            if created:
                count_novos += 1
            else:
                count_atualizados += 1

        print(f"   Resumo: {count_novos} novos, {count_atualizados} atualizados.")

    except Exception as e:
        print(f"   [!] Erro crítico: {e}")
    
    time.sleep(2)


































# import requests
# import time
# # Ajuste o import abaixo para o local correto dos seus models
# from sistema_justica.models import Municipio, Bairro, Estado

# def buscar_bairros_corrigido(sigla_uf=None):
#     """
#     Busca bairros no Nominatim usando apenas query string para evitar erro 400.
#     """
    
#     # Headers OBRIGATÓRIOS (Use um User-Agent descritivo)
#     headers = {
#         'User-Agent': 'ProjetoPievdcs/1.0 (natanogliari@gmail.com)' 
#     }

#     # Filtra os municípios
#     if sigla_uf:
#         municipios = Municipio.objects.filter(estado__sigla=sigla_uf)
#     else:
#         municipios = Municipio.objects.all()

#     print(f"--- Iniciando busca de bairros para {municipios.count()} municípios ---")

#     for municipio in municipios:
#         # Se o município não tiver estado vinculado, pula
#         if not municipio.estado:
#             continue
            
#         nome_cidade = municipio.nome
#         sigla_estado = municipio.estado.sigla
        
#         print(f"\n> {nome_cidade} - {sigla_estado}: Buscando bairros...")

#         # URL base
#         url = "https://nominatim.openstreetmap.org/search"
        
#         # PARÂMETROS CORRIGIDOS:
#         # Removemos 'city' e 'state' e usamos apenas 'q'
#         # Adicionamos 'polygon_geojson' para vir o desenho
#         params = {
#             'q': f"bairro in {nome_cidade}, {sigla_estado}, Brazil",
#             'format': 'json',
#             'polygon_geojson': 1,  # Traz a geometria (polígono)
#             'addressdetails': 1,   # Para conferir se é mesmo bairro
#             'limit': 40,           # Tenta trazer até 40 resultados
#             'countrycodes': 'br'
#         }

#         try:
#             response = requests.get(url, params=params, headers=headers)
            
#             # Rate Limit: Pausa obrigatória de 1.5s entre requisições
#             time.sleep(1.5) 

#             if response.status_code == 200:
#                 resultados = response.json()
                
#                 if not resultados:
#                     print("   [!] Nenhum resultado encontrado.")
#                     continue

#                 novos = 0
#                 atualizados = 0

#                 for item in resultados:
#                     # 1. Verifica se tem GeoJSON (o desenho)
#                     geojson = item.get('geojson')
#                     if not geojson:
#                         continue
                    
#                     # 2. Verifica classificação para garantir que é bairro/subdistrito
#                     # O Nominatim retorna tipos variados. Vamos aceitar os comuns.
#                     tipo = item.get('type')             # administrative, suburb, neighbourhood
#                     classe = item.get('class')          # boundary, place
#                     endereco = item.get('address', {})
#                     tipo_end = item.get('addresstype')  # suburb, quarter, neighbourhood

#                     # Lista de tipos aceitos como "Bairro"
#                     tipos_aceitos = ['suburb', 'neighbourhood', 'quarter', 'residential', 'administrative']
                    
#                     # Validação simplificada: Se tem nome e é do tipo aceito
#                     eh_bairro = (tipo in tipos_aceitos) or (tipo_end in tipos_aceitos)
                    
#                     # Filtro extra: Se for 'administrative', confirmar se não é a própria cidade
#                     if tipo == 'administrative' and item.get('place_rank') < 12:
#                          # Rank baixo geralmente é cidade ou estado, ignorar
#                          eh_bairro = False

#                     if not eh_bairro:
#                         continue

#                     # 3. Pega o nome (preferência pelo address.suburb se existir)
#                     nome_bairro = endereco.get('suburb') or endereco.get('neighbourhood') or item.get('name')
                    
#                     # Remove prefixo "Bairro " se vier no nome (opcional, mas limpa o dado)
#                     # ex: "Bairro Pioneiro" -> "Pioneiro" (se preferir manter, remova as duas linhas abaixo)
#                     # if nome_bairro and nome_bairro.startswith("Bairro "):
#                     #     nome_bairro = nome_bairro[7:]

#                     if not nome_bairro:
#                         continue

#                     # 4. Salva no Banco de Dados
#                     try:
#                         bairro_obj, created = Bairro.objects.update_or_create(
#                             municipio=municipio,
#                             nome=nome_bairro,
#                             defaults={
#                                 'limites': geojson  # Salva o polígono aqui
#                             }
#                         )

#                         if created:
#                             novos += 1
#                         else:
#                             atualizados += 1
                            
#                     except Exception as db_err:
#                         print(f"      [Erro DB] {db_err}")

#                 if novos > 0 or atualizados > 0:
#                     print(f"   [v] Sucesso: {novos} novos, {atualizados} atualizados.")
#                 else:
#                     print("   [.] Nenhum bairro válido filtrado.")
            
#             else:
#                 # Se der erro, mostra o código e o motivo
#                 print(f"   [x] Erro API: {response.status_code} - {response.text}")

#         except Exception as e:
#             print(f"   [!] Erro de conexão: {e}")
#             time.sleep(2) # Espera um pouco mais em caso de erro de rede

# buscar_bairros_corrigido("SC")