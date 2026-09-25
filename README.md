# Rastreador de Leitura

API REST em Django + DRF pra acompanhar o que estou lendo — fanfic, mangá,
manhwa, webtoon, HQ, light novel e até matéria da faculdade — com uma estante
web que separa por grupo e marca capítulo sem abrir o admin.

Construído porque o Wattpad deixa votar, mas não deixa guardar nota própria,
nem separar "pausado" de "abandonado", nem ver tudo que leio em vários sites
numa lista só. Uso todo dia.

![Topo da estante, com o grupo Leitura de fã](docs/TelaLeitura.png)

![Resto da rolagem, com os grupos Quadrinhos, Livros e Matéria](docs/TelaGrupos.png)

*O topo da estante e o resto da rolagem. Cada seção sai do tipo da obra — não
existe campo `grupo` no banco.*

## O que faz

- **Estante** (`/`) — cards com selo de status, barra de progresso, título
  clicável pro site original e nota em estrelas.
- **Estante separada por grupo** — leitura de fã, quadrinhos, livros e matéria.
  O grupo é deduzido do tipo da obra, não é campo no banco.
- **Cadastro numa tela só** (`/obras/nova/`) — obra e leitura no mesmo POST,
  dentro de uma transação: capítulo inválido não deixa obra órfã no banco.
- **Botões `+1` / `-1`** direto no card: marca o capítulo sem sair da página, e
  a página volta pro mesmo card em vez de pular pro topo.
- **Status pelo selo** — clicar no selo do card abre os status e troca na hora,
  sem abrir a edição.
- **Excluir pela estante** — o 🗑 apaga a obra e a leitura juntas, com confirmação.
- **Edição pela estante** (`/leituras/<id>/editar/`) — o botão ✎ abre obra e
  leitura no mesmo formulário, salvos numa transação. Sem passar pelo admin.
- **Busca instantânea** — a caixa no topo filtra por título, autor, tipo ou
  plataforma enquanto você digita, e esconde a seção que ficou vazia. Só
  JavaScript, sem ida ao servidor.
- **Status que se corrige sozinho** — chegou no último capítulo vira
  `Finalizado` e grava a data; voltou atrás, volta pra `Lendo`.
- **Tema claro/escuro**, guardado no navegador.
- **API REST** (CRUD) em `/api/` — autenticada, e cada pessoa só enxerga a
  própria estante.
- **Admin** do Django pra cadastro em massa.

## Stack

Python · Django 5.2 · Django REST Framework · SQLite · HTML/CSS/JS sem framework

## Como rodar

```bash
git clone https://github.com/gabrielbastosg/rastreador-leitura.git
cd rastreador-leitura
python -m venv .venv
.venv\Scripts\activate        # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env         # Linux/macOS: cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abre `http://127.0.0.1:8000/`. A estante começa vazia — cadastre a primeira
obra em `/obras/nova/`.

O `.env` guarda a `SECRET_KEY` e o `DEBUG`, lidos com `python-decouple`.
Nunca vai pro Git — o modelo está no `.env.example`.

## Rotas web

| Rota | O que faz |
|---|---|
| `/` | estante — cards agrupados, busca, `+1`/`-1`, tema claro/escuro |
| `/obras/nova/` | cadastro de obra + leitura |
| `/leituras/<id>/editar/` | edição de obra + leitura na mesma tela |
| `/leituras/<id>/mover/` | `+1` / `-1` no capítulo (só POST) |
| `/leituras/<id>/status/` | troca o status pelo selo (só POST) |
| `/leituras/<id>/excluir/` | apaga a obra e a leitura (só POST) |
| `/contas/cadastro/` | cria a conta |
| `/contas/login/` e `/contas/logout/` | entrar e sair |
| `/admin/` | admin do Django |

## API

| Método | Rota | O que faz |
|---|---|---|
| `GET` `POST` | `/api/obras/` | lista e cadastra obras |
| `GET` `PUT` `PATCH` `DELETE` | `/api/obras/{id}/` | uma obra |
| `GET` `POST` | `/api/leituras/` | lista e cadastra leituras |
| `GET` `PUT` `PATCH` `DELETE` | `/api/leituras/{id}/` | uma leitura |

