// =============================================================================
// tools.ts — Definições das tools MCP expostas pelo kb-mcp server
// =============================================================================

import type { KBLoader } from "./kb-loader.js";

export interface ToolHandler {
  name: string;
  description: string;
  inputSchema: {
    type: "object";
    properties: Record<string, { type: string; description: string; enum?: string[] }>;
    required?: string[];
  };
  handler: (args: Record<string, unknown>) => Promise<{ content: Array<{ type: "text"; text: string }> }>;
}

export function buildTools(kb: KBLoader): ToolHandler[] {
  return [
    {
      name: "kb_list_domains",
      description:
        "List all knowledge base domains with their description, mcp_validated date, and counts of concepts/patterns/specs. Use this first to discover what's available.",
      inputSchema: {
        type: "object",
        properties: {},
      },
      handler: async () => {
        const domains = await kb.listDomains();
        const text = [
          `# Knowledge Base — ${domains.length} domains`,
          "",
          "| Domain | Description | Validated | C/P/S |",
          "|--------|-------------|-----------|-------|",
          ...domains.map(
            (d) =>
              `| \`${d.slug}\` | ${d.name} — ${d.description.substring(0, 80)}${d.description.length > 80 ? "…" : ""} | ${d.mcp_validated || "N/A"} | ${d.counts.concepts}/${d.counts.patterns}/${d.counts.specs} |`
          ),
          "",
          "Use `kb_get_domain` for full details, `kb_search` to query content, or `kb_read_concept`/`kb_read_pattern` for specific files.",
        ].join("\n");
        return { content: [{ type: "text", text }] };
      },
    },

    {
      name: "kb_get_domain",
      description:
        "Get full metadata for a specific KB domain: list of concepts, patterns, specs with paths and confidence scores.",
      inputSchema: {
        type: "object",
        properties: {
          slug: {
            type: "string",
            description: "Domain slug (e.g., 'gcp', 'terraform', 'pydantic')",
          },
        },
        required: ["slug"],
      },
      handler: async (args) => {
        const slug = args["slug"] as string;
        const domain = await kb.getDomain(slug);
        const text = [
          `# ${domain.name} (\`${slug}\`)`,
          "",
          domain.description,
          "",
          `**MCP validated**: ${domain.mcp_validated || "N/A"}`,
          `**Path**: \`.claude/kb/${domain.path}\``,
          "",
          "## Entry Points",
          ...(domain.entry_points.index ? [`- Index: \`${domain.entry_points.index}\``] : []),
          ...(domain.entry_points.quick_reference ? [`- Quick Reference: \`${domain.entry_points.quick_reference}\``] : []),
          "",
          `## Concepts (${domain.concepts.length})`,
          ...domain.concepts.map((c) => `- \`${c.name}\` → \`${c.path}\`${c.confidence ? ` (confidence: ${c.confidence})` : ""}`),
          "",
          `## Patterns (${domain.patterns.length})`,
          ...domain.patterns.map((p) => `- \`${p.name}\` → \`${p.path}\``),
          ...(domain.specs.length > 0
            ? ["", `## Specs (${domain.specs.length})`, ...domain.specs.map((s) => `- \`${s.name}\` → \`${s.path}\``)]
            : []),
        ].join("\n");
        return { content: [{ type: "text", text }] };
      },
    },

    {
      name: "kb_search",
      description:
        "Full-text search across concepts and patterns in the KB. Returns ranked results with snippets. Useful when you don't know exact concept names but want to find related material.",
      inputSchema: {
        type: "object",
        properties: {
          query: {
            type: "string",
            description: "Keywords to search for (space-separated). Example: 'cloud run authentication'",
          },
          domain: {
            type: "string",
            description: "Optional: limit to a specific domain slug (e.g., 'gcp')",
          },
          type: {
            type: "string",
            description: "Optional: limit to 'concept' or 'pattern'. Default: 'all'",
            enum: ["concept", "pattern", "all"],
          },
          limit: {
            type: "number",
            description: "Max results (default 10)",
          },
        },
        required: ["query"],
      },
      handler: async (args) => {
        const query = args["query"] as string;
        const domain = args["domain"] as string | undefined;
        const type = (args["type"] as "concept" | "pattern" | "all" | undefined) || "all";
        const limit = (args["limit"] as number | undefined) || 10;

        const results = await kb.search(query, { domain, type, limit });

        if (results.length === 0) {
          return {
            content: [
              {
                type: "text",
                text: `No matches for "${query}"${domain ? ` in domain \`${domain}\`` : ""}.\n\nTry: \`kb_list_domains\` to see what's available, or broader keywords.`,
              },
            ],
          };
        }

        const text = [
          `# Search Results — "${query}" (${results.length} matches)`,
          "",
          ...results.flatMap((r) => [
            `## [${r.score} pts] \`${r.domain}/${r.type}/${r.name}\``,
            "",
            r.snippet,
            "",
            `→ Read full: \`kb_read_${r.type}\` with \`domain: "${r.domain}"\`, \`name: "${r.name}"\``,
            "",
          ]),
        ].join("\n");

        return { content: [{ type: "text", text }] };
      },
    },

    {
      name: "kb_read_concept",
      description:
        "Read full content of a concept (foundational knowledge piece, max ~150 lines). Concepts are bedrock understanding of a topic, not solutions.",
      inputSchema: {
        type: "object",
        properties: {
          domain: { type: "string", description: "Domain slug" },
          name: { type: "string", description: "Concept name (e.g., 'cloud-run', 'base-model')" },
        },
        required: ["domain", "name"],
      },
      handler: async (args) => {
        const domain = args["domain"] as string;
        const name = args["name"] as string;
        const { content, meta } = await kb.getConcept(domain, name);
        const header = `<!-- KB Concept: ${domain}/${name} | confidence: ${meta.confidence ?? "N/A"} | path: ${meta.path} -->\n\n`;
        return { content: [{ type: "text", text: header + content }] };
      },
    },

    {
      name: "kb_read_pattern",
      description:
        "Read full content of a pattern (applied solution recipe, max ~200 lines). Patterns combine concepts to solve specific problems.",
      inputSchema: {
        type: "object",
        properties: {
          domain: { type: "string", description: "Domain slug" },
          name: { type: "string", description: "Pattern name (e.g., 'llm-output-validation')" },
        },
        required: ["domain", "name"],
      },
      handler: async (args) => {
        const domain = args["domain"] as string;
        const name = args["name"] as string;
        const { content, meta } = await kb.getPattern(domain, name);
        const header = `<!-- KB Pattern: ${domain}/${name} | path: ${meta.path} -->\n\n`;
        return { content: [{ type: "text", text: header + content }] };
      },
    },

    {
      name: "kb_quick_reference",
      description:
        "Get the quick-reference cheatsheet for a domain (≤100 lines). Best entry point when you need a fast overview before diving deep.",
      inputSchema: {
        type: "object",
        properties: {
          domain: { type: "string", description: "Domain slug" },
        },
        required: ["domain"],
      },
      handler: async (args) => {
        const domain = args["domain"] as string;
        const content = await kb.getQuickReference(domain);
        const header = `<!-- KB Quick Reference: ${domain} -->\n\n`;
        return { content: [{ type: "text", text: header + content }] };
      },
    },
  ];
}
