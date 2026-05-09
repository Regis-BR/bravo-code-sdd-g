# Roadmap — bravo-code-sdd-g

> Plano de evolução deste fork em 4 ondas. Estado atual: **Onda 1 — em entrega**.

---

## Visão geral

```text
╔═══════════════════════════════════════════════════════════════════╗
║   Roadmap em 4 ondas                                              ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║   ONDA 1 ✅       ONDA 2 ✅       ONDA 3 📋       ONDA 4 🚀       ║
║   ────────        ────────        ────────        ────────        ║
║   Fundação        Integração       Automação      Estrutural      ║
║   (~1 dia)        GitHub           (~1 sem)       (~2 sem)        ║
║                   (~3 dias)                                       ║
║                                                                   ║
║   README          CODEOWNERS       Validate-SDD   MCP Server      ║
║   LICENSE-NOTICE  Project v2       KB-Drift       Bidi-Sync       ║
║   CONTRIBUTING    Discussions      Lint-Agents    Iterate-        ║
║   SECURITY        Branch protect   MkDocs Pages   Cascade         ║
║   Issue Forms     Sync Issue↔SDD   Bootstrap      Auto-Release    ║
║   PR Template     Project setup    Telemetry      Devcontainer    ║
║   labels.yml                                                      ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
```

---

## Onda 1 — Fundação ✅

**Objetivo**: Tornar o fork apresentável, juridicamente honesto, e pronto para fluxo SDD via GitHub Issues.

**Entregáveis**:

| Item | Arquivo | Status |
|------|---------|--------|
| README com pipeline + estrutura + comandos | `README.md` | ✅ |
| Nota legal sobre licenciamento | `LICENSE-NOTICE.md` | ✅ |
| Guia de contribuição com fluxo SDD | `CONTRIBUTING.md` | ✅ |
| Política de segurança | `SECURITY.md` | ✅ |
| Code of Conduct minimalista | `CODE_OF_CONDUCT.md` | ✅ |
| `.gitignore` robusto | `.gitignore` | ✅ |
| Issue Form: Brainstorm | `.github/ISSUE_TEMPLATE/brainstorm.yml` | ✅ |
| Issue Form: Define (com clarity score) | `.github/ISSUE_TEMPLATE/define.yml` | ✅ |
| Issue Form: Iterate | `.github/ISSUE_TEMPLATE/iterate.yml` | ✅ |
| Issue Form: Bug report | `.github/ISSUE_TEMPLATE/bug-report.yml` | ✅ |
| Issue Form: KB update | `.github/ISSUE_TEMPLATE/kb-update.yml` | ✅ |
| Issue selector config | `.github/ISSUE_TEMPLATE/config.yml` | ✅ |
| PR Template com checklist SDD | `.github/PULL_REQUEST_TEMPLATE.md` | ✅ |
| Labels schema | `.github/labels.yml` | ✅ |
| Script de aplicação de labels | `scripts/apply-labels.sh` | ✅ |
| Documentação do roadmap | `docs/ROADMAP.md` | ✅ |
| Guia de setup pós-fork | `docs/SETUP.md` | ✅ |

**Ações manuais necessárias após aplicar Onda 1** (não dá pra fazer via git):

1. Configurações → marcar repo como **Template repository**
2. Configurações → adicionar **descrição** e **topics**: `claude-code`, `spec-driven-development`, `ai-agents`, `gcp`, `llm-extraction`, `agentic-workflow`
3. Rodar `./scripts/apply-labels.sh` para sincronizar labels
4. Configurações → habilitar **Discussions** (preparação para Onda 2)
5. Configurações → habilitar **Sponsors** (opcional)

---

## Onda 2 — Integração GitHub ✅

**Objetivo**: Transformar Issues, PRs e Project v2 em parte estrutural do framework, não apenas hospedagem.

**Entregáveis**:

| Item | Arquivo | Status |
|------|---------|--------|
| CODEOWNERS por path/domínio | `.github/CODEOWNERS` | ✅ |
| Workflow: phase-sync de PRs para Issues | `.github/workflows/phase-sync-pr.yml` | ✅ |
| Workflow: auto-ship label ao mergear | `.github/workflows/auto-ship-label.yml` | ✅ |
| Workflow: validação de PR template | `.github/workflows/pr-template-check.yml` | ✅ |
| Workflow: sync-labels automático | `.github/workflows/sync-labels.yml` | ✅ |
| Script setup Project v2 (custom fields, link repo) | `scripts/setup-project.sh` | ✅ |
| Script check-discussions (alerta categorias faltando) | `scripts/check-discussions.sh` | ✅ |
| Documentação da integração GitHub-nativa | `docs/GITHUB_INTEGRATION.md` | ✅ |