Dois `ModelViewSet` registrados num `DefaultRouter`, então a API navegável do
DRF responde no navegador em `/api/`.

**Tudo exige login** (`permission_classes = [IsAuthenticated]`) e devolve só o
que é seu: cada ViewSet troca o atributo `queryset` por um `get_queryset()` que
filtra por `request.user`. O atributo seria calculado uma vez, na importação do
módulo, quando não existe request nenhum pra consultar; o método roda a cada
chamada. Como o `queryset` some da classe, o `DefaultRouter` perde de onde tirar
o nome das rotas — daí o `basename=` no `register`.

Pedir a obra de outra pessoa dá **404**, não 403: ela não está no queryset,
então pra API não existe. Mesma ideia do
`get_object_or_404(..., obra__dono=request.user)` nas views web.

O `dono` nunca vem do corpo do POST — é um `HiddenField` com
`CurrentUserDefault()`, que lê o usuário do request. Mandar `"dono": 2` na mão
não faz nada. É `HiddenField` e não `read_only` de propósito: a
`UniqueConstraint(fields=['dono', 'link'])` precisa do campo pra montar o
validador de unicidade, e campo read-only sem default o DRF pula em silêncio —
link repetido deixaria de dar 400 com mensagem e viraria erro 500.

Já a `obra` de uma leitura vem de quem chama, e aí não dá pra adivinhar a
certa: um `validate_obra()` no serializer recusa com **400** a obra que não é
sua. Sem ele, um POST bastaria pra pendurar uma leitura na estante alheia.

O menu de obras da API navegável também é filtrado, num `get_fields()` que troca
o `queryset` do campo `obra` pelas obras de quem pediu. Validar depois impedia a
gravação, mas o formulário HTML já tinha desenhado o título de todo mundo no
`<select>` — vazamento de leitura, não de escrita. Com o queryset filtrado, a
obra alheia falha no próprio campo e a mensagem vira o genérico "Pk inválido",
em vez de "Essa obra não é sua.". É de propósito, e é a mesma linha do 404: pra
você, a obra de outra pessoa não existe.

`GET /api/leituras/` devolve `obra_titulo` junto, via `source='obra.titulo'`,
pra não precisar de uma segunda chamada só pelo nome da obra.

## Modelo de dados

**Obra** — `tipo` (Fanfic/Mangá/Manhwa/Webtoon/HQ/Light Novel/Matéria),
`titulo`, `autor`, `plataforma`, `link` (único, opcional),
`total_capitulos` (opcional).

**Leitura** — FK pra `Obra`, `capitulo_atual`, `status`
(Lendo/Pausado/Finalizado/Abandonado), `nota` de 1 a 5, `criado_em`,
`atualizado_em`, `encerrado_em`.

Obra e leitura são separadas porque a mesma obra pode ser relida.
`total_capitulos` aceita nulo: fanfic em andamento não tem total. `link` também:
matéria da faculdade é PDF, não tem URL.

## Decisões que valem explicar

**A regra de validação mora num lugar só.** `Leitura.clean()` barra
`capitulo_atual` maior que o total da obra. O DRF **não** chama `full_clean()`
sozinho, então `LeituraSerializer.validate()` monta uma `Leitura` e chama o
mesmo `clean()` — em vez de reescrever a regra em dois lugares e um dos dois
ficar pra trás.

**O status só muda no par que o app tem certeza.** Chegou no total →
`Finalizado`. Saiu do total estando `Finalizado` → `Lendo`. `Pausado` e
`Abandonado` nunca são tocados automaticamente: a diferença entre os dois é
decisão do leitor, não dá pra deduzir do número do capítulo.

**Os botões usam POST, não GET.** Um `<form>` com `{% csrf_token %}`,
`@require_POST` na view e redirect depois de salvar — mudança de estado por
link seria disparada por qualquer prefetch do navegador, e o F5 repetiria a
ação.

**O intervalo é conferido no servidor.** `save()` não chama `clean()`, então a
view valida o capítulo antes de gravar em vez de confiar no botão.

**As estrelas são uma `@property` no modelo.** Template do Django não faz laço
com contador nem aritmética; a nota vira `★★★★☆` em Python.

