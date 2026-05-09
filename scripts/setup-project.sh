#!/usr/bin/env bash
# =============================================================================
#  setup-project.sh — Cria/configura Project v2 "AgentSpec Pipeline"
# =============================================================================
#  Cria:
#    - Project v2 no nível do user (ou org)
#    - Custom fields: Phase, Agent, Sprint, Clarity Score, KB Domains
#    - Linka o repositório (auto-add Issues/PRs)
#
#  Uso:
#    bash scripts/setup-project.sh
#
#  Variáveis opcionais:
#    OWNER=Regis-BR             (default — pode ser org)
#    REPO=Regis-BR/bravo-code-sdd-g
#    PROJECT_TITLE="AgentSpec Pipeline"
#    DEBUG=1                    (mostra output bruto das chamadas)
# =============================================================================

set -euo pipefail

OWNER="${OWNER:-Regis-BR}"
REPO="${REPO:-Regis-BR/bravo-code-sdd-g}"
PROJECT_TITLE="${PROJECT_TITLE:-AgentSpec Pipeline}"
DEBUG="${DEBUG:-0}"

log()  { printf "\033[1;34m[%(%H:%M:%S)T]\033[0m %s\n" -1 "$*"; }
ok()   { printf "\033[1;32m✅\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33m⚠️ \033[0m %s\n" "$*"; }
err()  { printf "\033[1;31m❌\033[0m %s\n" "$*" >&2; }
debug(){ [[ "$DEBUG" == "1" ]] && echo "    [debug] $*" >&2 || true; }

# ---------- Pré-requisitos ----------
command -v gh >/dev/null || { err "gh CLI não instalado"; exit 1; }
command -v jq >/dev/null || { err "jq não instalado: sudo apt install jq"; exit 1; }
gh auth status >/dev/null 2>&1 || { err "gh CLI não autenticado"; exit 1; }

# Verifica scopes (project requer 'project' scope)
SCOPES=$(gh auth status 2>&1 | grep -i "token scopes" | sed 's/.*scopes: //' | tr -d "'" || echo "")
if [[ ! "$SCOPES" =~ "project" ]]; then
  warn "Token não tem scope 'project'. Adicionando..."
  gh auth refresh -s project,read:project
  ok "Scope 'project' adicionado"
fi

# ---------- 1. Criar Project (idempotente) ----------
log "Verificando se projeto '$PROJECT_TITLE' já existe..."
EXISTING_NUMBER=$(gh project list --owner "$OWNER" --format json 2>/dev/null | \
  jq -r --arg t "$PROJECT_TITLE" '.projects[] | select(.title==$t) | .number' | head -1 || echo "")

if [[ -n "$EXISTING_NUMBER" ]]; then
  warn "Projeto '$PROJECT_TITLE' já existe (#$EXISTING_NUMBER)"
  PROJECT_NUMBER="$EXISTING_NUMBER"
else
  log "Criando projeto '$PROJECT_TITLE'..."
  PROJECT_NUMBER=$(gh project create --owner "$OWNER" --title "$PROJECT_TITLE" --format json | jq -r '.number')
  ok "Projeto criado: #$PROJECT_NUMBER"
fi

