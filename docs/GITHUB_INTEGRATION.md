# GitHub Integration

> Como Issues, Pull Requests, Projects v2 e GitHub Actions se conectam neste fork para materializar o pipeline SDD de 5 fases. Esta documentação reflete o estado **pós-Onda 2**.

---

## Princípio fundamental

O GitHub deixou de ser hospedagem e passou a ser **plano de controle do framework**. Toda fase SDD tem uma manifestação nativa em uma entidade GitHub:

| Fase SDD | Entidade GitHub | Mecanismo |
|----------|-----------------|-----------|
| 0 — Brainstorm | Issue (`brainstorm.yml`) ou Discussion | Issue Form / Discussion |
| 1 — Define | Issue (`define.yml`) | Issue Form com clarity score nativo |
| 2 — Design | Comment + commit | Agent posta resumo + commita DESIGN.md |
| 3 — Build | Pull Request | Branch + PR template com checklist |
| 4 — Ship | PR mergeado | Auto-label `phase:shipped` via Action |
| Iterate | Issue (`iterate.yml`) | Cascata via Action (Onda 4) |

---

## Fluxo end-to-end

```text
                    ╔═══════════════════════════════════════╗
                    ║   GITHUB AS CONTROL PLANE             ║
                    ╚═══════════════════════════════════════╝

  USUÁRIO                                              GITHUB AUTOMATION
  ───────                                              ─────────────────

  /brainstorm "ideia"
         │
         ▼
  Cria Issue tipo brainstorm.yml ──────────────▶ Label phase:brainstorm
                                                  ↓
                                                  Aparece no Project v2
                                                  (Phase column = Brainstorm)

  /define <feature>
         │
         ▼
  Cria Issue tipo define.yml ──────────────────▶ Issue Form valida campos
  (com 5 campos obrigatórios)                     obrigatórios = clarity≥12
                                                  ↓
                                                  Label phase:define
                                                  ↓
                                                  Project Phase = Define

  /design <feature>
         │
         ▼
  Agent comita DESIGN.md  ─────────────────────▶ Commit em branch
  e comenta na Issue                              feature/design-X
                                                  ↓
                                                  Comment na Issue
                                                  com agent matching

  /build <feature>
         │
         ▼
  Code generation  ────────────────────────────▶ Branch feature/build-X
  /create-pr                                       ↓
                                                  PR aberto com Closes #N
                                                  ↓
                              ╔════════════════════════════════════════╗
                              ║ Action: phase-sync-pr.yml              ║
                              ║   • Adiciona phase:build no PR         ║
                              ║   • Propaga phase:build na Issue       ║
                              ║   • Project Phase = Build              ║
                              ╠════════════════════════════════════════╣
                              ║ Action: pr-template-check.yml          ║
                              ║   • Valida Closes #N presente          ║
                              ║   • Valida tipo de mudança marcado     ║
                              ║   • Valida artefatos SDD linkados      ║
                              ║   • Posta comment no PR                ║
                              ╚════════════════════════════════════════╝
                                                  ↓
                                              CODEOWNERS define revisores
                                                  ↓
                                              Code review humano
                                                  ↓
                                              Merge (squash)
                                                  ↓
                              ╔════════════════════════════════════════╗
                              ║ Action: auto-ship-label.yml            ║
                              ║   • Issue → phase:shipped              ║
                              ║   • PR → phase:shipped                 ║
                              ║   • Project Phase = Shipped            ║
                              ║   • Issue fechada via "Closes #N"      ║
                              ╚════════════════════════════════════════╝

  /ship <feature>
         │
         ▼
  Agent move artefatos ────────────────────────▶ Commit em main
  para archive/                                   archive/SHIPPED_DATE.md

```

---

## Componentes desta integração

### 1. Issue Forms (Onda 1)

5 templates em `.github/ISSUE_TEMPLATE/*.yml`:

| Form | Trigger | Labels aplicadas |
|------|---------|------------------|
| `brainstorm.yml` | Phase 0 | `phase:brainstorm`, `needs-triage` |
| `define.yml` | Phase 1 (clarity ≥12) | `phase:define`, `needs-triage` |
| `iterate.yml` | Cross-phase | `iterate`, `needs-triage` |
| `bug-report.yml` | Bug do framework | `bug`, `needs-triage` |
| `kb-update.yml` | Update no Knowledge Base | `kb-update`, `needs-triage` |

**Validação nativa**: cada form tem campos `validations: required: true`. GitHub bloqueia criação se faltarem.

### 2. PR Template (Onda 1) + Checklist Action (Onda 2)

`.github/PULL_REQUEST_TEMPLATE.md` define a estrutura. `.github/workflows/pr-template-check.yml` valida:

- ✅ `Closes #N` presente (exceto para `chore`/`docs`/`refactor`)
- ✅ Pelo menos um tipo de mudança marcado
- ✅ Artefatos SDD linkados (DEFINE, DESIGN) se PR é `phase:build`
- ✅ Sem secrets óbvios (heurística com regex)

Resultado posta como comment automático no PR. **Status check** falha se houver issues — pronto para usar como `required_status_checks` em Branch Protection (Onda 3).

### 3. CODEOWNERS (Onda 2)

`.github/CODEOWNERS` mapeia paths para responsáveis:

