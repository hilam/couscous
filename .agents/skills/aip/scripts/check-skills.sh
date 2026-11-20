#!/usr/bin/env bash
# check-skills.sh — validador estrutural das skills AIP (.agents/skills/aip*)
# uso: check-skills.sh [diretorio-skills]
# requer: bash, awk, grep, find
set -euo pipefail

TARGET="${1:-.agents/skills}"
ERRORS=0

fail() {
  echo "FAIL: $*" >&2
  ERRORS=$((ERRORS + 1))
}

if [[ ! -d "$TARGET" ]]; then
  echo "erro: diretório não encontrado: $TARGET" >&2
  exit 1
fi

shopt -s nullglob
SKILL_FILES=("$TARGET"/aip*/SKILL.md)
shopt -u nullglob

if [[ ${#SKILL_FILES[@]} -eq 0 ]]; then
  echo "erro: nenhum arquivo aip*/SKILL.md encontrado em $TARGET" >&2
  exit 1
fi

# 1 & 2. Frontmatter YAML íntegro e disable-model-invocation: true nas skills filhas
for f in "${SKILL_FILES[@]}"; do
  dir_name=$(basename "$(dirname "$f")")
  fm_status=$(awk '
    NR == 1 {
      if ($0 != "---") { print "missing_start"; exit }
      in_fm = 1
      next
    }
    in_fm && $0 == "---" { closed = 1; exit }
    in_fm {
      if ($0 ~ /^name:[[:space:]]*[^[:space:]]/) has_name = 1
      if ($0 ~ /^version:[[:space:]]*[^[:space:]]/) has_ver = 1
      if ($0 ~ /^description:[[:space:]]*[^[:space:]]/) {
        has_desc = 1
        val = $0
        sub(/^description:[[:space:]]*/, "", val)
        if (val !~ /^["'\'']/ && val ~ /:([[:space:]]|$)/) bad_desc = 1
      }
      if ($0 ~ /^disable-model-invocation:[[:space:]]*true[[:space:]]*$/) has_dmi = 1
    }
    END {
      if (!closed) { print "missing_end"; exit }
      if (!has_name) print "missing_name"
      if (!has_ver) print "missing_version"
      if (!has_desc) print "missing_description"
      if (bad_desc) print "unquoted_colon_in_description"
      if (!has_dmi) print "missing_dmi"
    }
  ' "$f")

  for issue in $fm_status; do
    if [[ "$issue" == "missing_dmi" ]]; then
      if [[ "$dir_name" != "aip" ]]; then
        fail "$f: falta 'disable-model-invocation: true' no frontmatter"
      fi
    else
      fail "$f: frontmatter inválido ($issue)"
    fi
  done
done

# Coleta todos os arquivos Markdown em aip*
mapfile -t MD_FILES < <(find "$TARGET" -maxdepth 4 -type f -name '*.md' | sort)
if [[ ${#MD_FILES[@]} -eq 0 ]]; then
  echo "erro: nenhum arquivo .md encontrado em $TARGET" >&2
  exit 1
fi

# 3. Caminhos CWD: zero ../aip e zero scripts/state.sh sem prefixo .agents/skills/aip/
for f in "${MD_FILES[@]}"; do
  if grep -En '\.\./aip' "$f" >/dev/null 2>&1; then
    while IFS= read -r line; do
      fail "$f:$line (caminho relativo '../aip' proibido; use '.agents/skills/...')"
    done < <(grep -En '\.\./aip' "$f")
  fi

  while IFS= read -r match; do
    [[ -n "$match" ]] && fail "$f:$match ('scripts/state.sh' sem prefixo '.agents/skills/aip/')"
  done < <(awk '{
    line = $0
    gsub(/\.agents\/skills\/aip\/scripts\/state\.sh/, "", line)
    if (line ~ /scripts\/state\.sh/) printf "%d:%s\n", NR, $0
  }' "$f")
done

# 4. Zero resíduo 'Sprint' em skills/templates
for f in "${MD_FILES[@]}"; do
  if grep -En '\bSprint\b' "$f" >/dev/null 2>&1; then
    while IFS= read -r line; do
      fail "$f:$line (resíduo 'Sprint'; use 'Entrega')"
    done < <(grep -En '\bSprint\b' "$f")
  fi
done

# 5. Zero 'npm test' literal em aip-execute/SKILL.md
if [[ -f "$TARGET/aip-execute/SKILL.md" ]]; then
  if grep -Fn 'npm test' "$TARGET/aip-execute/SKILL.md" >/dev/null 2>&1; then
    while IFS= read -r line; do
      fail "$TARGET/aip-execute/SKILL.md:$line ('npm test' fixo proibido)"
    done < <(grep -Fn 'npm test' "$TARGET/aip-execute/SKILL.md")
  fi
fi

# 6. Nomes canônicos sem prefixo @aip ou /aip de invocação (em .md e state.sh)
PREFIX_TARGETS=("${MD_FILES[@]}")
if [[ -f "$TARGET/aip/scripts/state.sh" ]]; then
  PREFIX_TARGETS+=("$TARGET/aip/scripts/state.sh")
fi
for f in "${PREFIX_TARGETS[@]}"; do
  while IFS= read -r match; do
    [[ -n "$match" ]] && fail "$f:$match (prefixo de invocação '@aip' ou '/aip' proibido; use nome canônico 'aip-*')"
  done < <(awk '{
    orig = $0
    line = $0
    gsub(/https?:\/\/[^[:space:])>"]+/, "", line)
    gsub(/\.agents\/skills\/aip(-[a-z]+)?/, "", line)
    if (line ~ /@aip([-[:alnum:]]*|…)?/ || line ~ /(^|[^[:alnum:]_./-])\/aip([-[:alnum:]]*|…)?/) {
      printf "%d:%s\n", NR, orig
    }
  }' "$f")
done

# 7. Rastreabilidade [S1] e vocabulário limpo nos templates de aip-plan
TPL_DIR="$TARGET/aip-plan/templates"
if [[ -f "$TPL_DIR/spec.md" ]]; then
  if ! grep -Fq '#### Scenario: [S1]' "$TPL_DIR/spec.md"; then
    fail "$TPL_DIR/spec.md: falta '#### Scenario: [S1]' para fonte única por ID"
  fi
fi
if [[ -f "$TPL_DIR/qa-plan.md" ]]; then
  if ! grep -Fq '[S1]' "$TPL_DIR/qa-plan.md"; then
    fail "$TPL_DIR/qa-plan.md: falta referência '[S1]' em **Traces**"
  fi
  if grep -En '\*\*WHEN\*\*|\*\*THEN\*\*' "$TPL_DIR/qa-plan.md" >/dev/null 2>&1; then
    while IFS= read -r line; do
      fail "$TPL_DIR/qa-plan.md:$line (WHEN/THEN duplicado no template qa-plan; mantenha só em spec.md)"
    done < <(grep -En '\*\*WHEN\*\*|\*\*THEN\*\*' "$TPL_DIR/qa-plan.md")
  fi
fi
if [[ -f "$TPL_DIR/tasks.md" ]]; then
  if ! grep -Fq '[S1]' "$TPL_DIR/tasks.md"; then
    fail "$TPL_DIR/tasks.md: falta referência '[S1]' nas tarefas"
  fi
fi
if [[ -f "$TPL_DIR/PLANO-CICLO.md" ]]; then
  if grep -En 'S1 →|\bSemanas\b|por feature' "$TPL_DIR/PLANO-CICLO.md" >/dev/null 2>&1; then
    while IFS= read -r line; do
      fail "$TPL_DIR/PLANO-CICLO.md:$line (resíduo 'S1 →', 'Semanas' ou 'por feature' no template PLANO-CICLO)"
    done < <(grep -En 'S1 →|\bSemanas\b|por feature' "$TPL_DIR/PLANO-CICLO.md")
  fi
fi

if [[ "$ERRORS" -gt 0 ]]; then
  echo "check-skills: $ERRORS falha(s) encontrada(s)" >&2
  exit 1
fi

echo "check-skills: OK (${#SKILL_FILES[@]} skills, ${#MD_FILES[@]} arquivos .md validados)"
