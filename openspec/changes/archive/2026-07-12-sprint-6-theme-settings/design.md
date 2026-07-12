## Context

Atualmente o CousCous tem tema claro fixo e tamanho de texto padrão do Flet. O `about_view` na rota `/about` mostra info estática sobre o app. A NavBar tem 4 destinos fixos: Início, Feeds, Categorias, Sobre. O modelo `User` não armazena preferências visuais.

## Goals / Non-Goals

**Goals:**
- Usuário pode alternar entre tema claro, escuro ou seguir o sistema
- Usuário pode ajustar o tamanho global do texto (escala 0.8x a 1.5x)
- Preferências são persistidas por usuário no banco e aplicadas ao logar
- Rota `/about` vira Config (settings_view), NavBar reflete isso
- Conteúdo do about_view vira popup dentro de settings

**Non-Goals:**
- Não adicionar temas customizáveis (apenas claro/escuro/sistema)
- Não modificar temas de componentes individuais
- Não adicionar cores personalizáveis
- Não tocar em views não relacionadas (explore, feeds, entries)

## Decisions

| Decisão | Alternativa | Rationale |
|---------|-------------|-----------|
| `theme_mode` como `str` no banco ("light"/"dark"/"system") | Enum no SQLModel | String é mais flexível, compatível com `ft.ThemeMode` via `getattr(ft.ThemeMode, val.upper())`. Migration de enum é mais complexa. |
| `font_scale` como `float` (0.8–1.5, step 0.1) | Inteiro ou discrete enum | Float dá granularidade suficiente. Slider do Flet aceita float nativamente. |
| `settings_view` na rota `/about` | Nova rota `/settings` | Evita quebrar links existentes. Menos mudanças no roteamento. O NavBar mostra "Config" mas a rota interna continua `/about`. |
| Settings **autenticada** (`is_public=False`) | Pública | Settings só faz sentido com usuário logado (persiste preferências por usuário). |
| Persistência via `settings_service.py` | Colocar no `user_service.py` | Separa preocupações. `settings_service` lida só com preferências do usuário. Segue o padrão do código (cada domínio tem seu service). |
| `UserSettings` dataclass com `theme_mode` e `font_scale` | Tupla ou dict | Mais legível que `tuple[str, float]`; self-documenting. |
| `save_settings()` combinada com kwargs opcionais | Funções separadas `save_theme_mode` / `save_font_scale` | Reduz número de queries quando os dois mudam juntos. `None` = não alterar. |
| Sem validação/clamp no service | Validar mode / clampar scale | O slider e o toggle já emitem valores válidos. Validar no service seria código defensivo nunca exercitado (YAGNI). |
| Default de `theme_mode` e `font_scale` no modelo `User` | `None` no banco + fallback no service | Mais seguro: o banco sempre tem um valor válido, mesmo sem migration ter rodado. |
| `State` ganha `theme_mode` e `font_scale` | Ler do banco a cada tela | Manter no State evita query extra por navegação. Sincronizado no login e ao salvar. |
| Aplicar `font_scale` **mutando** `page.theme` (preserva `color_scheme`) | Substituir `page.theme` do zero | Mutar o tema existente mantém `color_scheme` definido em `app_run`. Substituir perderia as cores. |
| Slider de fonte: **preview local**, salvar via botão | Aplicar globalmente a cada slider move | Preview só no texto "Aa" (efeito local). Botão "Salvar" aplica `page.theme` global + persiste + atualiza State. Evita query no banco a cada 0.1 de step. |

## Risks / Trade-offs

| Risco | Mitigação |
|-------|-----------|
| Font scale não se aplica a controles que usam `size=` direto em vez de `TextStyle` | Documentar que controles devem usar `TextStyle` do theme. Para os existentes que usam `size=`, aplicar manualmente o scale no código. |
| ThemeMode.SYSTEM não funciona em todos os ambientes Flet (ex: web desktop vs mobile) | Fallback para LIGHT. Deixar SYSTEM como opção, se não funcionar o usuário pode escolher manualmente. |
| Preview local vs aplicar global — usuário pode esquecer de clicar "Salvar" | Indicador visual (ex: label "não salvo" no slider quando valor difere do State). |
| `page.theme` substituído perde `color_scheme` | Mutar o tema existente em vez de criar novo: `t = page.theme or ft.Theme(); t.text_theme = ...; page.theme = t`. |
| NavBar muda nome mas rota é a mesma — confusão de URL | Aceitável. O NavBar mostra "Config" que é mais descritivo que "Sobre". A URL interna é abstração. |
