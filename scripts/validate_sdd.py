#!/usr/bin/env python3
"""
validate_sdd.py — Valida artefatos SDD (DEFINE, DESIGN, BUILD_REPORT)

Uso:
    python3 scripts/validate_sdd.py <file_path>...
    python3 scripts/validate_sdd.py --pr <pr_number> --repo <owner/name>

Saída:
    - JSON estruturado com {file, kind, errors, warnings, clarity_score}
    - Exit code 0 se tudo válido, 1 se erros, 2 se warnings only

Tipos detectados:
    - DEFINE: arquivo começa com "# DEFINE:"
    - DESIGN: arquivo começa com "# DESIGN:"
    - BUILD_REPORT: arquivo começa com "# BUILD REPORT:"
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Literal


@dataclass
class ValidationResult:
    file: str
    kind: Literal["DEFINE", "DESIGN", "BUILD_REPORT", "UNKNOWN"]
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    clarity_score: int | None = None
    clarity_max: int = 14
    valid: bool = True


# Marcadores de placeholder não preenchido
# Qualquer texto entre {...} ou linha que é majoritariamente placeholders
PLACEHOLDER_PATTERN = re.compile(r"\{[^{}]+\}")


def is_placeholder(text: str) -> bool:
    """Retorna True se o texto é apenas placeholder(s) não preenchido(s)."""
    if not text or len(text.strip()) < 3:
        return True
    cleaned = text.strip()
    # Remove qualquer placeholder {...}
    without_placeholders = PLACEHOLDER_PATTERN.sub("", cleaned).strip()
    # Remove asteriscos de bold (e.g., "**MUST**")
    without_placeholders = re.sub(r"\*+", "", without_placeholders).strip()
    # Se sobrou pouquíssimo texto, era basicamente um placeholder
    if len(without_placeholders) < 3:
        return True
    # Heurística: se >50% do texto é placeholder, considera placeholder
    placeholder_chars = sum(len(m.group(0)) for m in PLACEHOLDER_PATTERN.finditer(cleaned))
    if placeholder_chars > 0 and placeholder_chars / len(cleaned) > 0.5:
        return True
    return False


def detect_kind(content: str) -> str:
    """Detecta tipo do artefato pelo H1."""
    first_line = content.lstrip().split("\n", 1)[0].strip()
    if first_line.startswith("# DEFINE:") or first_line.startswith("# DEFINE "):
        return "DEFINE"
    if first_line.startswith("# DESIGN:") or first_line.startswith("# DESIGN "):
        return "DESIGN"
    if "BUILD REPORT" in first_line.upper() or "BUILD_REPORT" in first_line.upper():
        return "BUILD_REPORT"
    return "UNKNOWN"


def extract_section(content: str, header: str) -> str | None:
    """Extrai conteúdo de uma seção H2 pelo nome do header."""
    pattern = re.compile(
        rf"^##\s+{re.escape(header)}\s*$(.*?)(?=^##\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(content)
    return match.group(1).strip() if match else None


def has_substantial_content(section: str | None, min_chars: int = 30) -> bool:
    """Verifica se seção tem conteúdo real (não placeholders)."""
    if not section:
        return False
    # Remove blockquotes, separadores, headers menores
    cleaned = re.sub(r"^>.*$", "", section, flags=re.MULTILINE)
    cleaned = re.sub(r"^---+$", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^\*\*Priority Guide:\*\*.*", "", cleaned, flags=re.MULTILINE | re.DOTALL)
    # Remove placeholders {...}
    cleaned = PLACEHOLDER_PATTERN.sub("", cleaned)
    cleaned = cleaned.strip()
    return len(cleaned) >= min_chars


def count_table_rows(section: str | None, exclude_header: bool = True) -> int:
    """Conta linhas de uma tabela markdown (excluindo header e separator)."""
    if not section:
        return 0
    lines = [l for l in section.split("\n") if l.strip().startswith("|") and l.strip().endswith("|")]
    # Remove header (linha 1) e separator (linha 2 com ---)
    if exclude_header:
        lines = [l for l in lines if not re.match(r"^\|\s*[-:|\s]+\|\s*$", l)]
        # Primeira linha é header
        lines = lines[1:] if lines else []
    # Filtra linhas com placeholders
    real_rows = [l for l in lines if not all(is_placeholder(c.strip()) for c in l.split("|")[1:-1])]
    return len(real_rows)


def count_checklist_items(section: str | None, real_only: bool = True) -> int:
    """Conta itens de checklist `- [ ]` ou `- [x]` na seção."""
    if not section:
        return 0
    items = re.findall(r"^[\s-]*\[[ xX]\]\s+(.*?)$", section, flags=re.MULTILINE)
    if real_only:
        items = [i for i in items if not is_placeholder(i)]
    return len(items)


def count_bullet_items(section: str | None, real_only: bool = True) -> int:
    """Conta bullets `-` ou `*` na seção (excluindo checklists)."""
    if not section:
        return 0
    items = re.findall(r"^\s*[-*]\s+(?!\[)(.+?)$", section, flags=re.MULTILINE)
    if real_only:
        items = [i for i in items if not is_placeholder(i)]
    return len(items)


# =============================================================================
# Validators por tipo
# =============================================================================


def validate_define(content: str, result: ValidationResult) -> None:
    """Valida DEFINE_*.md e calcula Clarity Score."""
    score = 0

    # Required sections
    required_sections = [
        "Problem Statement",
        "Target Users",
        "Goals",
        "Success Criteria",
        "Acceptance Tests",
        "Out of Scope",
    ]
    for section in required_sections:
        content_section = extract_section(content, section)
        if content_section is None:
            result.errors.append(f"Missing required section: ## {section}")
            continue

        # Validações específicas + scoring
        if section == "Problem Statement":
            if has_substantial_content(content_section, min_chars=50):
                score += 2
            else:
                result.errors.append("Problem Statement is empty or only placeholders")

        elif section == "Target Users":
            rows = count_table_rows(content_section)
            if rows >= 1:
                score += 2
                if rows < 2:
                    result.warnings.append("Target Users has only 1 user — consider 2+ personas")
            else:
                result.errors.append("Target Users table has no real rows")

        elif section == "Goals":
            if "**MUST**" in content_section and not all(
                is_placeholder(line.split("|")[2] if len(line.split("|")) > 2 else "")
                for line in content_section.split("\n")
                if "MUST" in line
            ):
                score += 2
            else:
                result.errors.append("Goals must include at least one MUST priority")

        elif section == "Success Criteria":
            items = count_checklist_items(content_section) + count_bullet_items(content_section)
            if items >= 3:
                score += 3
            elif items >= 1:
                score += 1
                result.warnings.append(f"Success Criteria has {items} items — recommend 3+")
            else:
                result.errors.append("Success Criteria must have at least 1 measurable item")

        elif section == "Acceptance Tests":
            rows = count_table_rows(content_section)
            if rows >= 3:
                score += 3
            elif rows >= 1:
                score += 1
                result.warnings.append(f"Acceptance Tests has {rows} tests — recommend 3+ (happy/error/edge)")
            else:
                result.errors.append("Acceptance Tests must have at least 1 test")

        elif section == "Out of Scope":
            items = count_bullet_items(content_section) + count_table_rows(content_section)
            if items >= 2:
                score += 2
            elif items >= 1:
                score += 1
                result.warnings.append(f"Out of Scope has {items} item — recommend 2+ for clarity")
            else:
                result.errors.append("Out of Scope must list at least 1 explicit exclusion")

    result.clarity_score = score
    result.clarity_max = 14

    if score < 12:
        result.errors.append(
            f"Clarity Score {score}/14 below minimum threshold 12. "
            f"Address warnings above to improve."
        )


def validate_design(content: str, result: ValidationResult) -> None:
    """Valida DESIGN_*.md."""
    # Estritamente obrigatórios (presentes em template e exemplos)
    required_sections = [
        "Metadata",
        "Architecture Overview",
        "Components",
        "File Manifest",
    ]
    # Recomendados (no template, mas exemplos variam)
    recommended_sections = [
        "Agent Assignment Rationale",
        "Key Decisions",
        "Testing Strategy",
    ]

    for section in required_sections:
        content_section = extract_section(content, section)
        if content_section is None:
            result.errors.append(f"Missing required section: ## {section}")
        elif not has_substantial_content(content_section, min_chars=50):
            result.errors.append(f"## {section} appears empty or only placeholders")

    for section in recommended_sections:
        if extract_section(content, section) is None:
            result.warnings.append(f"Recommended section missing: ## {section}")

    # File Manifest deve ter tabela ou lista de arquivos
    file_manifest = extract_section(content, "File Manifest")
    if file_manifest:
        files_listed = re.findall(r"`([\w/.\-]+\.[a-z]+)`", file_manifest)
        if not files_listed:
            result.warnings.append(
                "File Manifest has no file paths in backticks — list expected files"
            )

    # Agent matching: warning se nenhum @agent referenciado em todo o doc
    agents = re.findall(r"@[\w-]+", content)
    if not agents:
        result.warnings.append(
            "No @agent references found — declare agents responsible for each component"
        )


def validate_build_report(content: str, result: ValidationResult) -> None:
    """Valida BUILD_REPORT_*.md."""
    # Estritamente obrigatórios (mínimo verificável)
    required_sections = [
        "Summary",
    ]
    # Pelo menos UMA destas deve existir (variantes do framework)
    files_alternatives = ["Files Created", "Files Modified", "File Manifest", "Verification"]
    issues_alternatives = ["Issues Encountered", "Known Limitations", "Open Issues"]
    refs_alternatives = ["KB References", "References", "Documentation Links"]

    for section in required_sections:
        content_section = extract_section(content, section)
        if content_section is None:
            result.errors.append(f"Missing required section: ## {section}")
        elif not has_substantial_content(content_section, min_chars=30):
            result.warnings.append(f"## {section} appears empty")

    # Pelo menos uma alternativa de cada categoria
    for label, alts in [
        ("file tracking", files_alternatives),
        ("issues/limitations", issues_alternatives),
        ("references", refs_alternatives),
    ]:
        if not any(extract_section(content, alt) for alt in alts):
            result.warnings.append(
                f"No {label} section found. Expected one of: {', '.join(alts)}"
            )

    # Agent attribution: warning se nenhum @agent
    agents = re.findall(r"@[\w-]+", content)
    if not agents:
        result.warnings.append(
            "No @agent references — list which agents executed which tasks"
        )


# =============================================================================
# Main
# =============================================================================


def validate_file(path: Path) -> ValidationResult:
    result = ValidationResult(file=str(path), kind="UNKNOWN")
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

    kind = detect_kind(content)
    result.kind = kind  # type: ignore

    if kind == "DEFINE":
        validate_define(content, result)
    elif kind == "DESIGN":
        validate_design(content, result)
    elif kind == "BUILD_REPORT":
        validate_build_report(content, result)
    else:
        result.warnings.append(
            f"File does not match DEFINE/DESIGN/BUILD_REPORT pattern (H1: '{content.lstrip().split(chr(10), 1)[0][:60]}')"
        )

    result.valid = len(result.errors) == 0
    return result


def main():
    parser = argparse.ArgumentParser(description="Validate SDD artifacts")
    parser.add_argument("files", nargs="*", help="Files to validate")
    parser.add_argument(
        "--format",
        choices=["json", "text", "markdown"],
        default="text",
        help="Output format",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )
    args = parser.parse_args()

    if not args.files:
        print("ℹ️  No files to validate.", file=sys.stderr)
        sys.exit(0)

    results: list[ValidationResult] = []
    for f in args.files:
        results.append(validate_file(Path(f)))

    if args.format == "json":
        print(json.dumps([asdict(r) for r in results], indent=2))
    elif args.format == "markdown":
        print("## SDD Artifacts Validation\n")
        for r in results:
            status = "✅" if r.valid and not r.warnings else ("⚠️" if r.valid else "❌")
            print(f"### {status} `{r.file}` ({r.kind})\n")
            if r.clarity_score is not None:
                print(f"**Clarity Score**: {r.clarity_score}/{r.clarity_max}\n")
            if r.errors:
                print("**Errors:**")
                for e in r.errors:
                    print(f"- ❌ {e}")
                print()
            if r.warnings:
                print("**Warnings:**")
                for w in r.warnings:
                    print(f"- ⚠️ {w}")
                print()
            if not r.errors and not r.warnings:
                print("All checks passed.\n")
    else:  # text
        for r in results:
            status = "✅ PASS" if r.valid else "❌ FAIL"
            print(f"\n{status} {r.file} [{r.kind}]")
            if r.clarity_score is not None:
                print(f"  Clarity Score: {r.clarity_score}/{r.clarity_max}")
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
