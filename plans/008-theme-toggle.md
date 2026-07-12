# Plano 008: Adicionar toggle de tema claro/escuro com persistência

> **Instruções ao executor**: Siga este plano passo a passo. Execute todo
> comando de verificação e confirme o resultado esperado antes de passar para
> o próximo passo. Se algo na seção "Condições STOP" ocorrer, pare e reporte
> — não improvise. Quando terminar, atualize a linha de status deste plano
> em `plans/README.md`.
>
> **Verificação de deriva (execute primeiro)**: `git diff --stat c24a31f..HEAD -- app/app.py app/controls/nav_bar.py app/services/ database/models/couscous.py`
> Se qualquer arquivo no escopo mudou desde que este plano foi escrito,
> compare os excertos de "Estado atual" contra o código vivo antes de
> prosseguir; em caso de incompatibilidade, trate como condição STOP.

## Status

- **Prioridade**: P3
- **Esforço**: P
- **Risco**: BAIXO
- **Depende de**: nenhum
- **Categoria**: direction
- **Planejado em**: commit `c24a31f`, 2026-07-12

## Por que isso é importante

O README lista "Temas claro/escuro personalizáveis" como feature. O código fixa `page.theme_mode = ft.ThemeMode.LIGHT` em `app.py:74`. Adicionar um toggle de tema é uma das features de maior impacto visual com menor custo de implementação — Flet suporta nativamente `page.theme_mode` com `ft.ThemeMode.LIGHT`, `ft.ThemeMode.DARK` e `ft.ThemeMode.SYSTEM`.

A abordagem mais simples: um `IconButton` no `NavigationBar` ou na `AppBar` que alterna entre claro e escuro, com persistência via `page.client_storage` (a API built-in do Flet para armazenar preferências do cliente).

## Estado atual

```python
# app/app.py:74
page.theme_mode = ft.ThemeMode.LIGHT
```

O `NavigationBar` em `app/controls/nav_bar.py` tem 4 destinos fixos: Início, Feeds, Categorias, Sobre. O botão de tema pode ser adicionado como um controle extra em cada view ou, mais pragmaticamente, como um `IconButton` flutuante global.

Alternativa mais limpa: adicionar `page.theme_mode = ft.ThemeMode.SYSTEM` como padrão e oferecer toggle via `page.client_storage` — sem UI customizada, usando apenas a API do Flet.

Convenções do repositório:
- `page` é acessível via `ctx.page` em views e `page` em `app_run`.
- `page.client_storage` é um dict-like persistente no cliente (sobrevive a recarregamentos).
- Ícones Flet: `ft.Icons.DARK_MODE`, `ft.Icons.LIGHT_MODE`, `ft.Icons.BRIGHTNESS_AUTO`.
- O `NavigationBar` é configurado em `set_navbar(page)` chamado em `on_route_change`.

## Comandos que você vai precisar

| Propósito | Comando | Esperado em caso de sucesso |
|-----------|---------|------------------------------|
| Typecheck | `make typecheck` | "Success: no issues found" |
| Lint | `make lint` | "All checks passed!" |
| Testes | `make test` | sem novas falhas |

## Escopo

**No escopo**:
- `app/app.py` — adicionar lógica de tema (leitura do client_storage, toggle handler)
- `app/controls/nav_bar.py` — adicionar botão de tema na NavigationBar (ou AppBar global)

**Fora de escopo** (NÃO toque):
- Temas customizados (cores, fontes) — apenas toggle claro/escuro/sistema
- `database/models/couscous.py` — sem nova tabela (usamos client_storage)
- Temas por usuário (multi-user) — client_storage é por cliente, suficiente para single-user

## Fluxo git

- Branch: `advisor/008-theme-toggle`
- Commits: `feat: adiciona toggle de tema claro/escuro/sistema`
- NÃO faça push ou abra PR a menos que o operador o instrua.

## Passos

### Passo 1: Adicionar toggle de tema em `app_run()` — abordagem System default + FloatingActionButton

A abordagem mais simples e eficaz: padrão SYSTEM, FloatingActionButton no canto para toggle.

Modifique `app/app.py` na função `app_run()`:

```python
async def app_run(page: ft.Page):
    page.title = "CousCous - Leitor de RSS"

    # Theme: persist preference in client_storage, default to SYSTEM
    saved_theme = page.client_storage.get("theme_mode")
    if saved_theme:
        page.theme_mode = ft.ThemeMode(saved_theme)
    else:
        page.theme_mode = ft.ThemeMode.SYSTEM

    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.CYAN_400,
            secondary=ft.Colors.BLUE_400,
        ),
    )
    page.padding = 0

    await init_async_db()

    state = State()
    page.session.store.set("state", state)

    # Theme toggle: cycle LIGHT → DARK → SYSTEM
    def toggle_theme(e):
        current = page.theme_mode
        if current == ft.ThemeMode.LIGHT:
            next_theme = ft.ThemeMode.DARK
        elif current == ft.ThemeMode.DARK:
            next_theme = ft.ThemeMode.SYSTEM
        else:
            next_theme = ft.ThemeMode.LIGHT
        page.theme_mode = next_theme
        page.client_storage.set("theme_mode", next_theme.value)
        page.update()

    # Floating theme button
    theme_button = ft.FloatingActionButton(
        icon=ft.Icons.BRIGHTNESS_AUTO,
        on_click=toggle_theme,
        mini=True,
    )
    page.floating_action_button = theme_button

    # ... rest of app_run remains the same
```

