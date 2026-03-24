// Função para atualizar o texto do botão do dropdown
function updateDropdownText2(selectedText) {
    const dropdownButton = document.getElementById('dropdownMenu2');
    dropdownButton.textContent = selectedText; // Atualiza o texto do botão
}

// Função para atualizar o texto do botão do dropdown
function updateDropdownText(selectedText) {
    const dropdownButton = document.getElementById('dropdownMenu');
    dropdownButton.textContent = selectedText; // Atualiza o texto do botão
}

function gerarCorAleatoria() {
    let cor = '#';
    const caracteres = '0123456789ABCDEF';
    for (let i = 0; i < 6; i++) {
        cor += caracteres[Math.floor(Math.random() * 16)];
    }
    return cor;
}

function gerarCoresAleatorias(qtd) {
    const cores = [];
    for (let i = 0; i < qtd; i++) {
        cores.push(gerarCorAleatoria());
    }
    return cores;
}

// Função para gerar um array de cores baseadas no lilás
function gerarCoresLilas(qtd) {
    const cores = [];
    for (let i = 0; i < qtd; i++) {
        cores.push(gerarCorLilas());
    }
    return cores;
}


