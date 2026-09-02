const raiz = document.documentElement;
const botao = document.getElementById('botao-tema');

function pintarBotao() {
    botao.textContent = raiz.dataset.tema === 'escuro' ? '☀️' : '🌙';
}

botao.addEventListener('click', () => {
    raiz.dataset.tema = raiz.dataset.tema === 'escuro' ? 'claro' : 'escuro';
    localStorage.setItem('tema', raiz.dataset.tema);
    pintarBotao();
});

pintarBotao();