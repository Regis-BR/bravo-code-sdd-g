#!/usr/bin/env node
// =============================================================================
// index.ts — Entry point do kb-mcp server
// =============================================================================
// Roda como subprocess via stdio MCP transport. Configurável via env:
//   KB_ROOT — caminho para .claude/kb/ (default: detecta via cwd)
// =============================================================================

import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { resolve } from "node:path";
import { existsSync } from "node:fs";
import { createServer } from "./server.js";

function detectKBRoot(): string {
  // 1. Env var explícita
  if (process.env["KB_ROOT"]) {
    return resolve(process.env["KB_ROOT"]);
  }

  // 2. Tenta ../.claude/kb (caso script esteja em kb-mcp/dist/)
  const fromDist = resolve(process.cwd(), "../.claude/kb");
  if (existsSync(fromDist)) {
    return fromDist;
  }

  // 3. Tenta ./.claude/kb (caso esteja na raiz do repo)
  const fromCwd = resolve(process.cwd(), ".claude/kb");
  if (existsSync(fromCwd)) {
    return fromCwd;
  }

  // 4. Fallback: erro com instrução
  throw new Error(
    `Could not detect KB root. Set KB_ROOT env var to the path of your .claude/kb/ directory.\n` +
      `Searched:\n  - ${fromDist}\n  - ${fromCwd}`
  );
}

async function main(): Promise<void> {
  const kbRoot = detectKBRoot();
  // Logs vão para stderr para não conflitar com MCP stdio (stdout)
  console.error(`[kb-mcp] Starting with KB_ROOT=${kbRoot}`);

  const server = createServer({ kbRoot });
  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error(`[kb-mcp] Connected via stdio. Ready.`);
}

main().catch((e) => {
  console.error(`[kb-mcp] Fatal: ${(e as Error).message}`);
  process.exit(1);
});
