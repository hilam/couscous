#!/usr/bin/env bash
# state.sh — estado do fluxo AIP em 2 níveis (aip/.state.json). Cópia canônica única. Ver ../REGRAS.md
# uso: state.sh {init <ciclo-slug> | status | advance [--force] <fase> [ciclo-slug|entrega-id] | finish <entrega-id> | set-plano <rascunho|aprovado>}
# requer: jq
set -euo pipefail

STATE="aip/.state.json"
FASES="explore context plan decide execute history"

die() { echo "erro: $*" >&2; exit 1; }
in_list() { [[ " $2 " == *" $1 "* ]]; } # $1 pertence à lista $2 (separada por espaço)

# o processo é círculo em 2 níveis:
# explore(opc) -> context(opc) -> plan(ciclo) -> [plan(Ei) -> decide(Ei) -> execute(Ei) -> history(Ei)]xN -> history(ciclo) -> próximo ciclo
proximas_de() {
  local fase="$1" nivel="$2"
  case "${fase}:${nivel}" in
    explore:*)       echo "context plan" ;;
    context:*)       echo "plan" ;;
    plan:ciclo)      echo "decide" ;;
    decide:ciclo)    echo "plan" ;;
    plan:entrega)    echo "decide" ;;
    decide:entrega)  echo "plan execute" ;;
    execute:*)       echo "history" ;;
    history:entrega) echo "plan" ;;
    history:ciclo)   echo "explore context plan" ;;
    *)               echo "" ;;
  esac
}

skill_de() { case "$1" in
  explore) echo "aip-explore" ;;
  context) echo "aip-context" ;;
  plan)    echo "aip-plan" ;;
  decide)  echo "aip-decide" ;;
  execute) echo "aip-execute" ;;
  history) echo "aip-history" ;;
  *)       echo "?" ;;
esac; }

validar_slug() { [[ "$1" =~ ^[0-9]{2}-[a-z0-9][a-z0-9-]*$ ]] || die "ciclo-slug inválido '$1' — use NN-nome-kebab (ex: 01-fundacao-mvp)"; }

need_state() { [[ -f "$STATE" ]] || die "$STATE não existe — rode 'state.sh init <ciclo-slug>' ou chame aip"; }
fase_atual() { jq -r '.fase' "$STATE"; }
entrega_atual() { jq -r '.entrega_atual // ""' "$STATE"; }
slug_atual() { jq -r '.slug // ""' "$STATE"; }
nivel_atual() { jq -r '.nivel // (if (.entrega_atual // "") == "" then "ciclo" else "entrega" end)' "$STATE"; }

# regrava $STATE atomicamente, no mesmo diretório
write_state() {
  local tmp; tmp=$(mktemp "${STATE}.XXXXXX")
  if jq "$@" "$STATE" >"$tmp"; then mv "$tmp" "$STATE"
  else rm -f "$tmp"; die "falha ao gravar $STATE"; fi
}

init() {
  local slug="${1:-}"
  [[ -n "$slug" ]] || die "uso: state.sh init <ciclo-slug> (NN-nome-kebab)"
  validar_slug "$slug"
  [[ -e "aip/$slug" ]] && die "ciclo já existe em aip/$slug — retome com aip"
  if [[ -f "$STATE" ]] && [[ -n "$(slug_atual)" ]]; then
    die "ciclo $(slug_atual) em andamento — próximo ciclo: 'state.sh advance explore <slug>' (apague $STATE para reiniciar do zero)"
  fi
  mkdir -p "aip/$slug/entregas" "aip/$slug/EXECUCAO"
  echo '{"ciclo":1,"slug":"","fase":"explore","nivel":"ciclo","plano":{"status":"rascunho"},"entrega_atual":"","entregas":{}}' > "$STATE"
  write_state --arg s "$slug" '.slug=$s'
  echo "ciclo=1 slug=$slug fase=explore nivel=ciclo next=aip-explore"
}

