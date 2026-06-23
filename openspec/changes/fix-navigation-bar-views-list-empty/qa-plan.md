## Capability: navbar-timing

### Test: Navegação para /feeds após login — CRITICAL

**Traces**: `specs/navbar-timing/spec.md` → Requirement: Navbar configurada após view ser adicionada ao page.views

- **GIVEN** um usuário cadastrado com credenciais válidas
- **WHEN** o usuário faz login com sucesso
- **THEN** o sistema redireciona para `/feeds` e a `NavigationBar` é exibida com "Feeds" selecionado, sem `RuntimeError`

### Test: Navegação para /feeds após cadastro — CRITICAL

**Traces**: `specs/navbar-timing/spec.md` → Requirement: Navbar configurada após view ser adicionada ao page.views

- **GIVEN** um novo usuário preenchendo o formulário de cadastro
- **WHEN** o usuário se cadastra com nome e senha válidos
- **THEN** o sistema redireciona para `/feeds` e a `NavigationBar` é exibida com "Feeds" selecionado, sem `RuntimeError`

### Test: Navegação pela navbar entre telas

**Traces**: `specs/navbar-timing/spec.md` → Requirement: Navbar configurada após view ser adicionada ao page.views

- **GIVEN** o usuário está autenticado e na tela `/feeds`
- **WHEN** o usuário toca no ícone "Início" na `NavigationBar`
- **THEN** a tela inicial é exibida com "Início" selecionado na navbar

- **GIVEN** o usuário está autenticado e na tela `/feeds`
- **WHEN** o usuário toca no ícone "Categorias" na `NavigationBar`
- **THEN** a tela de categorias é exibida com "Categorias" selecionado na navbar

- **GIVEN** o usuário está autenticado e na tela `/feeds`
- **WHEN** o usuário toca no ícone "Sobre" na `NavigationBar`
- **THEN** a tela "Sobre" é exibida com "Sobre" selecionado na navbar

### Test: Índice correto da navbar por rota

**Traces**: `specs/navbar-timing/spec.md` → Requirement: Navbar configurada após view ser adicionada ao page.views

- **GIVEN** o usuário está autenticado
- **WHEN** o usuário acessa `/` (home)
- **THEN** o índice "Início" (0) está selecionado

- **GIVEN** o usuário está autenticado
- **WHEN** o usuário acessa `/feed/<url>` ou `/entries` ou `/entry/<id>`
- **THEN** o índice "Feeds" (1) está selecionado

- **GIVEN** o usuário está autenticado
- **WHEN** o usuário acessa `/categories`
- **THEN** o índice "Categorias" (2) está selecionado

- **GIVEN** o usuário está autenticado
- **WHEN** o usuário acessa `/about`
- **THEN** o índice "Sobre" (3) está selecionado

### Test: Telas de autenticação sem navbar

**Traces**: `specs/navbar-timing/spec.md` → Requirement: Telas de autenticação não possuem navbar

- **GIVEN** o sistema está iniciando
- **WHEN** o usuário acessa `/login`
- **THEN** a tela de login é exibida sem `NavigationBar` inferior

- **GIVEN** o sistema está iniciando
- **WHEN** o usuário acessa `/register`
- **THEN** a tela de cadastro é exibida sem `NavigationBar` inferior

### Test: EDGE — Navegação rápida entre rotas com navbar

**Traces**: `specs/navbar-timing/spec.md` → (edge case)

- **GIVEN** o usuário está autenticado
- **WHEN** o usuário alterna rapidamente entre `/feeds`, `/categories` e `/about` tocando na navbar
- **THEN** cada tela é exibida com o índice correto selecionado, sem erros

### Test: EDGE — Acesso direto a rota com navbar sem autenticação

**Traces**: `specs/navbar-timing/spec.md` → (edge case)

- **GIVEN** nenhum usuário está autenticado (state.user é None)
- **WHEN** o usuário tenta acessar `/feeds` diretamente
- **THEN** o sistema redireciona para `/login` (tela sem navbar), sem erros

## Review Notes

- **UNTESTABLE**: `specs/navbar-timing/spec.md` → Requirement: Navbar configurada após view ser adicionada ao page.views — O teste automatizado exigiria mockar o ciclo de vida do Flet (`page.views`, `page.navigation_bar`). Recomenda-se teste manual funcional ou teste de integração com `flet` em modo web.