| Path | Owner |
|------|-------|
| `*` (default) | `@Regis-BR` |
| `.claude/agents/`, `.claude/commands/`, `.claude/sdd/` | `@Regis-BR` |
| `.claude/kb/_index.yaml` | `@Regis-BR` (crítico) |
| `.claude/kb/<domain>/` | `@Regis-BR` (especialista por domínio quando time crescer) |
| `.github/`, `.github/workflows/` | `@Regis-BR` |
| `*.md`, `docs/` | `@Regis-BR` |

**Estado atual**: dev solo → todos `@Regis-BR`. Quando colaboradores entrarem, basta adicionar handles após `@Regis-BR`. Para forçar review por owner, ative em branch protection: `require_code_owner_reviews: true`.

### 4. Workflows de Actions (Onda 2)

Quatro automações que rodam no GitHub:

| Workflow | Trigger | O que faz |
|----------|---------|-----------|
| `phase-sync-pr.yml` | PR opened/edited | Aplica `phase:build` no PR e na Issue linkada |
| `auto-ship-label.yml` | PR merged | Move PR e Issue para `phase:shipped` |
| `pr-template-check.yml` | PR opened/edited | Valida template e posta comment |
| `sync-labels.yml` | `.github/labels.yml` muda | Re-aplica todas as 47 labels do schema |

Permissões mínimas (princípio do menor privilégio): cada workflow declara apenas `issues: write` ou `pull-requests: write` conforme necessário.

### 5. Project v2 (Onda 2)

`scripts/setup-project.sh` cria projeto "AgentSpec Pipeline" com custom fields:

| Field | Tipo | Opções |
|-------|------|--------|
| `Phase` | Single-select | 🌱 Brainstorm, 📋 Define, 🎨 Design, 🏗️ Build, 🚀 Shipped |
| `Agent` | Single-select | @brainstorm-agent, @define-agent, ..., @function-developer, etc. |
| `Clarity Score` | Number | 0-15 (do Issue Form) |
| `Estimated Days` | Number | Estimativa em dias |
| `KB Domain` | Single-select | gcp, gemini, terraform, etc. |
| `Sprint` | Iteration | Definida pelo maintainer |

**Views recomendadas** (criar via UI após o script):

- **Kanban — Pipeline**: group by `Phase`
- **Roadmap — Sprints**: usando `Sprint` iteration
- **Table — Backlog**: filter `Phase != Shipped`, ordenado por `Estimated Days` desc

### 6. Discussions (verificação manual via Onda 2)

`scripts/check-discussions.sh` valida 4 categorias canônicas:

- 💡 Brainstorm (DISCUSSION)
- ❓ Q&A (QUESTION/ANSWER)
- 📢 Announcements (ANNOUNCEMENT)
- 🛠️ Show & Tell (DISCUSSION)

⚠️ **GitHub não permite criar categorias via API.** O script só **alerta** quais faltam e dá instruções precisas. Você cria manualmente em `Settings → Discussions → New category`.

---

## Branch protection state

| Setting | Valor atual | Justificativa |
|---------|-------------|---------------|
| `required_pull_request_reviews.required_approving_review_count` | `0` | Dev solo (sobe para 1+ quando ganhar colaboradores) |
| `required_pull_request_reviews.dismiss_stale_reviews` | `true` | Aprovações antigas expiram em novos commits |
| `required_pull_request_reviews.require_code_owner_reviews` | `false` | Será `true` quando CODEOWNERS tiver múltiplos handles |
| `required_linear_history` | `true` | Sem merge commits — histórico legível |
| `required_conversation_resolution` | `true` | Comentários de review resolvidos antes de merge |
| `enforce_admins` | `true` | Admin não bypassa |
| `required_status_checks` | `null` | Será preenchido na Onda 3 com `pr-template-check`, `validate-sdd-artifacts`, etc. |

---

## O que ainda falta (Ondas 3-4)

| Capacidade | Onda |
|------------|------|
| Validação automática de DEFINE/DESIGN/BUILD_REPORT em PR | 3 |
| KB drift detection (concept >90 dias sem `mcp_validated`) | 3 |
| Lint de agent definitions (frontmatter, tools válidas) | 3 |
| KB publicado como GitHub Pages (MkDocs) | 3 |
| Telemetria como Actions Summary + dashboard | 3 |
| KB MCP Server (consumível por Cursor/Windsurf/n8n) | 4 |
| Bidirectional Issue ↔ DEFINE.md sync | 4 |
| Iterate-cascade automation | 4 |
| Auto-release on `/ship` | 4 |
| Devcontainer para Codespaces | 4 |

---

## Troubleshooting

### Workflow não roda

```bash
# Verifica último run
gh run list --repo Regis-BR/bravo-code-sdd-g --limit 5

# Ver detalhes
gh run view <run-id> --repo Regis-BR/bravo-code-sdd-g
```

### Label não aplicada automaticamente

Verifique que a label existe no schema:

```bash
gh label list --repo Regis-BR/bravo-code-sdd-g | grep "phase:"
```

Se faltar, force re-sync:

```bash
gh workflow run sync-labels.yml --repo Regis-BR/bravo-code-sdd-g
```

### Project v2 não auto-adiciona Issues

Configure manualmente em:

```
https://github.com/users/Regis-BR/projects/<N>/workflows
```

→ Habilitar "Auto-add to project" → filtrar por `repo:Regis-BR/bravo-code-sdd-g is:issue`

### CODEOWNERS não força review

Edite branch protection:

```bash
gh api repos/Regis-BR/bravo-code-sdd-g/branches/main/protection \
  --method PATCH \
  --field 'required_pull_request_reviews[require_code_owner_reviews]=true'
```

(Só ative quando tiver mais de um colaborador.)
