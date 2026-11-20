#!/usr/bin/env bash
# test-state.sh — suíte isolada em /tmp para .agents/skills/aip/scripts/state.sh
# uso: test-state.sh
# requer: bash, jq
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
STATE_SH="$SCRIPT_DIR/state.sh"
REPO_ROOT=$(pwd)
REPO_STATE="$REPO_ROOT/aip/.state.json"

[[ -x "$STATE_SH" ]] || { echo "erro: state.sh não encontrado/executável em $STATE_SH" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "erro: jq não encontrado" >&2; exit 1; }

HASH_BEFORE=""
if [[ -f "$REPO_STATE" ]]; then
  HASH_BEFORE=$(sha256sum "$REPO_STATE" | awk '{print $1}')
fi

WORK_DIR=$(mktemp -d)
trap 'rm -rf "$WORK_DIR"' EXIT

PASS=0
FAIL=0

assert_eq() {
  local got="$1" expected="$2" msg="$3"
  if [[ "$got" != "$expected" ]]; then
    echo "FAIL: $msg (esperado='$expected', obtido='$got')" >&2
    exit 1
  fi
}

assert_contains() {
  local haystack="$1" needle="$2" msg="$3"
  if [[ "$haystack" != *"$needle"* ]]; then
    echo "FAIL: $msg (esperado conter '$needle' em '$haystack')" >&2
    exit 1
  fi
}

assert_not_contains() {
  local haystack="$1" needle="$2" msg="$3"
  if [[ "$haystack" == *"$needle"* ]]; then
    echo "FAIL: $msg (não deveria conter '$needle' em '$haystack')" >&2
    exit 1
  fi
}

run_case() {
  local name="$1" fn="$2"
  local dir="$WORK_DIR/$name"
  local rc=0
  mkdir -p "$dir/aip"
  set +e
  (set -euo pipefail; cd "$dir" && "$fn")
  rc=$?
  set -e
  if [[ $rc -eq 0 ]]; then
    echo "PASS: $name"
    PASS=$((PASS + 1))
  else
    echo "FAIL: $name" >&2
    FAIL=$((FAIL + 1))
  fi
}

case_init_and_legacy_status() {
  local out
  out=$(bash "$STATE_SH" init 01-teste)
  assert_contains "$out" "nivel=ciclo" "init output deve conter nivel=ciclo"
  assert_contains "$out" "next=aip-explore" "init output deve usar nome canônico aip-explore"
  assert_not_contains "$out" "@aip" "init output não deve conter prefixo @"
  assert_eq "$(jq -r '.nivel' aip/.state.json)" "ciclo" "json deve gravar nivel=ciclo"

  out=$(bash "$STATE_SH" status)
  assert_contains "$out" "nivel=ciclo" "status deve exibir nivel=ciclo"
  assert_contains "$out" "next=aip-explore" "status deve exibir next=aip-explore"

  # Legacy state sem campo nivel (entrega_atual vazio -> ciclo)
  cat > aip/.state.json <<'EOF'
{"ciclo":1,"slug":"01-teste","fase":"plan","plano":{"status":"rascunho"},"entrega_atual":"","entregas":{}}
EOF
  out=$(bash "$STATE_SH" status)
  assert_contains "$out" "nivel=ciclo" "legacy sem entrega_atual deve inferir nivel=ciclo"

  # Legacy state sem campo nivel (entrega_atual preenchido -> entrega)
  cat > aip/.state.json <<'EOF'
{"ciclo":1,"slug":"01-teste","fase":"execute","plano":{"status":"aprovado"},"entrega_atual":"01-e1","entregas":{"01-e1":"proposta"}}
EOF
  out=$(bash "$STATE_SH" status)
  assert_contains "$out" "nivel=entrega" "legacy com entrega_atual deve inferir nivel=entrega"
}