# Pega o ID interno do projeto via GraphQL (necessário para custom fields)
PROJECT_ID=$(gh api graphql -f query="
  query {
    user(login: \"$OWNER\") {
      projectV2(number: $PROJECT_NUMBER) { id }
    }
  }
" --jq '.data.user.projectV2.id' 2>/dev/null || echo "")

# Tenta como org se user não funcionar
if [[ -z "$PROJECT_ID" ]] || [[ "$PROJECT_ID" == "null" ]]; then
  PROJECT_ID=$(gh api graphql -f query="
    query {
      organization(login: \"$OWNER\") {
        projectV2(number: $PROJECT_NUMBER) { id }
      }
    }
  " --jq '.data.organization.projectV2.id' 2>/dev/null || echo "")
fi

if [[ -z "$PROJECT_ID" ]] || [[ "$PROJECT_ID" == "null" ]]; then
  err "Não foi possível obter PROJECT_ID. Verifique se OWNER='$OWNER' está correto."
  exit 1
fi
ok "Project ID resolvido: $PROJECT_ID"

# ---------- 2. Custom fields ----------
# Helper: cria custom field se não existir
create_field() {
  local field_name="$1"
  local data_type="$2"  # SINGLE_SELECT, NUMBER, TEXT, ITERATION, DATE
  local options_json="${3:-null}"  # array de {name, color, description} para SINGLE_SELECT

  # Verifica se field já existe
  EXISTING=$(gh api graphql -f query="
    query {
      node(id: \"$PROJECT_ID\") {
        ... on ProjectV2 {
          fields(first: 50) {
            nodes {
              ... on ProjectV2FieldCommon { id name }
            }
          }
        }
      }
    }
  " --jq ".data.node.fields.nodes[] | select(.name==\"$field_name\") | .id" 2>/dev/null | head -1)

  if [[ -n "$EXISTING" ]]; then
    debug "Field '$field_name' já existe (id=$EXISTING)"
    echo "$EXISTING"
    return
  fi

  log "Criando custom field: $field_name ($data_type)..."
  if [[ "$data_type" == "SINGLE_SELECT" ]]; then
    RESPONSE=$(gh api graphql -f query="
      mutation {
        createProjectV2Field(input: {
          projectId: \"$PROJECT_ID\"
          dataType: SINGLE_SELECT
          name: \"$field_name\"
          singleSelectOptions: $options_json
        }) {
          projectV2Field {
            ... on ProjectV2SingleSelectField { id }
          }
        }
      }
    " 2>&1)
  else
    RESPONSE=$(gh api graphql -f query="
      mutation {
        createProjectV2Field(input: {
          projectId: \"$PROJECT_ID\"
          dataType: $data_type
          name: \"$field_name\"
        }) {
          projectV2Field {
            ... on ProjectV2FieldCommon { id }
          }
        }
      }
    " 2>&1)
  fi

  FIELD_ID=$(echo "$RESPONSE" | jq -r '.data.createProjectV2Field.projectV2Field.id // empty')
  if [[ -n "$FIELD_ID" ]]; then
    ok "Field '$field_name' criado"
    echo "$FIELD_ID"
  else
    warn "Field '$field_name': $RESPONSE"
    echo ""
  fi
}

# Phase (single-select com 5 fases SDD)
PHASE_OPTIONS='[
  {name: "🌱 Brainstorm", color: BLUE, description: "Phase 0 — exploração"},
  {name: "📋 Define", color: PURPLE, description: "Phase 1 — requisitos"},
  {name: "🎨 Design", color: PINK, description: "Phase 2 — arquitetura"},
  {name: "🏗️ Build", color: GREEN, description: "Phase 3 — implementação"},
  {name: "🚀 Shipped", color: GRAY, description: "Phase 4 — entregue"}
]'
create_field "Phase" "SINGLE_SELECT" "$PHASE_OPTIONS" >/dev/null

# Agent (single-select com agentes principais)
AGENT_OPTIONS='[
  {name: "@brainstorm-agent", color: BLUE, description: "Phase 0"},
  {name: "@define-agent", color: PURPLE, description: "Phase 1"},
  {name: "@design-agent", color: PINK, description: "Phase 2"},
  {name: "@build-agent", color: GREEN, description: "Phase 3"},
  {name: "@ship-agent", color: GRAY, description: "Phase 4"},
  {name: "@function-developer", color: ORANGE, description: "Backend"},
  {name: "@infra-deployer", color: YELLOW, description: "Infra/Terraform"},
  {name: "@test-generator", color: RED, description: "QA"}
]'
create_field "Agent" "SINGLE_SELECT" "$AGENT_OPTIONS" >/dev/null

# Clarity Score (number)
create_field "Clarity Score" "NUMBER" >/dev/null

# Estimated Days (number)
create_field "Estimated Days" "NUMBER" >/dev/null

# KB Domains (single-select; multi-select não é nativo em ProjectV2 ainda)
KB_OPTIONS='[
  {name: "gcp", color: BLUE, description: "Google Cloud Platform"},
  {name: "terraform", color: PURPLE, description: "IaC"},
  {name: "terragrunt", color: PURPLE, description: "Multi-env IaC"},
  {name: "gemini", color: PINK, description: "LLM multimodal"},
  {name: "openrouter", color: ORANGE, description: "LLM gateway"},
  {name: "pydantic", color: PINK, description: "Validation"},
  {name: "langfuse", color: YELLOW, description: "LLMOps obs"},
  {name: "crewai", color: GREEN, description: "Multi-agent"},
  {name: "multi", color: GRAY, description: "Múltiplos domínios"}
]'
create_field "KB Domain" "SINGLE_SELECT" "$KB_OPTIONS" >/dev/null

# Sprint (iteration field)
create_field "Sprint" "ITERATION" >/dev/null

ok "Custom fields configurados"

# ---------- 3. Linkar repositório ----------
log "Linkando $REPO ao projeto..."
gh project link "$PROJECT_NUMBER" --owner "$OWNER" --repo "$REPO" 2>&1 | grep -v "already" || warn "Já linkado"
ok "Repositório linkado"

# ---------- 4. Auto-add Issues e PRs (workflow nativo do Project) ----------
log "Habilitando auto-add de Issues e PRs..."
# Auto-add via REST não tem endpoint público; orientação via UI
warn "Auto-add: configure manualmente em Project Settings → Workflows → 'Auto-add to project' (filtra por repo)"

# ---------- Final ----------
echo ""
cat << EOF
═══════════════════════════════════════════════════════════════════════
  ✅ Project v2 configurado: '$PROJECT_TITLE' (#$PROJECT_NUMBER)
═══════════════════════════════════════════════════════════════════════

  🔗 URL: https://github.com/users/$OWNER/projects/$PROJECT_NUMBER

  Custom fields criados:
    - Phase (5 opções: 🌱 Brainstorm, 📋 Define, 🎨 Design, 🏗️ Build, 🚀 Shipped)
    - Agent (8 opções: workflow + specialists)
    - Clarity Score (número)
    - Estimated Days (número)
    - KB Domain (single-select com 9 opções)
    - Sprint (iteration field)

  Próximos passos manuais (UI do Project):
    1. Settings → Workflows → "Auto-add to project" → filtra por $REPO
    2. Crie views: Kanban (group by Phase), Roadmap (by Sprint), Table
    3. Customize colunas visíveis em cada view

  Para popular com Issues existentes:
    gh project item-add $PROJECT_NUMBER --owner $OWNER --url https://github.com/$REPO/issues/<N>
═══════════════════════════════════════════════════════════════════════
EOF
