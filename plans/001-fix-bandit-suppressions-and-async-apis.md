# Plano 001: Corrigir supressões do bandit e padronizar APIs assíncronas

> **Instruções ao executor**: Siga este plano passo a passo. Execute todo
> comando de verificação e confirme o resultado esperado antes de passar para
> o próximo passo. Se algo na seção "Condições STOP" ocorrer, pare e reporte
> — não improvise. Quando terminar, atualize a linha de status deste plano
> em `plans/README.md`.
>
> **Verificação de deriva (execute primeiro)**: `git diff --stat c24a31f..HEAD -- app/services/search_service.py app/services/oauth_service.py app/views/oauth_callback_view.py app/controls/oauth_buttons.py app/controls/confirm_dialog.py app/controls/add_feed_dialog.py`
> Se qualquer arquivo no escopo mudou desde que este plano foi escrito,
> compare os excertos de "Estado atual" contra o código vivo antes de
> prosseguir; em caso de incompatibilidade, trate como condição STOP.

## Status

- **Prioridade**: P1
- **Esforço**: P
- **Risco**: BAIXO
- **Depende de**: nenhum
- **Categoria**: dx, security
- **Planejado em**: commit `c24a31f`, 2026-07-12

## Por que isso é importante

Três problemas de baixa gravidade mas alta irritação minam a confiança nas verificações do projeto:

1. Os comentários `# noseq B105` e `# noseq B608` estão escritos errado (deveria ser `# nosec`), então o bandit ignora as supressões e `make security` sempre falha com 3 issues. Corrigindo os comentários, `make security` passa limpo.

2. O código usa três APIs inconsistentes: `page.launch_url()` (deprecated pelo Flet) vs `ft.UrlLauncher().launch_url()` (canônica), `page.go()` vs `page.push_route()` (semânticas diferentes de navegação), e `asyncio.ensure_future()` vs `asyncio.create_task()` (API legada vs moderna).

3. Corrigir essas inconsistências reduz surpresas em manutenção futura e alinha o codebase a um único padrão.

## Estado atual

Arquivos relevantes e convenções:

- `app/services/oauth_service.py` — contém `# noseq B105` nos blocos de config de OAuth (linhas 34 e 47). Bandit reporta B105 (false positive para URLs de token).
- `app/services/search_service.py` — contém `# noseq B608` na linha 57. Bandit reporta B608 (false positive — a query usa `:params` parametrizados).
- `app/controls/oauth_buttons.py` — linha 9 usa `await page.launch_url(uri)`, API deprecated.
- `app/views/oauth_callback_view.py` — linha 54 usa `page.go("/login")` em vez de `page.push_route("/login")`.
- `app/controls/confirm_dialog.py` — linha 26 usa `asyncio.ensure_future(self.on_confirm(e))`.
- `app/controls/add_feed_dialog.py` — linha 78 usa `asyncio.ensure_future(self.on_submit(url, category_id))`.

Convenções do repositório:

- O bandit é executado via `make security` (comando: `uv run bandit -r app/ database/`).
- O padrão de navegação no codebase é `page.push_route()` — usado em 11 locais (app.py, entry_view.py, feed_list_view.py, etc.). `page.go()` é a exceção.
- O padrão para tasks assíncronas é `asyncio.create_task()` — usado em explore_view.py, feed_list_view.py, category_list_view.py. `ensure_future()` é a exceção.
- O padrão para abertura de URLs é `ft.UrlLauncher().launch_url()` — usado em entry_view.py:18. `page.launch_url()` é a exceção.

## Comandos que você vai precisar

| Propósito | Comando | Esperado em caso de sucesso |
|-----------|---------|------------------------------|
| Segurança | `make security` | exit 0, zero issues reportados |
| Lint | `make lint` | "All checks passed!" |
| Typecheck | `make typecheck` | "Success: no issues found" |

## Escopo

**No escopo** (os únicos arquivos que você deve modificar):
- `app/services/oauth_service.py`
- `app/services/search_service.py`
- `app/controls/oauth_buttons.py`
- `app/views/oauth_callback_view.py`
- `app/controls/confirm_dialog.py`
- `app/controls/add_feed_dialog.py`

**Fora de escopo** (NÃO toque):
- Qualquer outro arquivo de view, service ou controle
- `tests/` — nenhum teste a alterar aqui
- `pyproject.toml` — configuração do bandit já está correta

## Fluxo git

- Branch: `advisor/001-fix-bandit-and-async-apis`
- Commits no estilo conventional commits: `fix: corrige supressões bandit e padroniza APIs assíncronas`
- NÃO faça push ou abra PR a menos que o operador o instrua.

## Passos

### Passo 1: Corrigir `# noseq` → `# nosec` nos 3 locais

