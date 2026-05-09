#!/usr/bin/env bash
# ============================================================================
# apply-labels.sh — Aplica labels do .github/labels.yml ao repo via gh CLI
# ============================================================================
# Uso:
#   ./scripts/apply-labels.sh                    # aplica em Regis-BR/bravo-code-sdd-g
#   REPO=user/repo ./scripts/apply-labels.sh     # aplica em outro repo
#
# Pré-requisitos:
#   - gh CLI instalado e autenticado (`gh auth login`)
#   - yq instalado (`sudo snap install yq` ou brew/apt)
# ============================================================================

set -euo pipefail

REPO="${REPO:-Regis-BR/bravo-code-sdd-g}"
LABELS_FILE="$(dirname "$0")/../.github/labels.yml"

if [[ ! -f "$LABELS_FILE" ]]; then
  echo "❌ Arquivo de labels não encontrado: $LABELS_FILE"
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "❌ gh CLI não instalado. https://cli.github.com/"
  exit 1
fi

if ! command -v yq >/dev/null 2>&1; then
  echo "❌ yq não instalado. https://github.com/mikefarah/yq"
  exit 1
fi

echo "🏷️  Aplicando labels em $REPO..."

# Conta total de labels
TOTAL=$(yq '. | length' "$LABELS_FILE")
echo "   Total de labels no schema: $TOTAL"

# Itera sobre cada label
COUNT=0
for i in $(seq 0 $((TOTAL - 1))); do
  NAME=$(yq ".[$i].name" "$LABELS_FILE")
  COLOR=$(yq ".[$i].color" "$LABELS_FILE")
  DESC=$(yq ".[$i].description" "$LABELS_FILE")

  # Tenta criar; se já existir, atualiza
  if gh label create "$NAME" \
       --color "$COLOR" \
       --description "$DESC" \
       --repo "$REPO" 2>/dev/null; then
    echo "  ✅ Criado: $NAME"
  else
    gh label edit "$NAME" \
       --color "$COLOR" \
       --description "$DESC" \
       --repo "$REPO"
    echo "  🔄 Atualizado: $NAME"
  fi

  COUNT=$((COUNT + 1))
done

echo ""
echo "✅ Concluído: $COUNT labels processadas em $REPO"
echo ""
echo "🔗 Veja em: https://github.com/$REPO/labels"