case_optional_explore_and_context() {
  local out
  bash "$STATE_SH" init 01-skip >/dev/null
  # Pula context: explore(ciclo) -> plan(ciclo)
  out=$(bash "$STATE_SH" advance plan)
  assert_contains "$out" "fase=plan" "explore deve avançar direto para plan"
  assert_contains "$out" "nivel=ciclo" "plan após explore deve manter nivel=ciclo"
  assert_contains "$out" "next=aip-plan" "next deve ser aip-plan"

  # Simula ciclo fechado em history(ciclo) e abre proximo direto em plan
  bash "$STATE_SH" advance --force history >/dev/null
  jq '.nivel="ciclo" | .entrega_atual=""' aip/.state.json > aip/.state.json.tmp
  mv aip/.state.json.tmp aip/.state.json

  out=$(bash "$STATE_SH" advance plan 02-direto-plan)
  assert_contains "$out" "ciclo=2" "deve incrementar ciclo para 2"
  assert_contains "$out" "fase=plan" "deve abrir ciclo 2 direto em plan"
  assert_contains "$out" "nivel=ciclo" "novo ciclo em plan deve começar em nivel=ciclo"
  [[ -d "aip/02-direto-plan/entregas" ]] || { echo "diretório entregas do ciclo 2 não criado" >&2; return 1; }
  [[ -d "aip/02-direto-plan/EXECUCAO" ]] || { echo "diretório EXECUCAO do ciclo 2 não criado" >&2; return 1; }

  # Também permite abrir ciclo seguinte direto em context
  bash "$STATE_SH" advance --force history >/dev/null
  jq '.nivel="ciclo" | .entrega_atual=""' aip/.state.json > aip/.state.json.tmp
  mv aip/.state.json.tmp aip/.state.json
  out=$(bash "$STATE_SH" advance context 03-direto-context)
  assert_contains "$out" "ciclo=3" "deve incrementar ciclo para 3"
  assert_contains "$out" "fase=context" "deve abrir ciclo 3 direto em context"
}

case_two_delivery_jit_lifecycle() {
  local out
  bash "$STATE_SH" init 01-ciclo >/dev/null
  bash "$STATE_SH" advance context >/dev/null
  bash "$STATE_SH" advance plan >/dev/null

  # decide(ciclo) opcional -> retorna com advance plan <E1-id>
  out=$(bash "$STATE_SH" advance decide)
  assert_contains "$out" "nivel=ciclo" "decide no nível ciclo deve manter nivel=ciclo"
  out=$(bash "$STATE_SH" advance plan 01-a)
  assert_contains "$out" "fase=plan" "deve entrar em plan(E1)"
  assert_contains "$out" "nivel=entrega" "deve mudar nivel para entrega"
  assert_contains "$out" "entrega=01-a" "deve definir entrega=01-a"

  bash "$STATE_SH" set-plano rascunho >/dev/null
  bash "$STATE_SH" advance decide >/dev/null
  bash "$STATE_SH" set-plano aprovado >/dev/null
  bash "$STATE_SH" advance execute >/dev/null
  bash "$STATE_SH" advance execute 01-a >/dev/null
  out=$(bash "$STATE_SH" finish 01-a)
  assert_contains "$out" "entrega=01-a concluida" "finish 01-a deve concluir entrega"

  # execute(E1) -> history(E1)
  out=$(bash "$STATE_SH" advance history)
  assert_contains "$out" "fase=history" "deve ir para history"
  assert_contains "$out" "nivel=entrega" "history após entrega deve ter nivel=entrega"
  assert_contains "$out" "next=aip-history" "next deve ser aip-history"

  # history(E1) -> plan(E2)
  out=$(bash "$STATE_SH" advance plan 02-b)
  assert_contains "$out" "fase=plan" "deve ir para plan(E2)"
  assert_contains "$out" "nivel=entrega" "deve permanecer em nivel=entrega"
  assert_contains "$out" "entrega=02-b" "entrega_atual deve ser 02-b"
  assert_eq "$(jq -r '.plano.status' aip/.state.json)" "rascunho" "nova entrega deve resetar plano.status para rascunho"

  bash "$STATE_SH" advance decide >/dev/null
  bash "$STATE_SH" set-plano aprovado >/dev/null
  bash "$STATE_SH" advance execute >/dev/null
  bash "$STATE_SH" advance execute 02-b >/dev/null
  bash "$STATE_SH" finish 02-b >/dev/null

  # execute(E2) -> history(E2) -> history(Ciclo) -> explore(proximo)
  out=$(bash "$STATE_SH" advance history)
  assert_contains "$out" "nivel=entrega" "history após E2 deve ser nivel=entrega"
  out=$(bash "$STATE_SH" advance history)
  assert_contains "$out" "fase=history" "promoção deve manter fase=history"
  assert_contains "$out" "nivel=ciclo" "promoção deve mudar nivel para ciclo"
  assert_eq "$(jq -r '.entrega_atual' aip/.state.json)" "" "history(ciclo) deve limpar entrega_atual"

  out=$(bash "$STATE_SH" advance explore 02-proximo)
  assert_contains "$out" "ciclo=2" "deve abrir ciclo 2"
  assert_contains "$out" "slug=02-proximo" "slug do ciclo 2 deve ser 02-proximo"
  assert_eq "$(jq -r '.entregas | length' aip/.state.json)" "0" "entregas deve reiniciar vazio no ciclo 2"
}