**O grupo da estante não é campo no banco.** Ele sai de um dicionário
`{tipo: grupo}` no modelo, exposto por uma `@property`. Guardar os dois seria
convidar os dois a discordarem — uma obra marcada `Manhwa` com grupo `Matéria`,
e nenhum jeito de saber qual está certo. A ordem das seções na tela também vem
desse dicionário, então não existe uma segunda lista pra ficar pra trás.

As onze decisões do projeto, cada uma em pergunta e resposta com o lugar onde
mora no código: [`docs/decisoes-perguntas.md`](docs/decisoes-perguntas.md).

## Testes

```bash
python manage.py test
```

Quarenta e um testes, sem dependência externa — o Django cria e destrói um banco
próprio a cada execução.

Cobrem o que **decide** alguma coisa:

- **`Obra.grupo`** — o tipo mapeado e o tipo que não está no dicionário.
- **`Leitura.clean()`** — capítulo acima do total, obra sem total (fanfic em
  andamento) e capítulo exatamente no total, que é a fronteira da regra.
- **`Leitura.estrelas`** — sem nota, nota no meio e nota cheia.
- **A view `mover_capitulo` inteira** — o avanço, a finalização automática ao
  bater no total, o teto, o piso e a recusa de `GET` pelo `@require_POST`.
- **As views `nova_obra` e `editar_leitura`** — o POST válido, os dois
  formulários voltando com erro cada um, o capítulo acima do total que não deixa
  nem a obra no banco (é esse que prova o `transaction.atomic`) e a edição que
  muda total e capítulo no mesmo POST.
- **O isolamento entre pessoas**, pela web e pela API — editar a leitura de
  outro dá 404; sem login a API não lista nada; a lista traz só o que é seu
  (com obra das duas pessoas no banco, senão um filtro quebrado passaria);
  `DELETE` na obra alheia dá 404 e não apaga; `dono` mandado no corpo é
  ignorado; leitura não gruda em obra de outro; e o menu de obras da API
  navegável não desenha título alheio.

Ficaram de fora de propósito `__str__` e o admin: não decidem nada, não têm como
estar errados.

## Próximos passos

- Filtros na API com `django-filter` (status, tipo, plataforma)
- Contagem do grupo acompanhando a busca, e aviso quando nada é encontrado
- Validador de senha exigindo pelo menos uma letra. Hoje o Django só recusa senha
  **inteiramente numérica** (`NumericPasswordValidator`), então `1234567!` é aceita.
  Exigir uma letra é regra comum em outros sites e precisaria de um validador próprio
  no `AUTH_PASSWORD_VALIDATORS` — enquanto não existe, o texto de ajuda do formulário
  descreve só o que é de fato validado.
- Mover as rotas do `leituras` para um `leituras/urls.py` próprio, como no `contas`.
  Hoje elas moram no `config/urls.py` e funcionam — a mudança é organização, não correção,
  então vale pegar carona na próxima vez que o app for mexido, não parar para fazer sozinha.
  **Regra adotada:** não mudar o que funciona, mas não repetir o padrão antigo em código novo.
- `base.html` e diretório de templates do projeto. Hoje cada template repete o HTML inteiro
  (`<head>`, script do tema, header com o menu de tema), e o `_campos.html` está duplicado entre
  `leituras` e `contas` — cópia deliberada, para o app `contas` não depender do `leituras`.
  A solução boa é um diretório de templates fora dos apps (`DIRS` no `TEMPLATES`) guardando
  `base.html` e `_campos.html`: aí não é um app dependendo do outro, são os dois usando o comum.
  **Regra adotada:** lógica se reaproveita; layout pequeno se copia — um parcial de apresentação
  de 12 linhas não vale o acoplamento entre apps.
- Separar os erros do campo de confirmação de senha, no cadastro. O `UserCreationForm` valida a
  senha depois que os dois campos batem e pendura **tudo** em `password2` — tanto "esta senha é
  muito curta" quanto "os dois campos de senha não correspondem". Na tela, os erros de regra de
  senha aparecem embaixo de *Confirmação de senha*, e a pessoa não sabe qual campo corrigir.
  O conserto é mover só os erros de validador para `password1`, deixando o de correspondência onde
  está. Encontrado clicando no botão, não lendo código — nenhum teste pegaria, porque
  tecnicamente funciona.
