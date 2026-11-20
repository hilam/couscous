<!-- Um bloco "## Capability" por capability afetada; um "### Test:" por cenário [S1] (sem repetir WHEN/THEN do spec.md).
     "Casos Limite", "Pontos de Integração" e "Notas de Revisão" uma única vez, no final. -->

> **Entrega:** `entregas/<id>/` — rastreia `entregas/<id>/specs/<capability>/spec.md`

## Capability: <!-- nome (igual à pasta do spec) -->

### Test: <!-- nome do teste -->
**Traces**: `entregas/<id>/specs/<capability>/spec.md` → [S1] (Requirement: <!-- nome -->)
- **CRITICAL**
- **GIVEN** <!-- pré-condição / fixture -->
- **Seam / Oráculo:** <!-- fronteira pública acionada + resultado literal esperado -->

### Test: EDGE - <!-- caso limite -->
**Traces**: `entregas/<id>/specs/<capability>/spec.md` → (edge case)
- **EDGE**
- **GIVEN** <!-- pré-condição / entrada incomum -->
- **Seam / Oráculo:** <!-- fronteira pública acionada + resultado literal esperado -->

## Casos Limite

<!-- contorno, estados de erro, entradas incomuns não cobertas pelos specs -->

## Pontos de Integração

<!-- interações entre capacidades que precisam de validação -->

## Notas de Revisão

<!-- ambiguidade/não-testabilidade — resolver no decide antes das tasks -->
<!-- - **AMBÍGUO**: `specs/<cap>/spec.md` → [S1] - <descrição> -->
<!-- - **NÃO TESTÁVEL**: `specs/<cap>/spec.md` → Requirement: <nome> - <motivo> -->