Atualize o ícone do botão para refletir o tema atual em `toggle_theme`:

```python
    def toggle_theme(e):
        current = page.theme_mode
        if current == ft.ThemeMode.LIGHT:
            next_theme = ft.ThemeMode.DARK
            e.control.icon = ft.Icons.DARK_MODE
        elif current == ft.ThemeMode.DARK:
            next_theme = ft.ThemeMode.SYSTEM
            e.control.icon = ft.Icons.BRIGHTNESS_AUTO
        else:
            next_theme = ft.ThemeMode.LIGHT
            e.control.icon = ft.Icons.LIGHT_MODE
        page.theme_mode = next_theme
        page.client_storage.set("theme_mode", next_theme.value)
        page.update()
```

E inicialize o ícone corretamente:
```python
    if saved_theme == "light":
        icon = ft.Icons.LIGHT_MODE
    elif saved_theme == "dark":
        icon = ft.Icons.DARK_MODE
    else:
        icon = ft.Icons.BRIGHTNESS_AUTO

    theme_button = ft.FloatingActionButton(
        icon=icon,
        on_click=toggle_theme,
        mini=True,
    )
```

**Verificar**: `make typecheck` → "Success: no issues found". `make lint` → "All checks passed!".

### Passo 2: Verificação final

```bash
make typecheck
# Esperado: "Success: no issues found"

make lint
# Esperado: "All checks passed!"

make test
# Esperado: sem novas falhas (apenas as 12 existentes do plano 002)
```

### Passo 3: Teste manual (instruções para o operador humano)

1. Execute `make run-web`
2. Abra o app no navegador
3. O tema padrão deve ser SYSTEM (respeita a preferência do SO)
4. Clique no FAB (botão flutuante) no canto inferior direito
5. O tema deve alternar: LIGHT → DARK → SYSTEM → LIGHT
6. Recarregue a página — o tema deve persistir (client_storage)
7. O ícone do FAB deve refletir o tema atual: ☀️ para LIGHT, 🌙 para DARK, 🔆 para SYSTEM

## Plano de testes

Nenhum teste automatizado neste plano. A funcionalidade de tema é puramente visual e usa APIs nativas do Flet (`page.theme_mode`, `page.client_storage`). Testar isso exigiria um ambiente Flet completo (headless browser), o que está fora do escopo da suite atual.

Se testes fossem adicionados, poderiam verificar:
- Que `page.client_storage.get("theme_mode")` é chamado durante init
- Que `toggle_theme` alterna entre os três modos
- Que `page.client_storage.set` é chamado a cada toggle

Mas esses testes seriam frágeis (dependem de mock do `page`) e de baixo valor (testam a API do Flet, não nossa lógica).

## Critérios de conclusão

- [ ] `page.theme_mode` inicializa de `page.client_storage` ou default SYSTEM
- [ ] `toggle_theme` alterna entre LIGHT, DARK, SYSTEM
- [ ] `page.floating_action_button` está configurado
- [ ] Preferência de tema persiste via `page.client_storage`
- [ ] Ícone do FAB reflete o tema atual
- [ ] `make typecheck` → "Success: no issues found"
- [ ] `make lint` → "All checks passed!"
- [ ] Nenhum arquivo fora da lista de escopo foi modificado

## Condições STOP

Pare e reporte (não improvise) se:

- `page.floating_action_button` não existe na versão do Flet em uso — verifique `uv run python -c "import flet as ft; print(hasattr(ft.Page, 'floating_action_button'))"`. Se False, use `page.overlay.append(theme_button)` como alternativa.
- `page.client_storage` não está disponível (improvável em Flet 0.85+). Alternativa: usar `page.session.store` (mas isso não persiste entre recarregamentos).
- `ft.ThemeMode.SYSTEM` não existe na versão do Flet. Verifique com `uv run python -c "import flet as ft; print(dir(ft.ThemeMode))"`. Se SYSTEM não existir, use apenas LIGHT/DARK.

## Notas de manutenção

- `page.client_storage` armazena a preferência no navegador (localStorage) em modo web, ou em arquivo local em modo desktop. É transparente — não requer migração de banco.
- Se no futuro o app suportar multi-dispositivo com sync, a preferência de tema pode ser migrada para o banco (`FeedMetadata` com key `theme_mode` por `user_id`). Por enquanto, client_storage é suficiente.
- O FAB é visível em todas as views porque `page.floating_action_button` é global ao `page`. Se alguma view específica precisar de seu próprio FAB, o toggle de tema pode ser movido para dentro do `NavigationBar` como um quinto destino ou um botão na AppBar de cada view.
