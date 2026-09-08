const campo = document.getElementById('busca');
const itens = document.querySelectorAll('.item');
const secoes = document.querySelectorAll('.grupo');

campo.addEventListener('input', () => {
    const termo = campo.value.toLowerCase();

    itens.forEach((item) => {
        const texto = item.textContent.toLowerCase();
        item.hidden = !texto.includes(termo);
    });
    
    secoes.forEach((secao) => {
        const visiveis = secao.querySelectorAll('.item:not([hidden])');
        secao.hidden = visiveis.length === 0;
    });
});