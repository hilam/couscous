## Why

As telas de detalhe (entry_list_view, entry_view) não possuem botão de voltar para a tela anterior. O usuário precisa usar a NavigationBar ou o refresh, sem poder navegar hierarchicalmente de volta.

## What Changes

- `entry_view`: adicionar botão voltar no AppBar (`leading`) que navega para `/feed/<feed_url>`
- `entry_list_view`: adicionar botão voltar no AppBar que navega para `/feeds`
- Ambos preservam a NavigationBar existente

## Capabilities

### New Capabilities
- `back-navigation`: botão de voltar nas telas de detalhe seguindo o fluxo hierárquico

## Impact

- `app/views/entry_list_view.py`: adicionar `leading=ft.IconButton(ft.Icons.ARROW_BACK, ...)` ao AppBar
- `app/views/entry_view.py`: adicionar `leading=ft.IconButton(ft.Icons.ARROW_BACK, ...)` ao AppBar