**Critério de "pronto"**: ✅ ao abrir PR vinculado a Issue via `Closes #N`, labels `phase:build` aparecem automaticamente em ambos. Ao mergear, `phase:shipped` é aplicado. PR template check posta comment de validação automaticamente.

---

## Onda 3 — Automação 📋

**Objetivo**: Validação automática de artefatos SDD, KB drift detection, lint de agents, publicação do KB como GitHub Pages.

**Entregáveis planejados**:

| Item | Arquivo | Esforço |
|------|---------|---------|
| Validador de artefatos SDD em PRs | `.github/workflows/validate-sdd-artifacts.yml` + `scripts/validate_sdd.py` | Alto |
| Calculador automático de Clarity Score | `scripts/clarity_score.py` | Médio |
| KB drift detection (cron semanal) | `.github/workflows/kb-drift-check.yml` + `scripts/kb_drift.py` | Alto |
| Lint de agent definitions | `.github/workflows/lint-agents.yml` + `scripts/lint_agents.py` | Médio |
| Sync de labels via Action (em vez de script manual) | `.github/workflows/sync-labels.yml` | Baixo |
| Bootstrap workflow para novos repos via template | `.github/workflows/template-bootstrap.yml` | Médio |
| MkDocs setup + Material theme | `mkdocs.yml`, `docs/index.md` etc. | Médio |
| GitHub Pages deploy workflow | `.github/workflows/pages.yml` | Médio |
| Telemetria como Actions Summary | `.github/workflows/telemetry.yml` | Médio |
| Telemetria dashboard estático | `docs/dashboard/index.html` | Alto |

**Critério de "pronto"**: PR não passa se DEFINE/DESIGN/BUILD_REPORT estão faltando ou mal formatados. KB recebe Issue automática para domínios não validados há mais de 90 dias. KB navegável publicamente em `https://Regis-BR.github.io/bravo-code-sdd-g/`.

---

## Onda 4 — Estrutural 🚀

**Objetivo**: Diferenciação real — KB como MCP server, sincronização bidirecional Issue↔.md, releases automatizadas, devcontainer.

**Entregáveis planejados**:

| Item | Arquivo | Esforço |
|------|---------|---------|
| KB MCP Server (TypeScript) | `kb-mcp/src/index.ts`, `package.json`, etc. | Muito alto |
| Tools MCP: list-domains, get-concept, get-pattern, search-kb | `kb-mcp/src/tools/*.ts` | Alto |
| Documentação MCP server | `kb-mcp/README.md` | Médio |
| Bidirectional Issue ↔ DEFINE.md sync | `.github/workflows/issue-md-sync.yml` + `scripts/sync_issue_md.py` | Muito alto |
| Iterate cascade detection | `.github/workflows/iterate-cascade.yml` + `scripts/cascade_detect.py` | Alto |
| Auto-release on /ship | `.github/workflows/auto-release.yml` | Médio |
| Release notes generator | `scripts/generate_release_notes.py` | Médio |
| Devcontainer setup completo | `.devcontainer/devcontainer.json`, `Dockerfile`, scripts | Alto |
| Codespaces secrets management docs | `docs/CODESPACES.md` | Baixo |

**Critério de "pronto"**: rodar `claude` em Codespaces fresh start funciona em <30s. Editar Issue body atualiza DEFINE_*.md no próximo push. Mudança em DEFINE dispara comment no PR alertando sobre cascata. Ship gera Release no GitHub com changelog.

---

## Sequenciamento das ondas

| Onda | Quando aplicar | Pré-requisito |
|------|----------------|---------------|
| 1 | Imediato | Fork criado |
| 2 | Após Onda 1 mergeada e ações manuais feitas | Labels aplicadas, repo marcado como template |
| 3 | Após Onda 2 mergeada | CODEOWNERS configurado, Project v2 setup |
| 4 | Após Onda 3 mergeada | Validações automáticas estáveis, KB Pages no ar |

[Inference] Aplicar tudo de uma vez funcionaria mas geraria PR gigante difícil de revisar. As 4 ondas permitem aplicar incrementalmente, validar cada uma em uso real, e ajustar antes da próxima.

---

## Tracking

Issues abertas para cada item desta onda receberão label `meta:roadmap` para distinguir do trabalho de feature comum.
