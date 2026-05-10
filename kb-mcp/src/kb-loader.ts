// =============================================================================
// kb-loader.ts — Carrega e indexa Knowledge Base a partir de _index.yaml
// =============================================================================
// Lê .claude/kb/_index.yaml e expõe API para listar domínios, ler concepts,
// patterns e quick-references. Cache em memória com invalidação por mtime.
// =============================================================================

import { readFile, stat } from "node:fs/promises";
import { join, resolve } from "node:path";
import { parse as parseYaml } from "yaml";

export interface KBLimits {
  quick_reference: number;
  concept: number;
  pattern: number;
  spec: number | null;
  reference: number | null;
}

export interface KBConcept {
  name: string;
  path: string;
  confidence?: number;
}

export interface KBPattern {
  name: string;
  path: string;
}

export interface KBSpec {
  name: string;
  path: string;
}

export interface KBDomain {
  slug: string;
  name: string;
  description: string;
  path: string;
  mcp_validated?: string;
  entry_points: {
    index?: string;
    quick_reference?: string;
  };
  concepts: KBConcept[];
  patterns: KBPattern[];
  specs: KBSpec[];
}

export interface KBIndex {
  version: string;
  last_updated: string;
  limits: KBLimits;
  domains: Record<string, KBDomain>;
}

export class KBLoader {
  private index: KBIndex | null = null;
  private indexMtime: number = 0;
  private fileCache = new Map<string, { content: string; mtime: number }>();

  constructor(private kbRoot: string) {
    this.kbRoot = resolve(kbRoot);
  }

  /**
   * Carrega ou recarrega o _index.yaml se modificado desde último load.
   */
  async getIndex(): Promise<KBIndex> {
    const indexPath = join(this.kbRoot, "_index.yaml");
    let stats;
    try {
      stats = await stat(indexPath);
    } catch (e) {
      throw new Error(`KB index not found at ${indexPath}: ${(e as Error).message}`);
    }

    const currentMtime = stats.mtimeMs;
    if (this.index && currentMtime === this.indexMtime) {
      return this.index;
    }

    const content = await readFile(indexPath, "utf-8");
    const raw = parseYaml(content) as Omit<KBIndex, "domains"> & {
      domains: Record<string, Omit<KBDomain, "slug">>;
    };

    // Normaliza: injeta slug em cada domain
    const domains: Record<string, KBDomain> = {};
    for (const [slug, meta] of Object.entries(raw.domains || {})) {
      domains[slug] = {
        slug,
        name: meta.name || slug,
        description: meta.description || "",
        path: meta.path || `${slug}/`,
        mcp_validated: meta.mcp_validated,
        entry_points: meta.entry_points || {},
        concepts: meta.concepts || [],
        patterns: meta.patterns || [],
        specs: meta.specs || [],
      };
    }

    this.index = { ...raw, domains };
    this.indexMtime = currentMtime;
    return this.index;
  }

  /**
   * Lista todos os domínios com metadata sucinta.
   */
  async listDomains(): Promise<Array<{ slug: string; name: string; description: string; mcp_validated?: string; counts: { concepts: number; patterns: number; specs: number } }>> {
    const idx = await this.getIndex();
    return Object.values(idx.domains).map((d) => ({
      slug: d.slug,
      name: d.name,
      description: d.description,
      mcp_validated: d.mcp_validated,
      counts: {
        concepts: d.concepts.length,
        patterns: d.patterns.length,
        specs: d.specs.length,
      },
    }));
  }

  /**
   * Retorna metadata completa de um domínio.
   */
  async getDomain(slug: string): Promise<KBDomain> {
    const idx = await this.getIndex();
    const domain = idx.domains[slug];
    if (!domain) {
      throw new Error(`Domain not found: '${slug}'. Available: ${Object.keys(idx.domains).join(", ")}`);
    }
    return domain;
  }

  /**
   * Lê conteúdo de um arquivo do KB com cache.
   */
  private async readKBFile(domainSlug: string, relativePath: string): Promise<string> {
    const domain = await this.getDomain(domainSlug);
    const fullPath = resolve(this.kbRoot, domain.path, relativePath);

    // Sandboxing: garante que está dentro de kbRoot
    if (!fullPath.startsWith(this.kbRoot)) {
      throw new Error(`Path outside KB root not allowed: ${relativePath}`);
    }

    let stats;
    try {
      stats = await stat(fullPath);
    } catch (e) {
      throw new Error(`File not found: ${domainSlug}/${relativePath}`);
    }

    const cached = this.fileCache.get(fullPath);
    if (cached && cached.mtime === stats.mtimeMs) {
      return cached.content;
    }

    const content = await readFile(fullPath, "utf-8");
    this.fileCache.set(fullPath, { content, mtime: stats.mtimeMs });
    return content;
  }

