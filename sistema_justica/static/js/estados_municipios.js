function carregarEstadosMunicipios(estadosUrl, municipiosUrl) {
    let estados = {};
    let municipios = {};

    // Carrega os estados
    fetch(estadosUrl)
        .then(response => response.json())
        .then(data => {
            estados = data;
            const estadoSelect = document.getElementById('estado');
            if (!estadoSelect) return;
            Object.entries(estados).forEach(([codigo, info]) => {
                const option = document.createElement('option');
                option.value = info.sigla;
                option.text = info.nome;
                estadoSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Erro ao carregar estados:', error);
        });

    // Carrega os municípios
    fetch(municipiosUrl)
        .then(response => response.json())
        .then(data => {
            municipios = data;
        })
        .catch(error => {
            console.error('Erro ao carregar municípios:', error);
        });

    // Atualiza municípios ao selecionar estado
    document.addEventListener('change', function (e) {
        if (e.target && e.target.id === 'estado') {
            const estadoSigla = e.target.value;
            const municipioSelect = document.getElementById('municipio');
            municipioSelect.innerHTML = '<option value="">Selecione o Município</option>';

            Object.entries(municipios).forEach(([codigo, info]) => {
                // Supondo que municipios.json tem {"3550308": {"nome": "São Paulo", "estado": "SP"}, ...}
                if (info.estado === estadoSigla) {
                    const option = document.createElement('option');
                    option.value = info.nome;
                    option.text = info.nome;
                    municipioSelect.appendChild(option);
                }
            });
        }
    });
}