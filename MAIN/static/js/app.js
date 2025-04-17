document.addEventListener("DOMContentLoaded", function () {
    // Exemplo de funcionalidade: Adicionar eventos aos botões
    const buttons = document.querySelectorAll(".submenu button");
    buttons.forEach((button) => {
        button.addEventListener("click", () => {
            alert(`Você clicou em: ${button.textContent}`);
        });
    });
});