  /**
   * Lê quick reference do domínio.
   */
  async getQuickReference(slug: string): Promise<string> {
    const domain = await this.getDomain(slug);
    const path = domain.entry_points.quick_reference;
    if (!path) {
      throw new Error(`Domain '${slug}' has no quick_reference defined in _index.yaml`);
    }
    return this.readKBFile(slug, path);
  }

  /**
   * Lê index.md do domínio.
   */
  async getDomainIndex(slug: string): Promise<string> {
    const domain = await this.getDomain(slug);
    const path = domain.entry_points.index || "index.md";
    return this.readKBFile(slug, path);
  }

  /**
   * Lê um concept específico.
   */
  async getConcept(domainSlug: string, conceptName: string): Promise<{ content: string; meta: KBConcept }> {
    const domain = await this.getDomain(domainSlug);
    const concept = domain.concepts.find((c) => c.name === conceptName);
    if (!concept) {
      throw new Error(
        `Concept '${conceptName}' not found in '${domainSlug}'. Available: ${domain.concepts.map((c) => c.name).join(", ")}`
      );
    }
    const content = await this.readKBFile(domainSlug, concept.path);
    return { content, meta: concept };
  }

  /**
   * Lê um pattern específico.
   */
  async getPattern(domainSlug: string, patternName: string): Promise<{ content: string; meta: KBPattern }> {
    const domain = await this.getDomain(domainSlug);
    const pattern = domain.patterns.find((p) => p.name === patternName);
    if (!pattern) {
      throw new Error(
        `Pattern '${patternName}' not found in '${domainSlug}'. Available: ${domain.patterns.map((p) => p.name).join(", ")}`
      );
    }
    const content = await this.readKBFile(domainSlug, pattern.path);
    return { content, meta: pattern };
  }

  /**
   * Busca por keywords em concepts e patterns de todos os domínios.
   * Retorna até `limit` matches ordenados por relevância (count de hits).
   */
  async search(
    query: string,
    options: { limit?: number; domain?: string; type?: "concept" | "pattern" | "all" } = {}
  ): Promise<Array<{ domain: string; type: "concept" | "pattern"; name: string; path: string; score: number; snippet: string }>> {
    const { limit = 10, domain: domainFilter, type = "all" } = options;
    const idx = await this.getIndex();
    const keywords = query.toLowerCase().split(/\s+/).filter((k) => k.length > 1);
    if (keywords.length === 0) return [];

    const results: Array<{ domain: string; type: "concept" | "pattern"; name: string; path: string; score: number; snippet: string }> = [];

    for (const domain of Object.values(idx.domains)) {
      if (domainFilter && domain.slug !== domainFilter) continue;

      const items: Array<{ kind: "concept" | "pattern"; meta: KBConcept | KBPattern }> = [];
      if (type === "all" || type === "concept") {
        items.push(...domain.concepts.map((c) => ({ kind: "concept" as const, meta: c })));
      }
      if (type === "all" || type === "pattern") {
        items.push(...domain.patterns.map((p) => ({ kind: "pattern" as const, meta: p })));
      }

      for (const item of items) {
        let content = "";
        try {
          content = await this.readKBFile(domain.slug, item.meta.path);
        } catch {
          continue;
        }
        const lower = content.toLowerCase();
        let score = 0;
        for (const kw of keywords) {
          // Pondera matches em headers (linhas com #) mais alto
          const headerMatches = (lower.match(new RegExp(`^#{1,6}.*${kw}`, "gm")) || []).length;
          const bodyMatches = (lower.split(kw).length - 1) - headerMatches;
          score += headerMatches * 3 + bodyMatches;
          // Bonus se nome bate
          if (item.meta.name.toLowerCase().includes(kw)) score += 5;
        }
        if (score > 0) {
          // Snippet: primeira ocorrência da primeira keyword
          const firstKw = keywords[0]!;
          const firstIdx = lower.indexOf(firstKw);
          const snippetStart = Math.max(0, firstIdx - 50);
          const snippetEnd = Math.min(content.length, firstIdx + 150);
          const snippet = content.substring(snippetStart, snippetEnd).replace(/\s+/g, " ").trim();

          results.push({
            domain: domain.slug,
            type: item.kind,
            name: item.meta.name,
            path: item.meta.path,
            score,
            snippet: `…${snippet}…`,
          });
        }
      }
    }

    return results.sort((a, b) => b.score - a.score).slice(0, limit);
  }
}
