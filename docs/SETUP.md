# Setup pós-aplicação da Onda 1

> Passo a passo das **ações manuais** que precisam ser feitas no GitHub após mergear a Onda 1.

---

## Pré-requisitos

```bash
# Confira que a Onda 1 está aplicada e mergeada em main
git pull origin main
ls .github/ISSUE_TEMPLATE/  # deve listar 5 .yml
ls README.md LICENSE-NOTICE.md CONTRIBUTING.md SECURITY.md  # devem existir

# Confira que gh CLI está instalado e autenticado
gh auth status
```

Se `gh auth status` falhar, rode `gh auth login` antes.

---

## Passo 1 — Marcar repo como Template

Pela UI:
1. Vá em **Settings** do repo (`https://github.com/Regis-BR/bravo-code-sdd-g/settings`)
2. Role até **General → Template repository**
3. Marque a caixa "Template repository"
4. Salve

Pela CLI:
```bash
gh repo edit Regis-BR/bravo-code-sdd-g --template
```

**Por que?** Permite que outros (ou você mesmo) criem novos projetos via "Use this template" mantendo a estrutura `.claude/` pronta.

---

## Passo 2 — Adicionar descrição e topics

```bash
gh repo edit Regis-BR/bravo-code-sdd-g \
  --description "AI-Native Spec-Driven Development framework for Claude Code com integração nativa ao GitHub" \
  --homepage "https://Regis-BR.github.io/bravo-code-sdd-g" \
  --add-topic claude-code \
  --add-topic spec-driven-development \
  --add-topic ai-agents \
  --add-topic agentic-workflow \
  --add-topic gcp \
  --add-topic llm-extraction \
  --add-topic github-template
```

**Por que?** Topics aumentam discoverability. Descrição aparece na busca e na página.

---

## Passo 3 — Aplicar labels

```bash
# Da raiz do repo
./scripts/apply-labels.sh
```

Output esperado: ~50 labels criadas/atualizadas. Se algum erro, garanta que `yq` está instalado:

```bash
# Ubuntu/WSL
sudo snap install yq
# OU
sudo wget -qO /usr/local/bin/yq https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64
sudo chmod +x /usr/local/bin/yq
```

**Por que?** As labels são usadas pelos Issue Forms (campo "priority", "phase", etc.) e pelos workflows da Onda 2+.

Verificação:
```bash
gh label list --repo Regis-BR/bravo-code-sdd-g | wc -l   # deve retornar ~50
```

---

## Passo 4 — Habilitar Discussions

Pela UI:
1. **Settings → General → Features**
2. Marque **Discussions**
3. Crie categorias inicialmente:
   - **💡 Brainstorm** (Discussion type)
   - **❓ Q&A** (Question & Answer type)
   - **📢 Announcements** (Announcement type, mantenedor only)
   - **🛠️ Show & Tell** (Discussion type)

Pela CLI (não há comando direto para criar categorias, só para habilitar):
```bash
gh repo edit Regis-BR/bravo-code-sdd-g --enable-discussions
```

**Por que?** Brainstorm exploratório vai melhor em Discussion (threaded, sem pressão de tracking) e converte para Issue quando matura.

---

## Passo 5 — Configurar default branch protections (mínimo)

Pela UI: **Settings → Branches → Add classic branch protection rule** para `main`:

- ✅ Require a pull request before merging
- ✅ Require approvals: 1 (você mesmo até a Onda 2)
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require linear history (proibe merge commits, força squash/rebase)
- ❌ Required status checks (vazio até Onda 3 ter workflows)
- ✅ Do not allow bypassing the above settings (até para admins)

Pela CLI:
```bash
gh api repos/Regis-BR/bravo-code-sdd-g/branches/main/protection \
  --method PUT \
  --field required_pull_request_reviews[required_approving_review_count]=1 \
  --field required_pull_request_reviews[dismiss_stale_reviews]=true \
  --field required_linear_history=true \
  --field enforce_admins=true \
  --field required_status_checks=null \
  --field restrictions=null
```

**Por que?** Mesmo trabalhando solo, força revisão consciente do próprio PR antes de mergear, evita push direto em main.

---

## Passo 6 — Habilitar Dependabot alerts

Pela UI: **Settings → Code security and analysis**:

- ✅ Dependabot alerts
- ✅ Dependabot security updates
- ✅ Dependabot version updates (criar `.github/dependabot.yml` na Onda 3)
- ✅ Secret scanning (já vem habilitado em repos públicos)
- ✅ Push protection (recomendado)

Pela CLI:
```bash
gh api repos/Regis-BR/bravo-code-sdd-g/vulnerability-alerts \
  --method PUT
gh api repos/Regis-BR/bravo-code-sdd-g/automated-security-fixes \
  --method PUT
```

---

## Passo 7 — Validação rápida

Após todos os passos:

```bash
# Issue Forms aparecem ao criar Issue?
echo "Acesse: https://github.com/Regis-BR/bravo-code-sdd-g/issues/new/choose"

# Topics aparecem na página principal?
gh repo view Regis-BR/bravo-code-sdd-g --json topics

# Template repo está marcado?
gh repo view Regis-BR/bravo-code-sdd-g --json isTemplate

# Labels existem?
gh label list --repo Regis-BR/bravo-code-sdd-g | head -10
```

---

## Próximo passo

Onda 1 ✅ → Pronto para receber Onda 2 (Integração GitHub).

Veja [`ROADMAP.md`](ROADMAP.md) para o que vem.

---

## Troubleshooting

### `gh: command not found`

```bash
# Ubuntu/WSL
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update && sudo apt install gh
gh auth login
```

### `yq: command not found`

```bash
sudo snap install yq
# OU baixar binário diretamente
sudo wget -qO /usr/local/bin/yq https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64
sudo chmod +x /usr/local/bin/yq
```

### Labels não criadas

Verifique permissões: `gh auth status` deve mostrar scope `repo`. Se não:

```bash
gh auth refresh -s repo
```
