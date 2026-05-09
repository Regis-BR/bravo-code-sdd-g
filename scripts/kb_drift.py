#!/usr/bin/env python3
"""
kb_drift.py — Detecta KB stale e propõe Issues para revalidação.

Lê .claude/kb/_index.yaml e checa:
- mcp_validated date por domínio (>90 dias = stale)
- Tamanho de arquivos vs limites do _index.yaml (concept ≤150, pattern ≤200, etc.)
- Confidence scores baixos (<0.85)
- Concepts/patterns referenciados no index mas com arquivo missing

Output:
- text/json/markdown
- Lista de Issues sugeridas (1 agregadora por domain)

Uso:
    python3 scripts/kb_drift.py [--format markdown] [--threshold-days 90]
    python3 scripts/kb_drift.py --create-issues --repo owner/name
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timedelta
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


@dataclass
class DomainDrift:
    domain: str
    name: str
    issues: list[str] = field(default_factory=list)
    severity: str = "low"  # low/medium/high
    days_stale: int | None = None


def parse_iso_date(s: str) -> date | None:
    if not s:
        return None
    try:
        return datetime.strptime(s.strip().strip('"').strip("'"), "%Y-%m-%d").date()
    except ValueError:
        return None


def check_file_size(path: Path, max_lines: int) -> int | None:
    """Retorna número de linhas se exceder limite, None se OK."""
    if not path.exists():
        return None
    lines = path.read_text(encoding="utf-8").count("\n") + 1
    return lines if lines > max_lines else None


def analyze(repo_root: Path, threshold_days: int = 90) -> list[DomainDrift]:
    """Analisa _index.yaml e detecta drifts."""
    index_path = repo_root / ".claude" / "kb" / "_index.yaml"
    if not index_path.exists():
        return [DomainDrift(domain="N/A", name="MISSING", issues=["_index.yaml not found"])]

    with open(index_path) as f:
        index = yaml.safe_load(f)

    limits = index.get("limits", {})
    concept_limit = limits.get("concept", 150)
    pattern_limit = limits.get("pattern", 200)
    qref_limit = limits.get("quick_reference", 100)

    domains = index.get("domains", {})
    today = date.today()
    threshold = today - timedelta(days=threshold_days)

    drifts: list[DomainDrift] = []

    for slug, meta in domains.items():
        drift = DomainDrift(domain=slug, name=meta.get("name", slug))
        domain_path = repo_root / ".claude" / "kb" / meta.get("path", f"{slug}/")

        # 1. mcp_validated date
        validated_str = meta.get("mcp_validated", "")
        validated_date = parse_iso_date(validated_str)
        if validated_date is None:
            drift.issues.append(f"mcp_validated date is missing or invalid")
            drift.severity = "high"
        else:
            days_old = (today - validated_date).days
            drift.days_stale = days_old
            if days_old > threshold_days:
                drift.issues.append(
                    f"mcp_validated is {days_old} days old (>{threshold_days} threshold)"
                )
                drift.severity = "high" if days_old > threshold_days * 2 else "medium"

        # 2. File size limits
        for concept_meta in meta.get("concepts", []):
            cpath = domain_path / concept_meta.get("path", "")
            if not cpath.exists():
                drift.issues.append(f"Concept file missing: {concept_meta.get('path')}")
                continue
            over = check_file_size(cpath, concept_limit)
            if over:
                drift.issues.append(
                    f"Concept '{concept_meta.get('name')}' exceeds limit: {over}/{concept_limit} lines"
                )
            # Confidence
            conf = concept_meta.get("confidence")
            if conf is not None and conf < 0.85:
                drift.issues.append(
                    f"Concept '{concept_meta.get('name')}' has low confidence: {conf}"
                )

        for pattern_meta in meta.get("patterns", []):
            ppath = domain_path / pattern_meta.get("path", "")
            if not ppath.exists():
                drift.issues.append(f"Pattern file missing: {pattern_meta.get('path')}")
                continue
            over = check_file_size(ppath, pattern_limit)
            if over:
                drift.issues.append(
                    f"Pattern '{pattern_meta.get('name')}' exceeds limit: {over}/{pattern_limit} lines"
                )

        # 3. Quick reference size
        entry_points = meta.get("entry_points", {})
        if entry_points.get("quick_reference"):
            qref_path = domain_path / entry_points["quick_reference"]
            over = check_file_size(qref_path, qref_limit)
            if over:
                drift.issues.append(
                    f"quick-reference exceeds limit: {over}/{qref_limit} lines"
                )

        if drift.issues:
            drifts.append(drift)

    return drifts


def format_markdown(drifts: list[DomainDrift]) -> str:
    if not drifts:
        return "## ✅ KB Drift Check — All domains healthy\n\nNo drift detected."

    severity_emoji = {"high": "🔴", "medium": "🟠", "low": "🟡"}

    lines = [
        f"## 🔍 KB Drift Check — {len(drifts)} domain(s) need attention",
        "",
        "| Domain | Severity | Issues | Days Stale |",
        "|--------|----------|--------|------------|",
    ]
    for d in drifts:
        emoji = severity_emoji.get(d.severity, "⚪")
        days = f"{d.days_stale}d" if d.days_stale is not None else "N/A"
        lines.append(f"| `{d.domain}` ({d.name}) | {emoji} {d.severity} | {len(d.issues)} | {days} |")

    lines.append("")
    for d in drifts:
        emoji = severity_emoji.get(d.severity, "⚪")
        lines.append(f"### {emoji} `{d.domain}` ({d.name})")
        lines.append("")
        for issue in d.issues:
            lines.append(f"- {issue}")
        lines.append("")
        lines.append(f"**Action**: revalidate via MCP, update `mcp_validated` in `_index.yaml`, or refactor files.")
        lines.append("")

    return "\n".join(lines)


def create_issues(drifts: list[DomainDrift], repo: str):
    """Cria/atualiza Issues no GitHub para cada domain com drift."""
    severity_emoji = {"high": "🔴", "medium": "🟠", "low": "🟡"}
    for d in drifts:
        emoji = severity_emoji.get(d.severity, "⚪")
        title = f"[kb] {emoji} {d.domain} drift detected ({len(d.issues)} issues)"
        body_lines = [
            f"**Domain**: `{d.domain}` ({d.name})",
            f"**Severity**: {d.severity}",
            f"**Days stale**: {d.days_stale if d.days_stale is not None else 'N/A'}",
            "",
            "## Issues detected",
            "",
        ]
        for issue in d.issues:
            body_lines.append(f"- {issue}")
        body_lines.extend(["", "## Action", "",
                           "1. Re-execute MCP validation for this domain",
                           "2. Update `mcp_validated` in `.claude/kb/_index.yaml`",
                           "3. Refactor oversized files into smaller concepts/patterns",
                           "4. Mark this Issue as resolved when all sub-issues addressed",
                           "",
                           f"_Auto-detected by `kb_drift.py` on {date.today().isoformat()}._"])
        body = "\n".join(body_lines)

        # Verifica se Issue já existe (evitar spam)
        check = subprocess.run(
            ["gh", "issue", "list", "--repo", repo, "--state", "open",
             "--label", f"kb-domain:{d.domain}", "--label", "kb-update",
             "--json", "title", "--limit", "20"],
            capture_output=True, text=True
        )
        existing = json.loads(check.stdout) if check.returncode == 0 else []
        already_open = any(d.domain in item.get("title", "") for item in existing)

        if already_open:
            print(f"⏭️  Issue already open for {d.domain} — skipping")
            continue

        labels = ["kb-update", f"kb-domain:{d.domain}", f"severity:{d.severity}"]
        result = subprocess.run(
            ["gh", "issue", "create",
             "--repo", repo,
             "--title", title,
             "--body", body,
             "--label", ",".join(labels)],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"✅ Issue created for {d.domain}: {result.stdout.strip()}")
        else:
            print(f"❌ Failed for {d.domain}: {result.stderr}")


def main():
    parser = argparse.ArgumentParser(description="Detect KB drift")
    parser.add_argument("--format", choices=["text", "json", "markdown"], default="text")
    parser.add_argument("--threshold-days", type=int, default=90)
    parser.add_argument("--create-issues", action="store_true",
                        help="Create GitHub Issues for each drift (requires --repo)")
    parser.add_argument("--repo", help="owner/name (required with --create-issues)")
    parser.add_argument("--repo-root", default=".", help="Path to repo root")
    args = parser.parse_args()

    drifts = analyze(Path(args.repo_root), args.threshold_days)

    if args.format == "json":
        print(json.dumps([asdict(d) for d in drifts], indent=2))
    elif args.format == "markdown":
        print(format_markdown(drifts))
    else:
        if not drifts:
            print("✅ All KB domains healthy")
        else:
            for d in drifts:
                print(f"\n[{d.severity.upper()}] {d.domain} ({d.name})")
                print(f"  Days stale: {d.days_stale}")
                for i in d.issues:
                    print(f"  - {i}")

    if args.create_issues:
        if not args.repo:
            print("ERROR: --repo required with --create-issues", file=sys.stderr)
            sys.exit(2)
        create_issues(drifts, args.repo)

    sys.exit(0 if not drifts else (1 if any(d.severity == "high" for d in drifts) else 0))


if __name__ == "__main__":
    main()
