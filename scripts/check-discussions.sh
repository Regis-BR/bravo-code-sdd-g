#!/usr/bin/env bash
# =============================================================================
#  check-discussions.sh — Verifica categorias de Discussions
# =============================================================================
#  GitHub não permite criar categorias de Discussions via API. Este script:
#    1. Confirma que Discussions está habilitado
#    2. Lista categorias existentes
#    3. Compara com as 4 categorias canônicas do framework e alerta o que falta
#    4. Imprime instruções precisas para criar manualmente
#
#  Uso: bash scripts/check-discussions.sh
# =============================================================================

set -euo pipefail

REPO="${REPO:-Regis-BR/bravo-code-sdd-g}"
OWNER="${OWNER:-Regis-BR}"
REPO_NAME="${REPO#*/}"

log()  { printf "\033[1;34m[%(%H:%M:%S)T]\033[0m %s\n" -1 "$*"; }
ok()   { printf "\033[1;32m✅\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33m⚠️ \033[0m %s\n" "$*"; }
err()  { printf "\033[1;31m❌\033[0m %s\n" "$*" >&2; }

# Categorias canônicas do framework
declare -A CANONICAL=(
  ["💡 Brainstorm"]="DISCUSSION — exploração inicial de ideias"
  ["❓ Q&A"]="QUESTION/ANSWER — dúvidas com respostas marcáveis"
  ["📢 Announcements"]="ANNOUNCEMENT — apenas mantenedor publica"
  ["🛠️ Show & Tell"]="DISCUSSION — demos e casos de uso"
)

# ---------- Pré-requisitos ----------
command -v gh >/dev/null || { err "gh CLI não instalado"; exit 1; }
gh auth status >/dev/null 2>&1 || { err "gh CLI não autenticado"; exit 1; }

# ---------- 1. Discussions habilitado? ----------
log "Verificando se Discussions está habilitado em $REPO..."
DISCUSSIONS_ENABLED=$(gh api graphql -f query="
  query {
    repository(owner: \"$OWNER\", name: \"$REPO_NAME\") {
      hasDiscussionsEnabled
    }
  }
" --jq '.data.repository.hasDiscussionsEnabled' 2>/dev/null || echo "false")

if [[ "$DISCUSSIONS_ENABLED" != "true" ]]; then
  warn "Discussions não habilitado. Habilitando..."
  gh repo edit "$REPO" --enable-discussions
  ok "Discussions habilitado"
else
  ok "Discussions já habilitado"
fi

# ---------- 2. Listar categorias existentes ----------
log "Listando categorias existentes..."
CATEGORIES_JSON=$(gh api graphql -f query="
  query {
    repository(owner: \"$OWNER\", name: \"$REPO_NAME\") {
      discussionCategories(first: 25) {
        nodes {
          id
          name
          slug
          emoji
          isAnswerable
          description
        }
      }
    }
  }
" 2>/dev/null || echo '{}')

EXISTING_NAMES=$(echo "$CATEGORIES_JSON" | jq -r '.data.repository.discussionCategories.nodes[].name' 2>/dev/null || echo "")

echo ""
echo "Categorias existentes:"
if [[ -z "$EXISTING_NAMES" ]]; then
  echo "  (nenhuma — apenas defaults do GitHub)"
else
  echo "$CATEGORIES_JSON" | jq -r '.data.repository.discussionCategories.nodes[] | "  - \(.emoji // "📁") \(.name)\(if .isAnswerable then " [Q&A]" else "" end)"'
fi
echo ""

# ---------- 3. Comparar com canônicas ----------
log "Comparando com categorias canônicas do framework..."
echo ""
MISSING=()
for cat in "${!CANONICAL[@]}"; do
  if echo "$EXISTING_NAMES" | grep -qF "$cat"; then
    ok "$cat (presente)"
  else
    warn "$cat (FALTANDO) — ${CANONICAL[$cat]}"
    MISSING+=("$cat|${CANONICAL[$cat]}")
  fi
done

# ---------- 4. Instruções de criação manual ----------
if [[ ${#MISSING[@]} -gt 0 ]]; then
  echo ""
  cat << EOF
═══════════════════════════════════════════════════════════════════════
  ⚠️  Categorias faltando: ${#MISSING[@]}
═══════════════════════════════════════════════════════════════════════

  GitHub não permite criar categorias de Discussions via API.
  Crie manualmente em:

    https://github.com/$REPO/discussions/categories/new

  Configurações para cada categoria faltando:

EOF
  for entry in "${MISSING[@]}"; do
    name="${entry%|*}"
    desc="${entry#*|}"
    format="${desc%% *}"
    echo "    • Nome:        $name"
    echo "      Format:      $format"
    echo "      Description: ${desc#$format — }"
    echo "      Emoji:       (já no nome)"
    echo ""
  done

  cat << EOF
  Após criar todas, rode este script novamente para validar.
═══════════════════════════════════════════════════════════════════════
EOF
  exit 1
fi

echo ""
ok "Todas as 4 categorias canônicas estão presentes"
echo ""
echo "🔗 Discussions: https://github.com/$REPO/discussions"
