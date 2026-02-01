# -*- coding: utf-8 -*-
"""
    Funções auxiliares para gerar gráficos Plotly
    dir: MAIN/utils/plotly_helpers.py
    @author: OgliariNatan
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Any
import json


def criar_grafico_incidencias_mensais(
    dados_incidencias: Dict[str, int],
    comarcas: List[Dict[str, Any]],
    titulo: str = "Incidências de Violência por Mês"
) -> str:
    """
    Cria gráfico de barras interativo com filtro por comarca
    
    Args:
        dados_incidencias: Dict com meses e quantidades por comarca
        comarcas: Lista de comarcas com seus dados
        titulo: Título do gráfico
    
    Returns:
        HTML do gráfico Plotly
    """
    
    # Criar figura
    fig = go.Figure()
    
    # Cores consistentes com o padrão PIEVDCS
    cores_violencia = {
        'Física': '#dc2626',      # Vermelho
        'Psicológica': '#ea580c',  # Laranja
        'Sexual': '#8b5cf6',       # Roxo
        'Patrimonial': '#0891b2',  # Ciano
        'Moral': '#16a34a'         # Verde
    }
    
    meses_labels = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    
    # Adicionar traço para cada comarca (inicialmente invisível, exceto "Todas")
    for idx, comarca_info in enumerate(comarcas):
        comarca_nome = comarca_info['nome']
        dados_comarca = comarca_info.get('dados_mensais', {})
        
        valores = [dados_comarca.get(mes.lower(), 0) for mes in meses_labels]
        
        fig.add_trace(go.Bar(
            name=comarca_nome,
            x=meses_labels,
            y=valores,
            visible=(idx == 0),  # Apenas a primeira visível (Todas)
            marker=dict(
                color='#8b5a9f',  # Cor padrão PIEVDCS
                line=dict(color='#6d4a7f', width=1)
            ),
            hovertemplate='<b>%{x}</b><br>Casos: %{y}<br>Comarca: ' + comarca_nome + '<extra></extra>'
        ))
    
    # Criar botões de dropdown para filtrar por comarca
    botoes_dropdown = []
    for idx, comarca in enumerate(comarcas):
        visibilidade = [False] * len(comarcas)
        visibilidade[idx] = True
        
        botoes_dropdown.append(
            dict(
                label=comarca['nome'],
                method='update',
                args=[
                    {'visible': visibilidade},
                    {'title': f"{titulo} - {comarca['nome']}"}
                ]
            )
        )
    
    # Layout do gráfico
    fig.update_layout(
        title=dict(
            text=titulo,
            font=dict(size=20, family='Inter, sans-serif', color='#1f2937')
        ),
        xaxis=dict(
            title='Meses do Ano',
            tickangle=-45,
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title='Número de Casos',
            tickfont=dict(size=12)
        ),
        updatemenus=[
            dict(
                active=0,
                buttons=botoes_dropdown,
                direction='down',
                pad={'r': 10, 't': 10},
                showactive=True,
                x=0.01,
                xanchor='left',
                y=1.15,
                yanchor='top',
                bgcolor='#f3f4f6',
                bordercolor='#d1d5db',
                font=dict(size=12)
            )
        ],
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter, sans-serif'),
        height=500,
        margin=dict(t=100, l=60, r=20, b=80)
    )
    
    # Adicionar grid
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e5e7eb')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e5e7eb')
    
    return fig.to_html(
        include_plotlyjs=False,
        div_id='grafico-incidencias',
        config={'displayModeBar': True, 'displaylogo': False}
    )


def criar_mapa_bairros_comarca(
    bairros_data: List[Dict[str, Any]],
    comarcas: List[Dict[str, Any]],
    geojson_municipios: Dict = None
) -> str:
    """
    Cria mapa interativo com marcadores por bairro, coloridos por intensidade
    de violência e filtráveis por comarca
    
    Args:
        bairros_data: Lista com dados dos bairros (lat, lon, qtd_casos, tipo_violencia)
        comarcas: Lista de comarcas
        geojson_municipios: GeoJSON dos municípios (opcional)
    
    Returns:
        HTML do mapa Plotly
    """
    
    # Converter para DataFrame
    df = pd.DataFrame(bairros_data)
    
    # Criar figura com Scattermapbox
    fig = go.Figure()
    
    # Cores por tipo de violência (padrão PIEVDCS)
    cores_violencia = {
        'Física': '#dc2626',
        'Psicológica': '#ea580c',
        'Sexual': '#8b5cf6',
        'Patrimonial': '#0891b2',
        'Moral': '#16a34a'
    }
    
    # Adicionar traços para cada comarca
    for idx, comarca in enumerate(comarcas):
        comarca_nome = comarca['nome']
        df_comarca = df[df['comarca'] == comarca_nome] if 'comarca' in df.columns else df
        
        if df_comarca.empty:
            continue
        
        # Criar mapa de calor/densidade
        fig.add_trace(go.Scattermapbox(
            lat=df_comarca['latitude'],
            lon=df_comarca['longitude'],
            mode='markers',
            name=comarca_nome,
            visible=(idx == 0),
            marker=dict(
                size=df_comarca['qtd_casos'].apply(lambda x: min(x * 3, 30)),  # Tamanho proporcional
                color=df_comarca['qtd_casos'],
                colorscale='Reds',
                cmin=0,
                cmax=df['qtd_casos'].max() if not df.empty else 100,
                showscale=(idx == 0),  # Mostrar escala apenas no primeiro
                colorbar=dict(
                    title='Casos',
                    x=1.02,
                    xanchor='left'
                ),
                opacity=0.7,
                sizemode='diameter'
            ),
            text=df_comarca.apply(
                lambda row: f"<b>{row['bairro']}</b><br>"
                            f"Município: {row.get('municipio', 'N/A')}<br>"
                            f"Casos: {row['qtd_casos']}<br>"
                            f"Tipo: {row.get('tipo_violencia', 'N/A')}",
                axis=1
            ),
            hovertemplate='%{text}<extra></extra>'
        ))
    
    # Criar botões de dropdown para comarcas
    botoes_dropdown = []
    for idx, comarca in enumerate(comarcas):
        visibilidade = [False] * len(comarcas)
        visibilidade[idx] = True
        
        # Centralizar mapa na comarca selecionada
        centro_lat = comarca.get('centro_lat', -14.235)
        centro_lon = comarca.get('centro_lon', -51.925)
        zoom = comarca.get('zoom', 8)
        
        botoes_dropdown.append(
            dict(
                label=comarca['nome'],
                method='update',
                args=[
                    {'visible': visibilidade},
                    {
                        'mapbox.center': {'lat': centro_lat, 'lon': centro_lon},
                        'mapbox.zoom': zoom
                    }
                ]
            )
        )
    
    # Layout do mapa
    fig.update_layout(
        title=dict(
            text='Mapa de Violência por Bairro',
            font=dict(size=20, family='Inter, sans-serif', color='#1f2937')
        ),
        mapbox=dict(
            style='open-street-map',
            center=dict(lat=-14.235, lon=-51.925),
            zoom=5
        ),
        updatemenus=[
            dict(
                active=0,
                buttons=botoes_dropdown,
                direction='down',
                pad={'r': 10, 't': 10},
                showactive=True,
                x=0.01,
                xanchor='left',
                y=0.99,
                yanchor='top',
                bgcolor='rgba(255, 255, 255, 0.9)',
                bordercolor='#d1d5db',
                font=dict(size=12)
            )
        ],
        height=600,
        margin=dict(t=60, l=0, r=0, b=0)
    )
    
    return fig.to_html(
        include_plotlyjs=False,
        div_id='mapa-bairros',
        config={'displayModeBar': True, 'displaylogo': False, 'scrollZoom': True}
    )


def criar_mapa_choropleth_municipios(
    municipios_data: pd.DataFrame,
    geojson_path: str,
    comarca_filter: str = None
) -> str:
    """
    Cria mapa choropleth (colorido por município) com filtro de comarca
    
    Args:
        municipios_data: DataFrame com colunas [codigo_ibge, municipio, qtd_violencia, comarca]
        geojson_path: Caminho para arquivo GeoJSON dos municípios
        comarca_filter: Filtrar por comarca específica (opcional)
    
    Returns:
        HTML do mapa choropleth
    """
    
    # Carregar GeoJSON
    with open(geojson_path, 'r', encoding='utf-8') as f:
        geojson = json.load(f)
    
    # Filtrar por comarca se especificado
    if comarca_filter and comarca_filter != 'Todas':
        municipios_data = municipios_data[municipios_data['comarca'] == comarca_filter]
    
    # Criar mapa choropleth
    fig = px.choropleth_mapbox(
        municipios_data,
        geojson=geojson,
        locations='codigo_ibge',
        color='qtd_violencia',
        featureidkey='properties.codarea',  # Ajuste conforme seu GeoJSON
        color_continuous_scale='Reds',
        mapbox_style='open-street-map',
        center={'lat': -14.235, 'lon': -51.925},
        zoom=5,
        opacity=0.7,
        labels={'qtd_violencia': 'Casos'},
        hover_name='municipio',
        hover_data={
            'qtd_violencia': True,
            'comarca': True,
            'codigo_ibge': False
        }
    )
    
    fig.update_layout(
        title='Distribuição de Violência por Município',
        height=600,
        margin=dict(t=60, l=0, r=0, b=0)
    )
    
    return fig.to_html(
        include_plotlyjs=False,
        div_id='mapa-choropleth',
        config={'displayModeBar': True, 'displaylogo': False}
    )