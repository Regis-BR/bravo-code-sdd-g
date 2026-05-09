# Security Policy

## Reporting a vulnerability

Se você identificar uma vulnerabilidade de segurança neste repositório (incluindo workflows do GitHub Actions, scripts, ou no servidor MCP introduzido na Onda 4), **não abra Issue pública**.

Reporte de forma responsável:

- **Email**: regis@rnztech.com
- **GPG Key (opcional)**: disponível mediante solicitação
- **Tempo de resposta esperado**: ≤72h em dias úteis

Inclua no relatório:

1. Descrição da vulnerabilidade
2. Passos de reprodução (PoC se possível)
3. Impacto estimado (escopo, escalada, dados expostos)
4. Sugestão de mitigação (se houver)

---

## Escopo

Vulnerabilidades dentro do escopo deste repo:

- **GitHub Actions workflows** (`.github/workflows/`) — risco de injection via PR de fork malicioso
- **Scripts de automação** (qualquer Python/JS executado via Actions)
- **MCP server** (`kb-mcp/`, a partir da Onda 4) — exposição não intencional de dados
- **Issue/PR templates** com `pull_request_target` ou similares
- **Agent definitions** (`.claude/agents/`) com prompts que possam vazar dados sensíveis

Fora do escopo:

- Vulnerabilidades em dependências terceirizadas (reporte direto ao mantenedor da dep)
- Bugs do upstream `ip2cloud/bravo-code-sdd` que persistem aqui (reporte ao upstream)
- Bugs do Claude Code, GitHub Actions, Anthropic API, etc.

---

## Práticas de segurança aplicadas

| Prática | Status | Onda |
|---------|--------|------|
| Branch protection em `main` | A configurar | 2 |
| Required PR review | A configurar | 2 |
| Required status checks | A configurar | 3 |
| Dependabot alerts | A habilitar | 2 |
| Secret scanning | Habilitado por GitHub default | — |
| CodeQL para JS/TS (kb-mcp) | A habilitar | 4 |
| Pinned action versions (SHA, não tag) | A aplicar | 3 |
| Least-privilege `GITHUB_TOKEN` por workflow | A aplicar | 3 |
| `pull_request_target` evitado quando possível | A aplicar | 3 |

---

## Hall of fame

(Vazio — nenhum reporte recebido até o momento.)

Reporters elegíveis para reconhecimento público (com consentimento) após confirmação e mitigação da vulnerabilidade.
