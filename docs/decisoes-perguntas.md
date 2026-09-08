# Por que o código é assim — 11 perguntas

Cada decisão do projeto escrita como pergunta e resposta, com o lugar onde ela
mora. Serve pra reler antes de uma entrevista e pra lembrar o motivo de uma
escolha seis meses depois, quando o motivo já sumiu da cabeça.

---

## 1. Por que `grupo` é uma `@property` e não uma coluna no banco?

`leituras/models.py:17` e `leituras/models.py:38`

O grupo sai do dicionário `GRUPOS`, e a property faz `GRUPOS.get(self.tipo, 'Outros')`.
Não há consulta ao banco: `self.tipo` já está em memória e a busca é num dicionário
Python.

**Se fosse coluna:** cadastrar "Solo Leveling" como Manhwa grava `Quadrinhos`. Trocar
o tipo depois pra Light Novel muda `tipo` e **não** muda a coluna `grupo` — os dois
passam a discordar, e não existe jeito de saber qual está certo. Com a property isso
é impossível: o grupo é recalculado toda vez que alguém pergunta.

A ordem das seções na tela também sai desse dicionário, então não há uma segunda
lista pra ficar desatualizada.

## 2. Por que `link` precisa de `null=True` **e** `blank=True`?

`leituras/models.py:31` — `models.URLField(unique=True, null=True, blank=True)`

São camadas diferentes: `null` é o banco (a coluna aceita `NULL`), `blank` é a
validação (formulário e `full_clean`).

Matéria da faculdade é PDF e não tem URL, então o campo fica vazio em várias obras.
Só com `blank=True`, o vazio viraria string vazia — e a **segunda** obra sem link
tentaria gravar `''` numa coluna `unique`, batendo em `IntegrityError`. Com
`null=True` o vazio vira `NULL`, e em SQL `NULL` não é igual a `NULL`: não é um valor,
é ausência de valor. Vinte obras sem link convivem debaixo do `unique`.

A documentação do Django recomenda evitar `null` em campo de texto — e abre exceção
explícita justamente pra `unique=True` com `blank=True`.

## 3. Por que os dois `is_valid()` rodam antes do `if`?

`leituras/views.py:67`

```python
obra_ok = form_obra.is_valid()
leitura_ok = form_leitura.is_valid()
if obra_ok and leitura_ok:
```

O `and` do Python faz curto-circuito: se o lado esquerdo é falso, o direito nem é
avaliado. E `is_valid()` não é só uma pergunta — ele **preenche `form.errors`**.

Numa linha só (`if form_obra.is_valid() and form_leitura.is_valid()`), um envio com
erro nos dois formulários validaria apenas o primeiro. A tela voltaria com **uma**
mensagem, no formulário da obra, e o campo do capítulo apareceria sem erro — não por
estar certo, mas porque ninguém olhou. O usuário corrige, reenvia, e só então descobre
o segundo erro. Duas viagens pra descobrir dois erros que já existiam na primeira.

## 4. Por que os botões +1 / −1 são POST e não link?

`leituras/views.py:35` (`@require_POST`) e o `<form>` com `{% csrf_token %}` em
`leituras/templates/leituras/lista.html`

GET é definido como seguro pela especificação do HTTP — não muda estado. Uma URL que
avança capítulo quebra essa promessa, e quem visita URL sem clicar é muita gente:
prefetch do navegador, prerender, antivírus, extensão, bot. Além disso, com link o F5
depois de avançar repetiria a ação; com POST + redirect, o F5 só recarrega a estante.

**O `csrf_token` é outra defesa, pra outro ataque.** O `require_POST` garante o método,
não a origem. Um site qualquer pode enviar um POST pro seu domínio e o navegador manda
o cookie de sessão junto. O token quebra isso porque é gerado pelo servidor dentro da
sua página: o atacante consegue enviar às cegas, mas não consegue **ler** uma página
sua pra descobrir o valor — a política de mesma origem proíbe. O Django compara o
token do corpo com o da sessão, e o corpo é o que ninguém preenche por você.

## 5. Por que `full_clean()` na mão na `nova_obra` e nenhum na `editar_leitura`?

`leituras/views.py:76` e `leituras/models.py:53`

A regra em jogo é a do `Leitura.clean()`: capítulo não pode passar do total da obra.
Ela começa assim:

```python
if not self.obra_id or self.capitulo_atual is None:
    return
```

**No cadastro:** o `LeituraForm` tem `capitulo_atual`, `status` e `nota` — não tem
`obra`. O `ModelForm` até chama `full_clean()` por baixo, mas a obra ainda não foi
atribuída, `obra_id` é `None`, e a regra sai pelo `return` **sem reclamar**. Falha
silenciosa. Por isso o `full_clean(exclude=['obra'])` explícito, logo depois do
`leitura.obra = obra`.

