<!--
  PR Template — bravo-code-sdd-g
  Validações automáticas (Onda 3) checarão preenchimento.
  PRs com checklist incompleto serão bloqueados via Branch Protection rules.
-->

## 📋 Feature

<!-- Vincule à Issue da feature usando "Closes #N". Múltiplas Issues: "Closes #N, Closes #M". -->
Closes #

## 📦 Tipo de mudança

- [ ] 🚀 Build phase — implementação de código (gerou `BUILD_REPORT_*.md`)
- [ ] 🔄 Iterate — atualização em fase anterior (DEFINE/DESIGN/BUILD)
- [ ] 📚 KB update — mudança em `.claude/kb/`
- [ ] 🤖 Agent/Command update — mudança em `.claude/agents/` ou `.claude/commands/`
- [ ] 🔧 Infra — workflows, configs, devcontainer, MCP server
- [ ] 📝 Docs — README, CONTRIBUTING, MkDocs Pages
- [ ] 🐛 Bug fix
- [ ] ⚠️ Breaking change

## 🔗 Artefatos SDD

<!-- Links para os artefatos das fases. Use paths relativos. -->

- DEFINE: `.claude/sdd/features/DEFINE_FEATURE_NAME.md`
- DESIGN: `.claude/sdd/features/DESIGN_FEATURE_NAME.md`
- BUILD_REPORT: `.claude/sdd/reports/BUILD_REPORT_FEATURE_NAME.md`

## 🤖 Agent attribution

<!-- Quais subagentes foram usados na fase Build? Liste no formato @agent-name → arquivo(s) gerado(s). -->

- `@function-developer` → `src/handlers/foo.py`, `src/handlers/bar.py`
- `@test-generator` → `tests/test_foo.py`
- `@infra-deployer` → `infra/terraform/cloudrun.tf`

## 📚 KB references usados

<!-- Quais concepts/patterns do KB foram aplicados? Críticos para cost/quality tracking. -->

- `kb/gcp/patterns/event-driven-pipeline.md`
- `kb/gemini/patterns/structured-json-output.md`
- `kb/pydantic/patterns/llm-output-validation.md`

## ✅ Checklist do contribuidor

### Código

- [ ] Tests passam localmente (`pytest`, `npm test`, etc.)
- [ ] Linter limpo (`ruff`, `eslint`, `tflint` — conforme aplicável)
- [ ] Type checks passam (`mypy`, `tsc`, `pyright`)
- [ ] Sem secrets, credenciais ou tokens commitados
- [ ] Sem PII real em fixtures/exemplos

### Artefatos SDD

- [ ] DEFINE existe e está vinculado acima
- [ ] DESIGN existe e está vinculado acima
- [ ] BUILD_REPORT existe e contém Verification + Issues encountered
- [ ] Agent attribution preenchido (lista acima)
- [ ] KB references preenchido (lista acima)

### KB (se PR mexe em `.claude/kb/`)

- [ ] Limites de tamanho respeitados (`concept ≤150`, `pattern ≤200`, `quick-reference ≤100`)
- [ ] `_index.yaml` atualizado com nova entrada (se adição) ou `mcp_validated` atualizado (se update)
- [ ] Confidence score declarado e justificado
- [ ] Sem duplicação com concept/pattern existente

### Documentação

- [ ] README atualizado (se mudança visível ao usuário)
- [ ] CONTRIBUTING atualizado (se mudança no fluxo)
- [ ] MkDocs Pages build passa (Onda 3+)

## 🧪 Como testar

<!-- Passos para o revisor reproduzir e validar. -->

```bash
# 1. ...
# 2. ...
# 3. ...
```

## 📸 Screenshots / output (se aplicável)

<!-- Cole screenshots de UI, exemplos de output, ou diagrams Mermaid. -->

## 🚨 Riscos / impacto downstream

<!-- O que pode quebrar? Que outros sistemas/features são afetados? -->

- Riscos identificados:
- Mitigações aplicadas:
- Itens que precisam atenção em produção:

## 📎 Notas adicionais

<!-- Decisões de design não óbvias, alternativas consideradas, débito técnico assumido. -->

---

<!-- 
  Branch Protection (Onda 2+) exige:
  - PR review obrigatório (CODEOWNERS)
  - Status checks: validate-sdd-artifacts, lint-agents, kb-drift-check (Onda 3)
  - Branch atualizado com main
-->