status() {
  need_state
  local fase nivel sp lista
  fase=$(fase_atual)
  in_list "$fase" "$FASES" || die "fase '$fase' fora do enum — corrija: state.sh advance --force <fase> (${FASES// /|})"
  nivel=$(nivel_atual)
  sp=$(entrega_atual)
  lista=$(jq -r '.entregas | to_entries | map("\(.key):\(.value)") | join(",")' "$STATE")
  echo "ciclo=$(jq -r '.ciclo' "$STATE") slug=$(slug_atual) fase=$fase nivel=$nivel plano=$(jq -r '.plano.status' "$STATE") entrega=${sp:--} entregas=${lista:--}"
  echo "plano_full=aip/PLANO-FULL.md plano_ciclo=aip/$(slug_atual)/PLANO-CICLO.md"
  echo "next=$(skill_de "$fase")"
}

iniciar_entrega() {
  local id="$1"
  write_state --arg id "$id" '.fase="plan" | .nivel="entrega" | .entrega_atual=$id | .entregas[$id] //= "proposta" | .plano.status="rascunho"'
  echo "fase=plan nivel=entrega entrega=$id next=aip-plan"
}

abrir_proximo_ciclo() {
  local alvo="$1" id="$2"
  [[ -n "$id" ]] || die "para abrir o próximo ciclo: state.sh advance $alvo <NN-nome-kebab>"
  validar_slug "$id"
  [[ -e "aip/$id" ]] && die "ciclo já existe em aip/$id"
  mkdir -p "aip/$id/entregas" "aip/$id/EXECUCAO"
  write_state --arg s "$id" --arg f "$alvo" \
    '.ciclo=(.ciclo+1) | .slug=$s | .fase=$f | .nivel="ciclo" | .plano.status="rascunho" | .entrega_atual="" | .entregas={}'
  echo "ciclo=$(jq -r '.ciclo' "$STATE") slug=$id fase=$alvo nivel=ciclo next=$(skill_de "$alvo")"
}

advance() {
  need_state
  local force="" alvo id atual nivel permitidas
  if [[ "${1:-}" == "--force" ]]; then force=1; shift; fi
  alvo="${1:-}"; id="${2:-}"
  atual=$(fase_atual)
  nivel=$(nivel_atual)
  [[ -n "$alvo" ]] || die "uso: state.sh advance [--force] <fase> [id] — fases: ${FASES// /|}"
  in_list "$alvo" "$FASES" || die "fase inválida '$alvo' — use: ${FASES// /|}"
  permitidas=$(proximas_de "$atual" "$nivel")

  # auto-transições sem mudança de nome de fase
  if [[ "$alvo" == "$atual" && -z "$force" ]]; then
    if [[ "$atual" == "execute" ]]; then
      [[ -n "$id" ]] || die "uso: state.sh advance execute <entrega-id> — registro de entrega exige id"
      write_state --arg id "$id" '.nivel="entrega" | .entrega_atual=$id | .entregas[$id] //= "proposta"'
      echo "fase=execute nivel=entrega entrega=$id registrada next=aip-execute"
      return
    fi
    if [[ "$atual" == "plan" && "$nivel" == "ciclo" ]]; then
      [[ -n "$id" ]] || die "uso: state.sh advance plan <entrega-id> — transição plan(ciclo) → plan(entrega) exige entrega-id"
      iniciar_entrega "$id"
      return
    fi
    if [[ "$atual" == "history" && "$nivel" == "entrega" ]]; then
      write_state '.nivel="ciclo" | .entrega_atual=""'
      echo "fase=history nivel=ciclo next=aip-history"
      return
    fi
    die "transição ilegal $atual($nivel) → $alvo (use --force para correção manual)"
  fi

  if [[ -z "$force" ]] && ! in_list "$alvo" "$permitidas"; then
    die "transição ilegal $atual($nivel) → $alvo (permitido: ${permitidas// /|}) — correção manual: state.sh advance --force $alvo"
  fi

  # fechar ciclo em history(ciclo) e abrir o próximo em explore|context|plan
  if [[ "$atual" == "history" && "$nivel" == "ciclo" && -z "$force" ]]; then
    abrir_proximo_ciclo "$alvo" "$id"
    return
  fi

  # history(entrega) -> plan(Ei+1) exige <entrega-id>
  if [[ "$atual" == "history" && "$nivel" == "entrega" && "$alvo" == "plan" && -z "$force" ]]; then
    [[ -n "$id" ]] || die "uso: state.sh advance plan <entrega-id> — próxima entrega exige entrega-id"
    iniciar_entrega "$id"
    return
  fi

  # decide(ciclo) -> plan(<E1-id> ou ciclo)
  if [[ "$atual" == "decide" && "$nivel" == "ciclo" && "$alvo" == "plan" && -z "$force" ]]; then
    if [[ -n "$id" ]]; then
      iniciar_entrega "$id"
    else
      write_state '.fase="plan" | .nivel="ciclo"'
      echo "fase=plan nivel=ciclo next=aip-plan"
    fi
    return
  fi

  # demais transições normais ou --force
  if [[ -n "$id" ]]; then
    write_state --arg f "$alvo" --arg id "$id" '.fase=$f | .nivel="entrega" | .entrega_atual=$id | .entregas[$id] //= "proposta"'
  else
    local novo_nivel="$nivel"
    if [[ "$alvo" == "explore" || "$alvo" == "context" ]]; then
      novo_nivel="ciclo"
    fi
    write_state --arg f "$alvo" --arg n "$novo_nivel" '.fase=$f | .nivel=$n'
  fi
  echo "fase=$alvo nivel=$(nivel_atual)${id:+ entrega=$id} next=$(skill_de "$alvo")"
}