**Na edição:** o form é construído com `instance=leitura`, uma linha que já existe no
banco e já tem `obra_id` preenchido. A regra roda dentro do próprio `is_valid()`, e um
`full_clean()` na mão seria a mesma checagem duas vezes.

Efeito colateral que isso garante: mudar **total e capítulo no mesmo POST** valida
contra o total novo, porque `form_obra.is_valid()` roda antes e altera o mesmo objeto
`obra` que está na memória da leitura.

## 6. Por que `transaction.atomic()` com dois `save()`?

`leituras/views.py:104`

São dois `UPDATE`. Sem a transação, um erro no segundo deixaria o título novo gravado
e a leitura não.

O problema não é perder a alteração — é o estado partido. O usuário vê a tela de erro
e conclui "não salvou", mas salvou metade, e não há como saber qual. Falha completa é
honesta: o erro na tela e o banco dizem a mesma coisa. O `atomic` dá `ROLLBACK` em
qualquer exceção: tudo ou nada.

## 7. Por que `dict.fromkeys` e não `set()` pra tirar repetição?

`leituras/views.py:27`

```python
ordem = list(dict.fromkeys(Obra.GRUPOS.values())) + ['Outros']
```

`GRUPOS.values()` repete "Quadrinhos" quatro vezes (Mangá, Manhwa, Webtoon, HQ). Os
dois removem duplicata, mas `set` é desordenado por construção — a ordem sai do hash,
e as seções da tela apareceriam embaralhadas, numa sequência que pode até parecer
estável e mudar depois.

`dict` preserva ordem de inserção (garantido desde o Python 3.7). Então a ordem das
seções é a ordem em que `GRUPOS` foi escrito no modelo, e não existe uma segunda lista
pra manter em dia quando um tipo novo entrar.

## 8. Por que `passo` é comparado com a string `'1'`?

`leituras/views.py:38`

```python
passo = 1 if request.POST.get('passo') == '1' else -1
```

Tudo que chega em `request.POST` é string — a conversão pra inteiro que existe no
Django acontece no `cleaned_data` do formulário, e aqui não há formulário, é POST cru.

E o `if/else` prende o resultado em exatamente `+1` ou `−1`. Qualquer outra coisa que
chegue (`999`, `abc`, vazio) vira `−1`, sem exceção e sem pulo. Isso importa porque
obra em andamento tem `total_capitulos = None`, e a guarda seguinte

```python
if novo < 0 or (total is not None and novo > total):
```

não tem teto pra comparar nesse caso.

## 9. Por que a leitura sobe pro topo da estante quando avança capítulo?

`leituras/models.py:45` e `:47`, com `leituras/views.py:21`

`atualizado_em` é `auto_now=True`: regravado a cada `save()`. A lista usa
`order_by('-atualizado_em')`. Logo, o que foi salvo por último aparece primeiro.

`criado_em` é `auto_now_add=True` e grava **uma vez só**, no `INSERT`, nunca mais.
`auto_now_add` é nascimento, `auto_now` é último toque.

**Pendência conhecida:** `auto_now` dispara em qualquer `save()`, então editar só a
nota pelo botão ✎ também joga a obra pro topo. A estante quer dizer "avancei nisso
agora", mas o campo só sabe dizer "salvei isso agora". O conserto seria um campo
próprio de último avanço, tocado apenas na `mover_capitulo`.

## 10. Por que `timezone.localdate()` e não `date.today()`?

`leituras/views.py:50`

Uma leitura finalizada às 21h de terça gravava a data de quarta. O
`timezone.localdate()` converte o instante em UTC para o fuso de `TIME_ZONE` antes de
extrair a data.

Três peças que precisam concordar:

- `USE_TZ = True` — o banco guarda tudo em UTC (e deve continuar assim);
- `TIME_ZONE = 'America/Sao_Paulo'` — define o que "local" quer dizer;
- `timezone.localdate()` — é quem pede a conversão na hora de usar.

O bug era as duas primeiras discordando da terceira: o `localdate()` já estava no
código e `TIME_ZONE` ainda era `'UTC'`. O conserto (commit `ddf771f`) mexeu só em
`config/settings.py`, duas linhas.

## 11. O que `on_delete=models.CASCADE` decide?

`leituras/models.py:42`

Apagar uma obra apaga junto todas as leituras que apontam pra ela. O argumento é
**obrigatório** — o Django não tem padrão, porque não existe padrão seguro: apagar em
cascata e recusar a exclusão são comportamentos opostos, e a escolha é de quem
modela.

**Por que `CASCADE` aqui:** leitura sem obra não significa nada, viraria lixo no
banco.

**Contra-argumento honesto:** com `CASCADE`, apagar uma obra por engano no admin leva
junto a nota, a data de término e o histórico daquela leitura, sem perguntar.
`PROTECT` obrigaria a apagar as leituras primeiro, de propósito. Num app cujo valor
**é** esse histórico, dá pra defender os dois lados — é decisão de produto, não de
sintaxe.
