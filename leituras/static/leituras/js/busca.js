const campo = document.getElementById('busca');
const itens = document.querySelectorAll('.item');
const secoes = document.querySelectorAll('.grupo');
const semResultado = document.getElementById('sem-resultado');

campo.addEventListener('input', () => {
    const termo = campo.value.toLowerCase();

    itens.forEach((item) => {
        const texto = item.textContent.toLowerCase();
        item.hidden = !texto.includes(termo);
    });
    
    secoes.forEach((secao) => {
        const visiveis = secao.querySelectorAll('.item:not([hidden])');
        secao.querySelector('.grupo__contagem').textContent = visiveis.length;
        secao.hidden = visiveis.length === 0;
    });
    
    semResultado.hidden = document.querySelectorAll('.item:not([hidden])').length > 0;
});