finish() {
  need_state
  local id="${1:-}"
  [[ -n "$id" ]] || die "uso: state.sh finish <entrega-id>"
  if [[ $(jq -r --arg id "$id" '.entregas[$id] // ""' "$STATE") == "" ]]; then
    die "entrega '$id' não registrada — registre com: state.sh advance execute $id"
  fi
  write_state --arg id "$id" '.entregas[$id]="concluida"'
  local restantes nao_registradas dir_entregas
  restantes=$(jq -r '[.entregas | to_entries[] | select(.value!="concluida") | .key] | join(",")' "$STATE")
  nao_registradas=""
  dir_entregas="aip/$(slug_atual)/entregas"
  if [[ -d "$dir_entregas" ]]; then
    local d nome
    for d in "$dir_entregas"/*/; do
      [[ -d "$d" ]] || continue
      nome=$(basename "$d")
      if [[ $(jq -r --arg id "$nome" '.entregas[$id] // ""' "$STATE") == "" ]]; then
        nao_registradas+="${nao_registradas:+,}$nome"
      fi
    done
  fi
  if [[ -n "$nao_registradas" ]]; then
    echo "entrega=$id concluida — ATENÇÃO: entregas não registradas no estado: $nao_registradas (registre com: state.sh advance execute <id>)"
  elif [[ -z "$restantes" ]]; then
    echo "entrega=$id concluida — avance para history da entrega: state.sh advance history"
  else
    echo "entrega=$id concluida — faltam no estado: $restantes; feche a entrega com: state.sh advance history"
  fi
}

set_plano() {
  need_state
  local st="${1:-}" atual
  case "$st" in rascunho|aprovado) ;; *) die "plano.status inválido '$st' — use rascunho|aprovado" ;; esac
  atual=$(fase_atual)
  case "$atual" in plan|decide) ;; *) die "plano.status não muda em fase=$atual (só em plan|decide)" ;; esac
  if [[ "$st" == "aprovado" && "$atual" != "decide" ]]; then
    die "não marque aprovado em fase=$atual — só após aip-decide e gate humano"
  fi
  write_state --arg s "$st" '.plano.status=$s'
  echo "plano.status=$st"
}

command -v jq >/dev/null 2>&1 || die "jq não encontrado — instale (apt install jq / brew install jq)"

case "${1:-}" in
  init)      shift; init "$@" ;;
  status)    status ;;
  advance)   shift; advance "$@" ;;
  finish)    shift; finish "$@" ;;
  set-plano) shift; set_plano "$@" ;;
  *) { echo "uso: state.sh {init <ciclo-slug>|status|advance [--force] <fase> [id]|finish <entrega-id>|set-plano <rascunho|aprovado>}"
       echo "fases: ${FASES// /|}"; } >&2; exit 1 ;;
esac
