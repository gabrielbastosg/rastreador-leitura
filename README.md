# Rastreador de Leitura

API REST em Django + DRF pra acompanhar o que estou lendo — fanfics, mangás,
manhwas e webtoons — com uma estante web pra marcar capítulo sem abrir o admin.

Construído porque o Wattpad deixa votar, mas não deixa guardar nota própria,
nem separar "pausado" de "abandonado", nem ver tudo que leio em vários sites
numa lista só. Uso todo dia.

![Estante](docs/TelaLeitura.png)

## O que faz

- **Estante** (`/`) — cards com selo de status, barra de progresso, título
  clicável pro site original e nota em estrelas.
- **Botões `+1` / `-1`** direto no card: marca o capítulo sem sair da página.
- **Status que se corrige sozinho** — chegou no último capítulo vira
  `Finalizado` e grava a data; voltou atrás, volta pra `Lendo`.
- **Tema claro/escuro**, guardado no navegador.
- **API REST** completa (CRUD) em `/api/`.
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

Abre `http://127.0.0.1:8000/`. Antes precisa cadastrar uma obra e uma leitura,
pelo admin (`/admin/`) ou pela API.

O `.env` guarda a `SECRET_KEY` e o `DEBUG`, lidos com `python-decouple`.
Nunca vai pro Git — o modelo está no `.env.example`.

## API

| Método | Rota | O que faz |
|---|---|---|
| `GET` `POST` | `/api/obras/` | lista e cadastra obras |
| `GET` `PUT` `PATCH` `DELETE` | `/api/obras/{id}/` | uma obra |
| `GET` `POST` | `/api/leituras/` | lista e cadastra leituras |
| `GET` `PUT` `PATCH` `DELETE` | `/api/leituras/{id}/` | uma leitura |

Dois `ModelViewSet` registrados num `DefaultRouter`, então a API navegável do
DRF responde no navegador em `/api/`.

`GET /api/leituras/` devolve `obra_titulo` junto, via `source='obra.titulo'`,
pra não precisar de uma segunda chamada só pelo nome da obra.

## Modelo de dados

**Obra** — `tipo` (Fanfic/Manga/Manhwa/Webtoon), `titulo`, `autor`,
`plataforma`, `link` (único), `total_capitulos` (opcional).

**Leitura** — FK pra `Obra`, `capitulo_atual`, `status`
(Lendo/Pausado/Finalizado/Abandonado), `nota` de 1 a 5, `criado_em`,
`atualizado_em`, `encerrado_em`.

Obra e leitura são separadas porque a mesma obra pode ser relida.
`total_capitulos` aceita nulo: fanfic em andamento não tem total.

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

## Próximos passos

- Filtros na API com `django-filter` (status, tipo, plataforma)
- Autenticação — hoje a API é aberta, é projeto de uso local
- Tela de cadastro de obra fora do admin
- Testes automatizados
- Tipos sem link: livro de papel e ebook (hoje `link` é obrigatório e único)
