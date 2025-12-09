function toggleChatbot() {
    const chatbotContainer = document.getElementById('chatbot-container');
    if (chatbotContainer.style.display === 'none' || chatbotContainer.style.display === '') {
        chatbotContainer.style.display = 'flex'; // Mostra o chatbot
    } else {
        chatbotContainer.style.display = 'none'; // Esconde o chatbot
    }
}