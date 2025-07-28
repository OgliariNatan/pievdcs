# -*- coding: utf-8 -*-

"""Script para cadastrar comarcas dos estados e seus respectivos municipios.

    Para uso em ambiente de desenvolvimento ou para inicializar o banco de dados com os estados brasileiros.

    @comando:
      python manage.py shell
      >>> from automacoes.cria_comarcas import cadastrar_comarcas_por_estado
      >>> cadastrar_comarcas_por_estado()
"""

from sistema_justica.models import Estado, Municipio


comarcas_por_estados = {
    "SC" : [
        "Abelardo Luz", "Anchieta", "Anita Garibaldi", "Araquari", "Araranguá", "Armazém", "Ascurra", "Balneário Camboriú", "Balneário Piçarras", "Barra Velha", "Biguaçu", "Blumenau - Foro Central",  "Blumenau - Fórum Universitário", "Bom Retiro", "Braço do Norte", "Brusque", "Caçador",       "Camboriú", "Campo Belo do Sul", "Campo Erê", "Campos Novos",
        "Canoinhas",
        "Capinzal",
        "Capital",
        "Capital - Estadual Bancário",
        "Capital - Continente",
        "Capital - Eduardo Luz",
        "Capital - Norte da Ilha",
        "Capivari de Baixo",
        "Catanduvas",
        "Chapecó",
        "Concórdia",
        "Coronel Freitas",
        "Correia Pinto",
        "Criciúma",
        "Cunha Porã",
        "Curitibanos",
        "Descanso",
        "Dionísio Cerqueira",
        "Forquilhinha",
        "Fraiburgo",
        "Garopaba",
        "Garuva",
        "Gaspar",
        "Guaramirim",
        "Herval D'Oeste",
        "Ibirama",
        "Içara",
        "Imaruí",
        "Imbituba",
        "Indaial",
        "Ipumirim",
        "Itá",
        "Itaiópolis",
        "Itajaí",
        "Itapema",
        "Itapiranga",
        "Itapoá",
        "Ituporanga",
        "Jaguaruna",
        "Jaraguá do Sul",
        "Joaçaba",
        "Joinville",
        "Joinville - Fórum Fazendário",
        "Lages",
        "Laguna",
        "Lauro Müller",
        "Lebon Régis",
        "Mafra",
        "Maravilha",
        "Meleiro",
        "Modelo",
        "Mondaí",
        "Navegantes",
        "Orleans",
        "Otacílio Costa",
        "Palhoça",
        "Palmitos",
        "Papanduva",
        "Penha",
        "Pinhalzinho",
        "Pomerode",
        "Ponte Serrada",
        "Porto Belo",
        "Porto União",
        "Presidente Getúlio",
        "Quilombo",
        "Rio do Campo",
        "Rio do Oeste",
        "Rio do Sul",
        "Rio Negrinho",
        "Santa Cecília",
        "Santa Rosa do Sul",
        "Santo Amaro da Imperatriz",
        "São Bento do Sul",
        "São Carlos",
        "São Domingos",
        "São Francisco do Sul",
        "São João Batista",
        "São Joaquim",
        "São José",
        "São José do Cedro",
        "São Lourenço do Oeste",
        "São Miguel do Oeste",
        "Seara",
        "Sombrio",
        "Taió",
        "Tangará",
        "Tijucas",
        "Timbó",
        "Trombudo Central",
        "Tubarão",
        "Turvo",
        "Urubici",
        "Urussanga",
        "Videira",
        "Xanxerê",
        "Xaxim"
    ]
}



municipios_por_comarcas = {
    "Pinhalzinho": [
        "Pinhalzinho", "Saudades", "Nova Erechim",
    ],
    "Maravilha": [
        "Maravilha", "Guaraciaba", "São Miguel do Oeste", "Descanso"
    ]
}



def cadastrar_comarcas_por_estado():
    """Cadastra as comarcas por estado no banco de dados."""
    for sigla_estado, comarcas in comarcas_por_estados.items():
        estado, created = Estado.objects.get_or_create(sigla=sigla_estado)
        for comarca in comarcas:
            Municipio.objects.get_or_create(nome=comarca, estado=estado)