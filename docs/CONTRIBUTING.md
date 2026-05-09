# Contributing

> Este fork é mantido para uso interno de **Regis Renzi / RNZ Tech Ltda**. Contribuições externas não estão abertas no momento, mas o fluxo abaixo documenta como o framework opera para quem usa internamente ou faz parte do círculo autorizado.

---

## TL;DR

```text
1. Abrir Issue tipo "brainstorm" ou "define" via Issue Form
2. Deixar o agente Claude conduzir a fase
3. Commitar artefatos SDD em .claude/sdd/features/
4. Abrir PR usando o template (vincula com `Closes #N`)
5. Validações automáticas (Onda 3) checam estrutura
6. Após merge → /ship arquiva e fecha o ciclo
```

---

## Fluxo SDD via GitHub (este fork)

### 1. Brainstorm (opcional, fase 0)

Para ideias vagas que precisam de exploração:

```bash
# Abre Issue tipo "brainstorm" com Issue Form
gh issue create --template brainstorm.yml
```

Ou diretamente no Claude Code:

```bash
/brainstorm "ideia inicial"
```

O `brainstorm-agent` (Opus) faz Q&A, explora 2-3 abordagens, aplica YAGNI, gera `BRAINSTORM_{FEATURE}.md`.

**Estado da Issue**: label `phase:brainstorm`, body editado pelo agente, comments com Q&A.

### 2. Define (fase 1)

Para requisitos validáveis:

```bash
gh issue create --template define.yml
# OU
/define <input>
```

O `define-agent` (Opus) extrai requisitos, calcula clarity score (mínimo 12), gera `DEFINE_{FEATURE}.md`.

**Estado da Issue**: label muda para `phase:define`. Issue Form força campos obrigatórios (Problem Statement, Target Users, Success Criteria, Acceptance Tests, Out of Scope) — clarity score nativo na UI.

### 3. Design (fase 2)

```bash
/design <feature>
```

O `design-agent` (Opus) define arquitetura, faz **agent matching** (identifica quais subagentes especialistas executarão cada peça), gera `DESIGN_{FEATURE}.md`.

**Estado da Issue**: label `phase:design`. Comment do agente lista agentes alocados.

### 4. Build (fase 3)

```bash
/build <feature>
```

O `build-agent` (Sonnet) executa via subagentes especialistas, gera código + `BUILD_REPORT_{FEATURE}.md`. Cria branch `feature/{feature-name}`.

```bash
/create-pr
```

Abre PR com:
- `Closes #<issue-number>` na descrição
- Links para DEFINE, DESIGN, BUILD_REPORT
- Checklist do PR template preenchido
- Labels `phase:build`

**Validação automática (Onda 3)**: GitHub Action checa estrutura dos artefatos, falha PR se algo estiver faltando.

### 5. Ship (fase 4)

Após merge do PR:

```bash
/ship <feature>
```

O `ship-agent` (Haiku) move artefatos para `archive/{FEATURE}/`, gera `SHIPPED_{DATE}.md`, opcionalmente cria GitHub Release (Onda 4).

**Estado da Issue**: closed automaticamente pelo `Closes #N` do PR. Label `phase:shipped`.

### Cross-phase: Iterate

```bash
/iterate <feature>
```

Atualiza fase anterior com **cascata** — se DEFINE muda, DESIGN existente é marcado para revisão automaticamente (Onda 4 via Action).

---

## Convenções

### Branches

| Padrão | Uso |
|--------|-----|
| `feature/<phase>-<feature-name>` | Trabalho ativo em uma fase específica |
| `iterate/<feature-name>-<date>` | Iteração em feature já shippada |
| `kb/<domain>-<concept>` | Atualização de KB |
| `infra/<change>` | Mudança em workflows/configs do framework |

### Commits

Conventional Commits, com prefixo de fase quando aplicável:

```
feat(define): add invoice extraction requirements (#42)
feat(design): agent matching for #42
feat(build): implement Cloud Run handler (#42)
docs(kb): update gemini quick-reference
chore(infra): bump validate-sdd action to v2
```

### Issues — Labels obrigatórias

Toda Issue deve ter pelo menos:

- 1 label de fase: `phase:brainstorm`, `phase:define`, `phase:design`, `phase:build`, `phase:shipped`
- 1 label de prioridade: `priority:critical`, `priority:high`, `priority:normal`, `priority:low`
- (Opcional) labels de domínio KB: `kb-domain:gcp`, `kb-domain:gemini`, etc.

### PRs — Checklist obrigatório

PR só será mergeado quando o template estiver totalmente preenchido (validação humana até a Onda 3, automatizada depois):

- [ ] `Closes #<N>` declarado
- [ ] Links para DEFINE, DESIGN, BUILD_REPORT
- [ ] KB references citadas (qual pattern/concept foi usado)
- [ ] Agent attribution declarado no BUILD_REPORT
- [ ] Tests pass

---

## Estrutura de arquivos

### Para SDD features

```
.claude/sdd/features/
├── BRAINSTORM_{FEATURE}.md   # Fase 0 (opcional)
├── DEFINE_{FEATURE}.md       # Fase 1
└── DESIGN_{FEATURE}.md       # Fase 2

.claude/sdd/reports/
└── BUILD_REPORT_{FEATURE}.md # Fase 3

.claude/sdd/archive/{FEATURE}/
└── SHIPPED_{YYYY-MM-DD}.md   # Fase 4
```

### Para Dev Loop

```
.claude/dev/tasks/
└── PROMPT_{TASK}.md          # Active

.claude/dev/progress/
└── PROGRESS_{TASK}.md        # Auto-managed

.claude/dev/logs/
└── LOG_{TASK}.md             # Auto-generated
```

### Para KB

Cada novo domínio segue templates de `.claude/kb/_templates/`:

```
.claude/kb/<domain>/
├── index.md                  # ≤150 linhas
├── quick-reference.md        # ≤100 linhas
├── concepts/                 # ≤150 linhas cada
├── patterns/                 # ≤200 linhas cada
└── specs/                    # YAML schemas
```

E adicione entrada em `.claude/kb/_index.yaml`.

---

## Code review

Code review é **obrigatório** em todo PR que toca:

- `.claude/agents/**` (mudança em definição de agente)
- `.claude/sdd/templates/**` (mudança em template)
- `.claude/kb/_index.yaml` (registry do KB)
- `.github/workflows/**` (automação)

Owners definidos em `.github/CODEOWNERS` (Onda 2).

---

## Dúvidas

- Discussions: https://github.com/Regis-BR/bravo-code-sdd-g/discussions (habilitado a partir da Onda 2)
- Email: regis@rnztech.com

---

## Notas legais

Veja [LICENSE-NOTICE.md](LICENSE-NOTICE.md) para a situação jurídica completa deste fork.
