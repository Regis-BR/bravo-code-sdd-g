# bravo-code-sdd-g

> **AgentSpec** — AI-Native Spec-Driven Development framework for Claude Code, com integração nativa ao GitHub.
>
> *Fork de [`ip2cloud/bravo-code-sdd`](https://github.com/ip2cloud/bravo-code-sdd) com extensões de workflow, automação via GitHub Actions, KB-as-MCP e telemetria.*

[![SDD Validation](https://img.shields.io/badge/SDD-validated-green)](.github/workflows/validate-sdd-artifacts.yml)
[![KB Domains](https://img.shields.io/badge/KB-8%20domains-blue)](.claude/kb/_index.yaml)
[![Agents](https://img.shields.io/badge/Agents-35%2B-purple)](.claude/agents/)
[![License](https://img.shields.io/badge/License-Internal%20Use-lightgrey)](LICENSE-NOTICE.md)

---

## O que é

Um framework de Spec-Driven Development (SDD) para Claude Code que materializa **5 fases auditáveis** (Brainstorm → Define → Design → Build → Ship) com **agent matching**, **knowledge base versionada** e **integração nativa com Issues, PRs, Projects e Actions do GitHub**.

Diferente do upstream, este fork trata o GitHub não como hospedagem, mas como **plano de controle do framework**: Issues são containers de feature, PRs validam artefatos SDD via Actions, Projects v2 reflete o estado das fases, e o KB é publicado como GitHub Pages e exposto via MCP.

---

## Quickstart (30 segundos)

```bash
# 1. Use este repo como template no GitHub (botão "Use this template")
# 2. Clone seu novo repo
git clone https://github.com/<seu-user>/<novo-repo>.git
cd <novo-repo>

# 3. Abra no Claude Code
claude

# 4. Inicie sua primeira feature
/brainstorm "ideia inicial vaga"
# ou direto:
/define "Build Cloud Run function para extrair NF-e"
```

A partir daí o framework conduz: agentes especialistas são selecionados na fase Design, o KB fornece patterns validados, e cada artefato vira Issue/PR rastreável no GitHub.

---

## Pipeline em 5 fases

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                    AGENTSPEC 5-PHASE PIPELINE                             │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  PHASE 0      PHASE 1      PHASE 2      PHASE 3      PHASE 4             │
│  BRAINSTORM   DEFINE       DESIGN       BUILD        SHIP                │
│  (Optional)   (What+Why)   (How)        (Do)         (Close)             │
│                                                                           │
│  /brainstorm  /define      /design      /build       /ship               │
│      │            │            │            │            │                │
│      ▼            ▼            ▼            ▼            ▼                │
│   Issue       Issue       Issue       PR opened    PR merged            │
│   created     updated     +DESIGN.md  +BUILD       +SHIPPED.md          │
│   label:       label:      label:      REPORT      label:                │
│   brainstorm   define      design      label:      shipped               │
│                                        build                              │
│                                                                           │
│  Cross-phase: /iterate  →  cascata automática via GitHub Actions         │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

Cada fase usa o modelo Claude apropriado: **Opus** para Brainstorm/Define/Design (raciocínio), **Sonnet** para Build (execução), **Haiku** para Ship (arquivamento).

---

## Quando usar SDD vs Dev Loop

```text
┌─────────────────────────────────────────────────────────────────────┐
│                    QUAL WORKFLOW USAR?                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Tarefa rápida (<3 arquivos, escopo claro)?                         │
│      ─── SIM ──▶ Dev Loop (.claude/dev/)  →  /dev "task"            │
│      ─── NÃO ─┐                                                     │
│               ▼                                                      │
│  Precisa rastreabilidade (audit, handoff, PRD)?                     │
│      ─── NÃO ──▶ Dev Loop                                           │
│      ─── SIM ─┐                                                     │
│               ▼                                                      │
│  Ideia clara?                                                        │
│      ─── SIM ──▶ /define                                            │
│      ─── NÃO ──▶ /brainstorm → /define                              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

| Dimensão | Dev Loop | AgentSpec (SDD) |
|----------|----------|-----------------|
| Fases | 1 (execute) | 5 (brainstorm→ship) |
| Overhead | Baixo | Médio |
| Rastreabilidade | Logs apenas | Issues + PRs + artefatos |
| Agent orchestration | Não | Sim, com matching |
| GitHub integration | Mínima | Issues, PRs, Project v2, Actions |
| Ideal para | Tarefas rápidas | Features complexas |

---

## Estrutura

```text
.
├── .github/                       # Integração GitHub (este fork)
│   ├── ISSUE_TEMPLATE/            # Issue Forms (brainstorm, define, iterate, bug, kb-update)
│   ├── workflows/                 # GitHub Actions
│   ├── labels.yml                 # Labels padronizadas
│   ├── CODEOWNERS                 # Mapeamento KB domain → revisor
│   └── PULL_REQUEST_TEMPLATE.md   # Template de PR com checklist SDD
│
├── .claude/
│   ├── agents/                    # 35+ subagents organizados por categoria
│   │   ├── workflow/              # brainstorm, define, design, build, ship, iterate
│   │   ├── ai-ml/                 # genai-architect, llm-specialist, etc.
│   │   ├── aws/, code-quality/, communication/, data-engineering/
│   │   └── dev/, domain/, exploration/
│   │
│   ├── commands/                  # Slash commands customizados
│   │   ├── workflow/              # /brainstorm, /define, /design, /build, /ship, /iterate
│   │   ├── core/                  # /memory, /sync-context, /telemetry, /readme-maker
│   │   ├── dev/, knowledge/, review/
│   │
│   ├── dev/                       # Dev Loop (Level 2)
│   │   ├── tasks/                 # Active PROMPT files
│   │   ├── progress/              # Session recovery
│   │   ├── logs/                  # Execution audit
│   │   └── templates/, examples/
│   │
│   ├── kb/                        # Knowledge Base (8 domains)
│   │   ├── _index.yaml            # Machine-readable registry
│   │   ├── _templates/            # concept, pattern, spec, quick-reference
│   │   ├── pydantic/, gcp/, gemini/, langfuse/, openrouter/
│   │   └── terraform/, terragrunt/, crewai/
│   │
│   └── sdd/                       # AgentSpec 5-phase workflow (Level 3)
│       ├── architecture/          # ARCHITECTURE.md, WORKFLOW_CONTRACTS.yaml
│       ├── features/              # Active feature specs
│       ├── reports/               # Build reports
│       ├── archive/               # Shipped features
│       ├── templates/, examples/
│
├── docs/                          # MkDocs source para GitHub Pages (Onda 3)
├── kb-mcp/                        # MCP server expondo KB (Onda 4)
└── .devcontainer/                 # Codespaces preconfig (Onda 4)
```

---

## Comandos disponíveis

### Workflow (SDD - 5 fases)

| Comando | Fase | Output |
|---------|------|--------|
| `/brainstorm <ideia>` | 0 | `BRAINSTORM_{FEATURE}.md` + Issue |
| `/define <input>` | 1 | `DEFINE_{FEATURE}.md` (clarity score ≥12) |
| `/design <feature>` | 2 | `DESIGN_{FEATURE}.md` + agent matching |
| `/build <feature>` | 3 | Código + `BUILD_REPORT_*.md` + PR |
| `/ship <feature>` | 4 | `archive/{FEATURE}/SHIPPED_{DATE}.md` |
| `/iterate <feature>` | * | Atualiza fase anterior com cascata |
| `/create-pr` | * | Abre PR vinculado à Issue da feature |

### Dev Loop (rápido)

| Comando | Uso |
|---------|-----|
| `/dev "task"` | Cria PROMPT file e executa |
| `/dev tasks/PROMPT_X.md` | Executa PROMPT existente |
| `/dev tasks/PROMPT_X.md --resume` | Retoma após interrupção |
| `/dev tasks/PROMPT_X.md --dry-run` | Valida sem executar |

### Core / Knowledge / Review

| Comando | Uso |
|---------|-----|
| `/memory` | Gestão de memória persistente |
| `/sync-context` | Sincroniza contexto entre sessões |
| `/telemetry` | Métricas de uso do framework |
| `/create-kb <domain>` | Cria novo domínio no KB |
| `/review <target>` | Code review estruturado |
| `/readme-maker` | Gera README a partir do código |

---

## KB — Knowledge Base

Domínios cobertos (todos validados via MCP em 2026-01):

| Domínio | Foco | Confidence |
|---------|------|------------|
| `gcp` | Cloud Run, Pub/Sub, GCS, BigQuery, IAM | 0.95 |
| `terraform` | IaC para GCP, módulos | 0.95 |
| `terragrunt` | Multi-environment, DRY hierarchies | 0.95 |
| `gemini` | LLM multimodal, extração de documentos | 0.95 |
| `openrouter` | LLM gateway, fallback, 400+ modelos | 0.95 |
| `pydantic` | Validação de output LLM estruturado | 0.95 |
| `langfuse` | LLMOps observability, cost tracking | 0.95 |
| `crewai` | Multi-agent orchestration | 0.95 |

Estrutura por domínio: `concepts/` (fundamentos), `patterns/` (soluções aplicadas), `specs/` (schemas YAML), `quick-reference.md` (cheatsheet ≤100 linhas).

A partir da Onda 3, o KB é publicado como site navegável em `https://Regis-BR.github.io/bravo-code-sdd-g/` via MkDocs.
A partir da Onda 4, é exposto como **MCP server** consumível por qualquer cliente MCP (Claude Desktop, Cursor, Windsurf, n8n).

---

## Roadmap deste fork

Este fork está sendo evoluído em 4 ondas. Estado atual: **Onda 1 — Fundação**.

- [x] **Onda 1 — Fundação** — README, LICENSE-NOTICE, Issue Forms, PR template, labels, CONTRIBUTING, SECURITY
- [ ] **Onda 2 — Integração GitHub** — CODEOWNERS, Project v2 setup, Discussions, fluxo Issue↔SDD
- [ ] **Onda 3 — Automação** — Actions de validação SDD, KB drift detection, lint de agents, MkDocs Pages
- [ ] **Onda 4 — Estrutural** — MCP server do KB, bidirectional Issue↔.md sync, iterate-cascade, devcontainer

Detalhes em [docs/ROADMAP.md](docs/ROADMAP.md).

---

## Como contribuir

Veja [CONTRIBUTING.md](CONTRIBUTING.md). TL;DR: abra Issue do tipo `brainstorm` ou `define`, deixe o agente conduzir a fase, abra PR seguindo o template.

---

## Licença

Este fork é mantido por **Regis Renzi** (RNZ Tech Ltda / Organização Renzi) para uso interno e estudo. Veja [LICENSE-NOTICE.md](LICENSE-NOTICE.md) para detalhes — incluindo a situação jurídica do código herdado do upstream `ip2cloud/bravo-code-sdd`, que não declara licença explícita.

---

## Créditos

- Framework original: [`ip2cloud/bravo-code-sdd`](https://github.com/ip2cloud/bravo-code-sdd)
- Adaptação GitHub-nativa, automação via Actions, KB-as-MCP: este fork
- Construído sobre [Claude Code](https://docs.claude.com/en/docs/claude-code) (Anthropic)
