# Sessão sempre disponível — `PageContext.session` nunca é None

Data: 2026-07-12

## Status

Aceito.

## Contexto

O `PageContext` transportava `session: AsyncSession | None` — rotas públicas
recebiam `session=None` e views precisavam bifurcar: `login_view` e
`register_view` usavam `ctx.new_session()` enquanto `feed_list_view` e
outras recebiam sessão direta. Uma rota (`oauth_callback_view`) precisava de
sessão mas era pública, o que forçava o flag `requires_session=True` +
`is_public=True` — um oxímoro semântico.

A raiz do problema: o lifecycle do Flet faz a sessão aberta em
`_build_and_invoke` ser fechada antes de event handlers (callbacks) rodarem.
Views precisavam `new_session()` nos callbacks de qualquer forma. A distinção
"rota pública não ganha sessão" só adicionava complexidade — a sessão inicial
era usada só para o load síncrono na função da view, e callbacks sempre
abriam a própria.

## Decisão

- `PageContext.session` é obrigatório — nunca `None`.
- `_Route.requires_session` é removido — toda rota recebe sessão.
- `PageContext.new_session()` vira `PageContext.open_session()` (API
  pública). Continua sendo o caminho para callbacks que rodam após o
  fechamento da sessão inicial.
- `PageContext._session_factory` permanece privado, populado por `app.py` —
  testável via injeção.
- Rotas públicas (login, register, about, oauth/callback) recebem sessão e
  podem ignorá-la no load inicial. O custo de abrir uma sessão é desprezível.

## Consequências

**Positivas:**

- Views nunca mais bifurcam entre `session` e `session=None`.
- `oauth_callback_view` não precisa mais do oxímoro
  `requires_session=True, is_public=True`.
- Uma decisão de lifecycle a menos para cada nova view aprender.
- `_build_and_invoke` vira um único fluxo linear.

**Negativas:**

- Rotas públicas que não tocam no banco (ex: `about_view`) ganham sessão que
  não usam — custo irrelevante, sessões são baratas.
- Testes de view precisam fornecer uma sessão real ou mockada.

## Alternativas consideradas

- **Session-per-callback (sem sessão no PageContext):** cada callback abre a
  própria sessão. Rejeitado porque views precisam de sessão para o load
  inicial também — teria que abrir na view function de qualquer jeito.
- **PageContext gerencia sessão longa:** manter sessão aberta enquanto a view
  estiver ativa. Rejeitado porque Flet não expõe hook de desmonte de view.
