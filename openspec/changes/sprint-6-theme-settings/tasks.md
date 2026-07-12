## 1. Git Setup e Planejamento

- [x] 1.1 Criar branch de funcionalidade: `git checkout -b feat/sprint-6-theme-settings`
- [x] 1.2 Commit dos artefatos de planejamento: `git add openspec/changes/sprint-6-theme-settings/ && git commit -m "docs(planning): gera artifacts para sprint-6-theme-settings"`

## 2. Modelo e Migração

- [x] 2.1 Adicionar colunas `theme_mode` (str, nullable, default "light") e `font_scale` (float, nullable, default 1.0) ao modelo `User`
- [x] 2.2 Gerar migration: `make db-migrate-create name="add-theme-and-font-to-users"` e revisar o arquivo gerado
- [x] 2.3 Aplicar migration: `make db-migrate-up`
- [x] 2.4 Commit incremental: `git add -A && git commit -m "feat(models): adiciona theme_mode e font_scale ao User"`

## 3. Testes do settings_service (TDD — test-first)

**Interface acordada:**
- `UserSettings` dataclass com `theme_mode: str = "light"` e `font_scale: float = 1.0`
- `get_settings(session, user_id) -> UserSettings` — lê do banco, fallback p/ defaults do modelo
- `save_settings(session, user_id, theme_mode=None, font_scale=None)` — `None` = não altera
- Sem validação de mode nem clamp de scale (YAGNI — UI já emite valores válidos)

- [x] 3.1 **RED**: criar `tests/test_settings_service.py` com:
      - `test_get_settings_returns_defaults` — usuário sem settings → `UserSettings("light", 1.0)`
      - `test_get_settings_returns_saved_values` — salva e lê de volta
      - `test_save_settings_updates_theme_only` — `save_settings(s, uid, theme_mode="dark")` → só theme muda
      - `test_save_settings_updates_font_only` — `save_settings(s, uid, font_scale=1.3)` → só font muda
      - `test_save_settings_updates_both` — altera os dois de uma vez
      - Executar: `uv run pytest tests/test_settings_service.py -v` — 5/5 falham (RED)
- [x] 3.2 **GREEN**: criar `app/services/settings_service.py` com:
      - `UserSettings` dataclass
      - `get_settings()` — `SELECT + scalars().first()`, retorna `UserSettings()` se None
      - `save_settings()` — `UPDATE` no banco só para kwargs não-None
      - Executar: `uv run pytest tests/test_settings_service.py -v` — 5/5 passam (GREEN)
- [x] 3.3 Commit incremental: `git add -A && git commit -m "feat(services): adiciona settings_service (TDD)"`

## 4. State + App bootstrap — carregar settings no login

- [x] 4.1 Adicionar campos `theme_mode: str = "light"` e `font_scale: float = 1.0` ao `State`
- [x] 4.2 No login/registro: chamar `get_settings()`, popular State, aplicar:
      - `page.theme_mode = getattr(ft.ThemeMode, state.theme_mode.upper())`
      - Mutar `page.theme.text_theme` com font_scale (preservando `color_scheme`)
- [x] 4.3 Commit incremental: `git commit -m "feat(state): carrega theme_mode e font_scale no login"`

## 5. NavBar — substituir "Sobre" por "Config"

- [x] 5.1 Em `app/controls/nav_bar.py`: alterar o 4º destino de `INFO`/`Sobre` para `SETTINGS`/`Config`; ajustar `_ROUTE_INDICES` e `_INDEX_ROUTES`
- [x] 5.2 Commit incremental: `git commit -m "refactor(nav): substitui Sobre por Config na NavBar"`

## 6. Settings View + About popup

- [x] 6.1 Criar `app/views/settings_view.py` com:
      - Dropdown/segmented control de tema (Light / Dark / System) — aplica `page.theme_mode` imediatamente ao trocar
      - Slider de tamanho de texto (0.8–1.5, step 0.1) com preview "Aa" que escala em tempo real **(efeito local, não global)**
      - Botão "Salvar" que: persiste no banco (`save_settings`), atualiza State, aplica font_scale via `page.theme` (mutando, não substituindo)
      - Botão "Salvar" desabilitado quando nenhuma mudança pendente
      - Botão "Sobre" que abre `ft.AlertDialog` com conteúdo do antigo `about_view` (copiado inline)
- [x] 6.2 Atualizar `app/app.py`: importar `settings_view` em vez de `about_view`; rota `/about` aponta para `settings_view`
- [x] 6.3 Remover arquivo `app/views/about_view.py`
- [x] 6.4 Commit incremental: `git commit -m "feat(views): cria settings_view com tema, fonte e about popup"`

## 7. Validação e Qualidade

- [ ] 7.1 Verificar typecheck: `make typecheck` — esperado "Success: no issues found"
- [ ] 7.2 Verificar lint: `make lint` — esperado "All checks passed!"
- [ ] 7.3 Executar testes do settings_service: `uv run pytest tests/test_settings_service.py -v`
- [ ] 7.4 Verificar testes existentes: `make test` — sem regressão
- [ ] 7.5 Executar formatação: `ruff check --fix . && ruff format .`
- [ ] 7.6 Commit final de formatação se houver: `git commit -m "style: aplica ruff e formata arquivos"`
