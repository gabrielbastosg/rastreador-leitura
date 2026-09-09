const raiz = document.documentElement;
const botao = document.getElementById('botao-tema');
const menu = document.getElementById('menu-tema');
const opcoes = menu.querySelectorAll('.tema__opcao');
const ICONES = { claro: '☀️', escuro: '🌙', sepia: '📜' };

function pintarBotao() {
    const atual = raiz.dataset.tema;
    botao.textContent = ICONES[atual] || ICONES.claro;
    opcoes.forEach(opcao => {
        if (opcao.dataset.temaOpcao === atual) {
            opcao.setAttribute('aria-current', 'true');
        } else {
            opcao.removeAttribute('aria-current');
        }
    });
}

function abrirMenu(abrir) {
    menu.hidden = !abrir;
    botao.setAttribute('aria-expanded', abrir);
}

botao.addEventListener('click', () => abrirMenu(menu.hidden));

opcoes.forEach(opcao => {
    opcao.addEventListener('click', () => {
        raiz.dataset.tema = opcao.dataset.temaOpcao;
        localStorage.setItem('tema', raiz.dataset.tema);
        pintarBotao();
        abrirMenu(false);
    });
});

document.addEventListener('click', evento => {
    if (!evento.target.closest('.tema')) {
        abrirMenu(false);
    }
});

document.addEventListener('keydown', evento => {
    if (evento.key === 'Escape') {
        abrirMenu(false);
    }
});

pintarBotao();