Em `app/services/oauth_service.py`, linha 34:
```python
        }  # noseq B105
```
Trocar por:
```python
        }  # nosec B105
```

Em `app/services/oauth_service.py`, linha 47:
```python
        }  # noseq B105
```
Trocar por:
```python
        }  # nosec B105
```

Em `app/services/search_service.py`, linha 57:
```python
    )  # noseq B608
```
Trocar por:
```python
    )  # nosec B608
```

**Verificar**: `make security` → exit 0, output não contém `>> Issue`.

### Passo 2: Substituir `page.launch_url()` deprecated por `UrlLauncher().launch_url()`

Em `app/controls/oauth_buttons.py`, linha 9:
```python
        await page.launch_url(uri)
```
Trocar por:
```python
        await ft.UrlLauncher().launch_url(uri)
```

**Verificar**: `make typecheck` → "Success: no issues found". `ft.UrlLauncher` é importado via `import flet as ft`.

### Passo 3: Substituir `page.go("/login")` por `page.push_route("/login")`

Em `app/views/oauth_callback_view.py`, linha 54:
```python
                        on_click=lambda _: page.go("/login"),
```
Trocar por:
```python
                        on_click=lambda _: page.push_route("/login"),
```

Nota: `page.push_route` é async, mas aqui está dentro de lambda em `on_click`. O callback `on_click` do Flet aceita callable síncrono para navegação — a task será criada internamente. Este é o mesmo padrão usado em `app/views/home_view.py:31`.

**Verificar**: `make typecheck` → "Success: no issues found". `make lint` → "All checks passed!".

### Passo 4: Substituir `asyncio.ensure_future()` por `asyncio.create_task()`

Em `app/controls/confirm_dialog.py`, linha 26:
```python
            self._task = asyncio.ensure_future(self.on_confirm(e))
```
Trocar por:
```python
            self._task = asyncio.create_task(self.on_confirm(e))
```

Em `app/controls/add_feed_dialog.py`, linha 78:
```python
                self._task = asyncio.ensure_future(self.on_submit(url, category_id))
```
Trocar por:
```python
                self._task = asyncio.create_task(self.on_submit(url, category_id))
```

Verifique que `import asyncio` existe no topo de ambos os arquivos (sim, ambos já importam asyncio).

**Verificar**: `make typecheck` → "Success: no issues found". `make lint` → "All checks passed!".

### Passo 5: Verificação final

Execute todos os comandos de verificação:

```bash
make security
# Esperado: exit 0, zero issues
```

```bash
make lint
# Esperado: "All checks passed!"
```

```bash
make typecheck
# Esperado: "Success: no issues found in 39 source files"
```

## Plano de testes

Nenhum novo teste necessário — estas são mudanças puramente sintáticas/cosméticas:
- `# noseq` → `# nosec`: afeta apenas interpretação do bandit, não runtime
- `launch_url()` deprecated → `UrlLauncher().launch_url()`: mesma API, mesmo comportamento
- `page.go()` → `page.push_route()`: ambas navegam para "/login", `push_route` é mais seguro (preserva histórico)
- `ensure_future()` → `create_task()`: funcionalmente idêntico para corrotinas

## Critérios de conclusão

Verificáveis por máquina. TODOS devem valer:

- [ ] `make security` sai com 0 (nenhuma issue reportada)
- [ ] `make lint` sai com "All checks passed!"
- [ ] `make typecheck` sai com "Success: no issues found"
- [ ] `grep -rn "noseq" app/` não retorna matches
- [ ] `grep -rn "ensure_future" app/` não retorna matches
- [ ] `grep -rn "page\.go(" app/` não retorna matches
- [ ] `grep -rn "page\.launch_url" app/` não retorna matches
- [ ] Nenhum arquivo fora da lista de escopo foi modificado (`git status`)

## Condições STOP

Pare e reporte (não improvise) se:

- O código nas localizações em "Estado atual" não corresponde aos excertos
  (o codebase derivou desde que este plano foi escrito).
- `make typecheck` falha após qualquer passo.
- `make security` ainda reporta B105 ou B608 após o passo 1.
- `grep` encontra mais ocorrências de `noseq`, `ensure_future`, `page.go(`, ou `page.launch_url` do que as listadas — elas podem precisar de tratamento diferente.

## Notas de manutenção

- As supressões do bandit (`# nosec B105`, `# nosec B608`) continuam sendo necessárias porque bandit não consegue distinguir URLs OAuth de hardcoded passwords, nem SQL parametrizado via `text()` com `:params` de SQL injection real. Se o bandit um dia melhorar a detecção, estas supressões podem ser removidas.
- `ensure_future` vs `create_task`: se algum dia for necessário compatibilidade com Python <3.7 (improvável, o projeto requer >=3.13), `create_task()` não estaria disponível. Mas `asyncio.ensure_future` continua existindo — a troca é só por consistência.
