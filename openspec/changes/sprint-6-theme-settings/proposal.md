## Why

O CousCous não oferece personalização visual — sempre tema claro, fonte fixa. Usuários que preferem tema escuro ou precisam de texto maior não têm como ajustar. Adicionar temas claro/escuro/sistema e controle de tamanho de texto melhora a experiência sem depender de bibliotecas externas (Flet já suporta nativamente).

## What Changes

- Adicionar colunas `theme_mode` (str: "light"/"dark"/"system") e `font_scale` (float: 0.8–1.5) ao modelo `User`
- Substituir `about_view` por `settings_view` — a rota `/about` vira Config, com toggle de tema e slider de fonte
- Conteúdo do `about_view` vira popup ("Sobre") dentro das Config
- NavBar muda de [Início, Feeds, Categorias, Sobre] para [Início, Feeds, Categorias, Config]
- `page.theme_mode` é aplicado dinamicamente ao trocar tema
- `font_scale` é aplicado via `page.theme` (escala de `TextStyle.size`)
- Preferências são persistidas no banco e aplicadas ao iniciar sessão

## Capabilities

### New Capabilities

- `theme-settings`: Usuário pode alternar entre tema claro, escuro ou seguir o sistema, e ajustar o tamanho global do texto. Preferências são persistidas por usuário.

### Modified Capabilities

- `app-navigation`: NavBar destino "Sobre" (ícone `INFO`, rota `/about`) é substituído por "Config" (ícone `SETTINGS`, rota `/about`). O conteúdo do about_view vira um popup acessível pela settings_view.

## Impact

- `database/models/couscous.py` — modelo `User` ganha campos `theme_mode` e `font_scale`
- **NOVO** `app/views/settings_view.py` — substitui `about_view` com toggle de tema, slider de fonte, botão "Sobre"
- `app/views/about_view.py` — removido (conteúdo vira popup)
- `app/controls/nav_bar.py` — destino "Sobre" → "Config"
- `app/app.py` — rota `/about` continua existindo mas aponta para `settings_view`
- `app/state.py` — ganha campos `theme_mode` e `font_scale` para estado em memória
- **NOVO** `app/services/settings_service.py` — funções `get_settings`, `save_theme_mode`, `save_font_scale`
- Migration: nova migration adiciona colunas `theme_mode` e `font_scale` à tabela `users`
- Nenhuma dependência externa nova (Flet já tem `ThemeMode`, `Theme`, `TextStyle` nativamente)
