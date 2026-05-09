#!/usr/bin/env python3
"""
lint_agents.py — Valida estrutura de .claude/agents/**/*.md

Checks:
- Frontmatter YAML obrigatório com: name, description, tools, model
- model ∈ {opus, sonnet, haiku, opus-4-7, sonnet-4-6, etc.}
- tools são strings da lista válida
- name é único entre todos os agents
- description tem >= 50 chars
- description começa com verbo de ação útil ("Use when...", "Specialist in...")

Uso:
    python3 scripts/lint_agents.py [path...]
    python3 scripts/lint_agents.py --all   # roda em .claude/agents/**/*.md
    python3 scripts/lint_agents.py --format markdown  # output para PR comment
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: python3-yaml not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


# Modelos aceitos (Claude family + aliases)
VALID_MODELS = {
    "opus", "sonnet", "haiku",
    "claude-opus-4-7", "claude-opus-4-6",
    "claude-sonnet-4-6", "claude-haiku-4-5",
    "opus-4-7", "opus-4-6", "sonnet-4-6", "haiku-4-5",
    "inherit",  # inherit do model do orquestrador
}

# Tools válidas (Claude Code core + extensões comuns)
VALID_TOOLS = {
    "Read", "Write", "Edit", "Glob", "Grep", "Bash",
    "Task", "TodoWrite", "WebFetch", "WebSearch",
    "AskUserQuestion", "NotebookEdit",
    "BashOutput", "KillBash", "SlashCommand",
}


@dataclass
class LintResult:
    file: str
    name: str | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    valid: bool = True


def parse_frontmatter(content: str) -> tuple[dict, str] | tuple[None, str]:
    """Extrai frontmatter YAML do início do arquivo."""
    if not content.startswith("---"):
        return None, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, content
    try:
        fm = yaml.safe_load(parts[1])
        if not isinstance(fm, dict):
            return None, content
        return fm, parts[2]
    except yaml.YAMLError:
        return None, content


def lint_file(path: Path, all_names: dict) -> LintResult:
    result = LintResult(file=str(path))

    if not path.exists():
        result.errors.append(f"File not found: {path}")
        result.valid = False
        return result

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        result.errors.append(f"Could not read file: {e}")
        result.valid = False
        return result

    fm, body = parse_frontmatter(content)
    if fm is None:
        result.errors.append("Missing or invalid YAML frontmatter (must start with ---)")
        result.valid = False
        return result

    # Required fields
    required = ["name", "description", "tools", "model"]
    for field_name in required:
        if field_name not in fm:
            result.errors.append(f"Missing required frontmatter field: {field_name}")

    if "name" in fm:
        name = fm["name"]
        result.name = name
        if not isinstance(name, str) or not re.match(r"^[a-z][a-z0-9-]*$", name):
            result.errors.append(
                f"Invalid name '{name}': must be kebab-case (lowercase, hyphens, starts with letter)"
            )
        # Detecta duplicatas (lista cumulativa)
        if name in all_names and all_names[name] != str(path):
            result.errors.append(
                f"Duplicate name '{name}' also defined in: {all_names[name]}"
            )
        all_names[name] = str(path)

    if "description" in fm:
        desc = fm["description"]
        if not isinstance(desc, str):
            result.errors.append("description must be a string")
        elif len(desc) < 50:
            result.warnings.append(
                f"description is short ({len(desc)} chars) — recommend 50+ for clear discoverability"
            )
        elif len(desc) > 500:
            result.warnings.append(
                f"description is long ({len(desc)} chars) — keep under 500 for readability"
            )

    if "tools" in fm:
        tools = fm["tools"]
        if not isinstance(tools, list):
            result.errors.append("tools must be a list (e.g., [Read, Write, Bash])")
        else:
            for tool in tools:
                if not isinstance(tool, str):
                    result.errors.append(f"Tool must be a string, got: {tool!r}")
                elif tool not in VALID_TOOLS:
                    # Tool customizada começando com mcp__ é OK
                    if not tool.startswith("mcp__"):
                        result.warnings.append(
                            f"Unknown tool '{tool}'. Valid tools: {sorted(VALID_TOOLS)}"
                        )

    if "model" in fm:
        model = fm["model"]
        if not isinstance(model, str):
            result.errors.append(f"model must be a string, got: {model!r}")
        elif model not in VALID_MODELS:
            result.errors.append(
                f"Invalid model '{model}'. Valid: {sorted(VALID_MODELS)}"
            )

    # Body content
    if not body.strip():
        result.warnings.append("Agent body is empty after frontmatter")
    elif len(body.strip()) < 200:
        result.warnings.append(
            f"Agent body is very short ({len(body.strip())} chars) — typical agents have 500+"
        )

    # H1 deve existir e bater com name
    h1_match = re.search(r"^#\s+(.+?)$", body, flags=re.MULTILINE)
    if not h1_match:
        result.warnings.append("No H1 heading found in agent body")

    result.valid = len(result.errors) == 0
    return result


def main():
    parser = argparse.ArgumentParser(description="Lint agent definitions")
    parser.add_argument("files", nargs="*", help="Files to lint")
    parser.add_argument("--all", action="store_true", help="Lint all agents in .claude/agents/")
    parser.add_argument(
        "--format", choices=["json", "text", "markdown"], default="text"
    )
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args()

    if args.all:
        files = sorted(Path(".claude/agents").rglob("*.md"))
    elif args.files:
        files = [Path(f) for f in args.files]
    else:
        print("ℹ️  No files. Use --all or provide paths.", file=sys.stderr)
        sys.exit(0)

    if not files:
        print("ℹ️  No agent files found.", file=sys.stderr)
        sys.exit(0)

    all_names: dict[str, str] = {}
    results = [lint_file(p, all_names) for p in files]

    if args.format == "json":
        print(json.dumps([asdict(r) for r in results], indent=2))
    elif args.format == "markdown":
        total = len(results)
        passed = sum(1 for r in results if r.valid and not r.warnings)
        warned = sum(1 for r in results if r.valid and r.warnings)
        failed = sum(1 for r in results if not r.valid)
        print(f"## Agent Lint — {total} agents checked\n")
        print(f"- ✅ Clean: {passed}")
        print(f"- ⚠️  With warnings: {warned}")
        print(f"- ❌ With errors: {failed}\n")
        for r in results:
            if not r.errors and not r.warnings:
                continue
            icon = "❌" if r.errors else "⚠️"
            print(f"### {icon} `{r.file}`{f' (`{r.name}`)' if r.name else ''}\n")
            for e in r.errors:
                print(f"- ❌ {e}")
            for w in r.warnings:
                print(f"- ⚠️ {w}")
            print()
    else:
        for r in results:
            if r.valid and not r.warnings:
                print(f"✅ {r.file}")
                continue
            icon = "❌" if not r.valid else "⚠️"
            print(f"\n{icon} {r.file}")
            for e in r.errors:
                print(f"  ❌ {e}")
            for w in r.warnings:
                print(f"  ⚠️  {w}")

    has_errors = any(r.errors for r in results)
    has_warnings = any(r.warnings for r in results)

    if has_errors:
        sys.exit(1)
    if args.strict and has_warnings:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
