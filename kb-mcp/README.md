# kb-mcp

> MCP server expondo a Knowledge Base do `bravo-code-sdd-g` para qualquer cliente compatível com Model Context Protocol — Claude Code, Cursor, Windsurf, n8n.

---

## O que faz

Lê `.claude/kb/_index.yaml` e expõe 6 tools:

| Tool | Descrição |
|------|-----------|
| `kb_list_domains` | Lista todos os domínios com counts (concepts/patterns/specs) |
| `kb_get_domain` | Retorna metadata completa de um domínio |
| `kb_search` | Busca full-text em concepts e patterns, retorna ranked snippets |
| `kb_read_concept` | Lê conteúdo completo de um concept específico |
| `kb_read_pattern` | Lê conteúdo completo de um pattern específico |
| `kb_quick_reference` | Retorna o quick-reference (cheatsheet) de um domínio |

Cache em memória com invalidação por mtime — edições no `_index.yaml` são detectadas automaticamente.

---

## Instalação

### Opção 1: Build local (recomendado durante dev)

```bash
cd kb-mcp
npm install
npm run build
```

Saída: `dist/index.js` executável.

### Opção 2: Via npx (após publicação no npm)

```bash
npx @regis-br/kb-mcp
```

> Não publicado ainda no momento da Onda 4.

---

## Configuração no Claude Code

Edite `~/.claude/settings.json` (Linux/macOS) ou `%APPDATA%\Claude\settings.json` (Windows):

```json
{
  "mcpServers": {
    "kb": {
      "command": "node",
      "args": ["/caminho/absoluto/para/kb-mcp/dist/index.js"],
      "env": {
        "KB_ROOT": "/caminho/absoluto/para/bravo-code-sdd-g/.claude/kb"
      }
    }
  }
}
```

Reinicie o Claude Code. Verifique conexão:

```
> /mcp
```

Você deve ver `kb` listado com 6 tools.

### Uso típico no Claude Code

```text
> @agent-define-agent encontre patterns para validação de output LLM no domínio pydantic
```

O agent invoca `kb_search` com `query="validation output", domain="pydantic"` e recebe ranked snippets sem precisar de Read em cada arquivo manualmente.

---

## Configuração no Cursor

Adicione ao `.cursor/mcp.json` na raiz do projeto:

```json
{
  "mcpServers": {
    "kb": {
      "command": "node",
      "args": ["./kb-mcp/dist/index.js"],
      "env": {
        "KB_ROOT": "./.claude/kb"
      }
    }
  }
}
```

---

## Configuração no n8n

n8n suporta MCP via [n8n-nodes-mcp-client](https://github.com/n8n-io/n8n-nodes-mcp-client). Configure como servidor MCP local:

```yaml
command: node
args: ['/caminho/absoluto/para/kb-mcp/dist/index.js']
env:
  KB_ROOT: '/caminho/absoluto/para/.claude/kb'
```

---

## Variáveis de ambiente

| Var | Default | Descrição |
|-----|---------|-----------|
| `KB_ROOT` | `../.claude/kb` ou `./.claude/kb` (auto-detect) | Caminho absoluto para `.claude/kb/` |

---

## Desenvolvimento

```bash
# Build
npm run build

# Watch mode (rebuild on change)
npm run dev

# Type check sem emitir output
npm run lint

# Smoke test (precisa de KB_ROOT configurado)
KB_ROOT=../.claude/kb node dist/index.js < /dev/null
# Deve imprimir "Starting" + "Connected via stdio. Ready." no stderr
```

### Testar tools manualmente via stdin

```bash
KB_ROOT=../.claude/kb node dist/index.js << 'EOF'
{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
EOF
```

---

## Arquitetura

```text
┌─────────────────────────────────────────┐
│  LLM Client (Claude Code, Cursor, etc.) │
└─────────────────┬───────────────────────┘
                  │ stdio (JSON-RPC)
                  ▼
┌─────────────────────────────────────────┐
│  src/index.ts (entry point)             │
│  ↓ StdioServerTransport                 │
│  src/server.ts (MCP Server)             │
│  ├─ ListToolsRequestSchema handler      │
│  └─ CallToolRequestSchema handler       │
│         ↓                               │
│  src/tools.ts (6 tool definitions)      │
│         ↓                               │
│  src/kb-loader.ts                       │
│  ├─ getIndex() — parse _index.yaml      │
│  ├─ search() — keyword scoring          │
│  └─ readKBFile() — sandboxed read       │
└─────────────────┬───────────────────────┘
                  │ readFile
                  ▼
        .claude/kb/
        ├── _index.yaml
        ├── gcp/
        │   ├── concepts/
        │   └── patterns/
        ├── pydantic/
        ...
```

### Segurança

- `readKBFile` sandbox: rejeita paths que escapam de `KB_ROOT` (proteção contra `..` injection)
- Cache invalidado por mtime — não serve conteúdo stale após edição
- Logs em `stderr` (stdout reservado para MCP protocol)

---

## Troubleshooting

### "Could not detect KB root"

Defina `KB_ROOT` explicitamente no `env` da configuração do cliente:

```json
"env": { "KB_ROOT": "/caminho/absoluto/para/.claude/kb" }
```

### "Domain not found"

Verifique que o slug está em `_index.yaml` na seção `domains:`:

```bash
yq eval '.domains | keys' .claude/kb/_index.yaml
```

### Tools listadas mas vazias / 0 results

Os concepts/patterns têm path relativo ao `path` do domínio em `_index.yaml`:

```yaml
domains:
  gcp:
    path: gcp/                      # ← relativo ao KB_ROOT
    concepts:
      - name: cloud-run
        path: concepts/cloud-run.md  # ← relativo ao path do domain
```

Confira se os arquivos físicos existem em `KB_ROOT/<domain.path>/<concept.path>`.

### MCP server não aparece no cliente

1. Verifique sintaxe JSON do settings (use `jq . settings.json`)
2. Verifique que `node` está no PATH do cliente
3. Cheque logs do cliente (Claude Code: `~/.claude/logs/`)

---

## Roadmap

- [ ] Resources MCP (cada concept/pattern como resource URI `kb://<domain>/<type>/<name>`)
- [ ] Prompts MCP (templates de uso pré-definidos)
- [ ] Health check tool (`kb_drift_status`)
- [ ] Publicação no npm como `@regis-br/kb-mcp`

Veja [docs/MCP_SERVER.md](../docs/MCP_SERVER.md) para detalhes da integração com o resto do framework.

---

## Licença

Veja `LICENSE-NOTICE.md` na raiz do repo.