case_illegal_transitions_and_guards() {
  bash "$STATE_SH" init 01-guard >/dev/null
  bash "$STATE_SH" advance plan >/dev/null
  bash "$STATE_SH" advance decide >/dev/null

  local before after
  before=$(cat aip/.state.json)
  # decide(ciclo) -> execute deve falhar
  if bash "$STATE_SH" advance execute 2>/dev/null; then
    echo "decide(ciclo) -> execute deveria falhar" >&2
    return 1
  fi
  after=$(cat aip/.state.json)
  assert_eq "$after" "$before" "state.json não pode mudar em transição ilegal decide(ciclo)->execute"

  # entra em entrega 01-a e chega em history(entrega)
  bash "$STATE_SH" advance plan 01-a >/dev/null
  bash "$STATE_SH" advance decide >/dev/null
  bash "$STATE_SH" advance execute >/dev/null
  # finish não registrado deve falhar
  if bash "$STATE_SH" finish nao-existe 2>/dev/null; then
    echo "finish de entrega não registrada deveria falhar" >&2
    return 1
  fi
  bash "$STATE_SH" advance execute 01-a >/dev/null
  bash "$STATE_SH" finish 01-a >/dev/null
  bash "$STATE_SH" advance history >/dev/null

  before=$(cat aip/.state.json)
  # history(entrega) -> advance plan sem <id> deve falhar
  if bash "$STATE_SH" advance plan 2>/dev/null; then
    echo "history(entrega) -> advance plan sem id deveria falhar" >&2
    return 1
  fi
  after=$(cat aip/.state.json)
  assert_eq "$after" "$before" "state.json não pode mudar quando falta <id> em plan"

  # promove para history(ciclo) e tenta advance history novamente -> deve falhar
  bash "$STATE_SH" advance history >/dev/null
  before=$(cat aip/.state.json)
  if bash "$STATE_SH" advance history 2>/dev/null; then
    echo "history(ciclo) -> advance history deveria falhar" >&2
    return 1
  fi
  after=$(cat aip/.state.json)
  assert_eq "$after" "$before" "state.json não pode mudar em history(ciclo) -> history"
}

case_force_and_edge() {
  local out
  bash "$STATE_SH" init 01-edge >/dev/null
  bash "$STATE_SH" advance plan >/dev/null
  bash "$STATE_SH" advance plan 01-a >/dev/null
  bash "$STATE_SH" advance decide >/dev/null
  bash "$STATE_SH" advance execute >/dev/null
  bash "$STATE_SH" advance execute 01-a >/dev/null
  bash "$STATE_SH" finish 01-a >/dev/null
  bash "$STATE_SH" advance history >/dev/null

  # --force permite retorno explícito
  out=$(bash "$STATE_SH" advance --force plan)
  assert_contains "$out" "fase=plan" "--force plan deve permitir retorno"
}

run_case "init_and_legacy_status" case_init_and_legacy_status
run_case "optional_explore_and_context" case_optional_explore_and_context
run_case "two_delivery_jit_lifecycle" case_two_delivery_jit_lifecycle
run_case "illegal_transitions_and_guards" case_illegal_transitions_and_guards
run_case "force_and_edge" case_force_and_edge

if [[ -n "$HASH_BEFORE" ]]; then
  HASH_AFTER=$(sha256sum "$REPO_STATE" | awk '{print $1}')
  if [[ "$HASH_BEFORE" != "$HASH_AFTER" ]]; then
    echo "FAIL: aip/.state.json do repositório foi modificado durante test-state.sh!" >&2
    exit 1
  fi
fi

if [[ "$FAIL" -gt 0 ]]; then
  echo "test-state: $FAIL falha(s), $PASS sucesso(s)" >&2
  exit 1
fi

echo "test-state: OK ($PASS casos passaram em isolamento /tmp)"
