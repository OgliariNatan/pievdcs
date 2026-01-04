import requests
import time
# Ajuste o import abaixo para o nome correto do seu app onde estão os models
from sistema_justica.models import Estado, Municipio 

def atualizar_limites_brasil():
    headers = {'User-Agent': 'AtualizadorGeo/1.0'}
    
    # 1. Busca todos os estados cadastrados no seu banco
    estados = Estado.objects.all()
    print(f"Iniciando atualização para {estados.count()} estados...")

    for estado in estados:
        if not estado.sigla:
            print(f"Estado ID {estado.id} sem sigla. Pulando.")
            continue
            
        print(f"\n>>> Processando {estado.sigla}...")
        
        # ---------------------------------------------------------
        # PASSO A: Atualizar Limites do ESTADO
        # ---------------------------------------------------------
        try:
            # Busca a geometria do estado
            url_uf = f"https://servicodados.ibge.gov.br/api/v3/malhas/estados/{estado.sigla}?formato=application/vnd.geo+json&qualidade=minima"

            resp_uf = requests.get(url_uf, headers=headers)
            
            if resp_uf.status_code == 200:
                geo_uf = resp_uf.json()
                
                # Salva o GeoJSON nos limites
                estado.limites = geo_uf
                
                # Bônus: Tenta salvar o código IBGE do estado se estiver vazio (vem nas properties como 'codarea')
                if not estado.sigla_IBGE and 'properties' in geo_uf and 'codarea' in geo_uf['properties']:
                    estado.sigla_IBGE = int(geo_uf['properties']['codarea'])
                
                estado.save()
                print(f"   [v] Estado {estado.sigla} atualizado.")
            else:
                print(f"   [x] Erro ao baixar UF {estado.sigla}: {resp_uf.status_code}")
                
        except Exception as e:
            print(f"   [!] Erro crítico no estado: {e}")

        # ---------------------------------------------------------
        # PASSO B: Atualizar Limites dos MUNICÍPIOS (Em lote)
        # ---------------------------------------------------------
        try:
            # Busca TODOS os municípios daquele estado de uma só vez
            
            url_mun = f"https://servicodados.ibge.gov.br/api/v3/malhas/estados/{estado.sigla}?intrarregiao=municipio&formato=application/vnd.geo+json&qualidade=minima"
            resp_mun = requests.get(url_mun, headers=headers)
            
            if resp_mun.status_code == 200:
                fc = resp_mun.json() # FeatureCollection
                features = fc.get('features', [])
                count_ok = 0
                
                print(f"   ... Processando {len(features)} municípios retornados pelo IBGE...")
                
                for feature in features:
                    props = feature.get('properties', {})
                    geom = feature.get('geometry', {})
                    
                    # O IBGE retorna 'codarea' (ex: "4210600")
                    cod_ibge_str = props.get('codarea')
                    if not cod_ibge_str:
                        continue
                        
                    cod_ibge = int(cod_ibge_str)
                    
                    # TENTATIVA 1: Busca pelo Código IBGE (Mais preciso)
                    mun_obj = Municipio.objects.filter(codigo_ibge=cod_ibge).first()
                    
                    # TENTATIVA 2: Se não achar pelo código, busca pelo Nome + Estado
                    if not mun_obj:
                        # O nome no IBGE pode vir como 'nom_municip'
                        # Para garantir, usamos iexact (case insensitive)
                        nome_mun = props.get('nom_municip')
                        if nome_mun:
                            mun_obj = Municipio.objects.filter(nome__iexact=nome_mun, estado=estado).first()
                            
                            # Se encontrou pelo nome, aproveita e SALVA o código IBGE para a próxima vez
                            if mun_obj:
                                mun_obj.codigo_ibge = cod_ibge
                    
                    # Se encontrou o município no banco, salva o JSON
                    if mun_obj:
                        mun_obj.limites = geom
                        mun_obj.save()
                        count_ok += 1
                
                print(f"   [v] {count_ok} municípios atualizados em {estado.sigla}.")
            
            else:
                print(f"   [x] Erro ao baixar municípios de {estado.sigla}.")

        except Exception as e:
            print(f"   [!] Erro crítico nos municípios: {e}")

        # Pausa de segurança para não sobrecarregar a API
        time.sleep(0.5)

# Executar a função

atualizar_limites_brasil()
print("\n" + "="*50)
print("\nAtualização de limites concluída.")
print("\n" + "="*50)