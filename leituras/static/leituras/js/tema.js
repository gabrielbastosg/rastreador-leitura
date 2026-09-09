const raiz = document.documentElement;
const botao = document.getElementById('botao-tema');
const TEMAS = ['claro','escuro','sepia'];
const ICONES = { claro: '🌙', escuro: '📜', sepia: '☀️' };

function pintarBotao() {
    botao.textContent = ICONES[raiz.dataset.tema];
}

botao.addEventListener('click', () => {
    const proximo = (TEMAS.indexOf(raiz.dataset.tema) + 1) % TEMAS.length;
    raiz.dataset.tema = TEMAS[proximo];
    localStorage.setItem('tema', raiz.dataset.tema);
    pintarBotao();
});

pintarBotao();