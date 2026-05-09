# Knowledge Base

> 8 domínios técnicos validados via MCP. Última verificação: ver `.claude/kb/_index.yaml`.

| Domínio | Foco | Confidence |
|---------|------|------------|
| [GCP](gcp.md) | Cloud Run, Pub/Sub, GCS, BigQuery, IAM | 0.95 |
| [Terraform](terraform.md) | IaC para GCP, módulos | 0.95 |
| [Terragrunt](terragrunt.md) | Multi-environment IaC, DRY hierarchies | 0.95 |
| [Gemini](gemini.md) | LLM multimodal, extração de documentos | 0.95 |
| [OpenRouter](openrouter.md) | LLM gateway, fallback, 400+ modelos | 0.95 |
| [Pydantic](pydantic.md) | Validação de output LLM estruturado | 0.95 |
| [Langfuse](langfuse.md) | LLMOps observability, cost tracking | 0.95 |
| [CrewAI](crewai.md) | Multi-agent orchestration | 0.95 |

## Estrutura de cada domínio

```
.claude/kb/<domain>/
├── index.md          # Visão geral
├── quick-reference.md  # Cheatsheet ≤100 linhas
├── concepts/         # Fundamentos (≤150 linhas cada)
├── patterns/         # Soluções aplicadas (≤200 linhas cada)
└── specs/            # Schemas YAML
```

## KB Drift

A automação `kb-drift-check.yml` roda semanalmente e abre Issues para domínios com `mcp_validated` >90 dias.
