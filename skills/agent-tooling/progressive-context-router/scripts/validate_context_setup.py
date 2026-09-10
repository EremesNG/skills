#!/usr/bin/env python3
"""Validate a repository's progressive context-routing documentation.

The validator is read-only. It checks entrypoints, links, reachability, routing
cases, placeholder residue, duplicate prose, secret-like content, and selected
repository path references. It intentionally leaves architectural judgment to
humans and agents.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import re
import sys
import urllib.parse
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

VERSION = "1.0.0"
DEFAULT_ENTRYPOINTS = ["AGENTS.md", "CLAUDE.md", ".github/copilot-instructions.md"]
SECRET_PATTERNS = [
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("OpenAI-style secret", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("assignment containing a credential-like value", re.compile(r"(?i)\b(?:password|passwd|api[_-]?key|secret|token)\s*[:=]\s*['\"]?[^\s<'\"]{12,}")),
]
PLACEHOLDER_WORDS = {
    "path",
    "command",
    "domain",
    "subsystem",
    "feature words, concepts",
    "verified command",
    "tests",
    "overlay or none",
    "condition",
    "paths",
    "terms",
    "uncertain fact",
    "prerequisite",
    "module",
    "flow name",
    "one paragraph describing what the repository delivers and its major runtime shape.",
}
PATH_PREFIXES = (
    "src/",
    "app/",
    "apps/",
    "lib/",
    "libs/",
    "packages/",
    "services/",
    "modules/",
    "tests/",
    "test/",
    "spec/",
    "specs/",
    "docs/",
    "migrations/",
    "scripts/",
    "config/",
    ".github/",
    ".cursor/",
)


@dataclass
class Issue:
    severity: str
    code: str
    message: str
    path: Optional[str] = None
    line: Optional[int] = None


@dataclass
class Metrics:
    path: str
    lines: int
    nonblank_lines: int
    words: int
    characters: int
    estimated_tokens: int


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate progressive repository context routing.")
    parser.add_argument("--root", default=".", help="Repository root (default: current directory).")
    parser.add_argument("--docs-dir", default="docs/agent", help="Agent documentation directory.")
    parser.add_argument(
        "--entrypoint",
        action="append",
        dest="entrypoints",
        help="Always-loaded entrypoint path; repeat for multiple files. Auto-detected when omitted.",
    )
    parser.add_argument(
        "--routing-cases",
        default="docs/agent/routing-cases.json",
        help="Routing cases JSON path.",
    )
    parser.add_argument("--json", action="store_true", help="Print a JSON report.")
    parser.add_argument("--strict", action="store_true", help="Return exit code 2 when warnings remain.")
    parser.add_argument("--no-path-check", action="store_true", help="Skip inline repository-path checks.")
    parser.add_argument("--version", action="version", version=VERSION)
    return parser.parse_args(argv)


def relative_str(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        return str(path)


def read_text(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def compute_metrics(path: Path, root: Path) -> Optional[Metrics]:
    text = read_text(path)
    if text is None:
        return None
    lines = text.splitlines()
    chars = len(text)
    return Metrics(
        path=relative_str(root, path),
        lines=len(lines),
        nonblank_lines=sum(1 for line in lines if line.strip()),
        words=len(re.findall(r"\S+", text)),
        characters=chars,
        estimated_tokens=math.ceil(chars / 4),
    )


def markdown_files(entrypoints: Sequence[Path], docs_dir: Path) -> List[Path]:
    result = [path for path in entrypoints if path.is_file()]
    if docs_dir.is_dir():
        result.extend(sorted(docs_dir.rglob("*.md")))
        result.extend(sorted(docs_dir.rglob("*.mdx")))
    deduped: List[Path] = []
    seen: Set[Path] = set()
    for path in result:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            deduped.append(path)
    return deduped


def extract_markdown_links(text: str) -> Iterable[Tuple[str, int]]:
    pattern = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
    for line_number, line in enumerate(text.splitlines(), start=1):
        for match in pattern.finditer(line):
            raw = match.group(1).strip()
            if raw.startswith("<") and raw.endswith(">"):
                raw = raw[1:-1]
            # Remove optional Markdown title after the path.
            if " \"" in raw:
                raw = raw.split(" \"", 1)[0]
            elif " '" in raw:
                raw = raw.split(" '", 1)[0]
            yield raw, line_number


def resolve_local_link(source: Path, raw: str, root: Path) -> Optional[Path]:
    lower = raw.lower()
    if not raw or raw.startswith("#") or lower.startswith(("http://", "https://", "mailto:", "data:", "tel:")):
        return None
    target_text = urllib.parse.unquote(raw.split("#", 1)[0].split("?", 1)[0]).strip()
    if not target_text:
        return None
    target = Path(target_text)
    if target.is_absolute():
        try:
            target.resolve().relative_to(root.resolve())
        except (OSError, ValueError):
            return target
        return target
    return (source.parent / target).resolve()


def line_for_pattern(text: str, pattern: re.Pattern[str]) -> Optional[int]:
    for number, line in enumerate(text.splitlines(), start=1):
        if pattern.search(line):
            return number
    return None


def add_secret_issues(path: Path, text: str, root: Path, issues: List[Issue]) -> None:
    for name, pattern in SECRET_PATTERNS:
        match = pattern.search(text)
        if match:
            line = text.count("\n", 0, match.start()) + 1
            issues.append(
                Issue("error", "secret-like-content", f"Possible {name} appears in agent documentation.", relative_str(root, path), line)
            )


def add_placeholder_issues(path: Path, text: str, root: Path, issues: List[Issue]) -> None:
    for number, line in enumerate(text.splitlines(), start=1):
        for match in re.finditer(r"<([^<>\n]{2,100})>", line):
            value = match.group(1).strip().lower()
            if value in PLACEHOLDER_WORDS or any(token in value for token in ("verified", "replace with", "one paragraph", "path or", "feature words")):
                issues.append(
                    Issue("error", "template-placeholder", f"Unresolved template placeholder `<{match.group(1)}>`.", relative_str(root, path), number)
                )


def normalize_paragraph(paragraph: str) -> str:
    value = re.sub(r"\s+", " ", paragraph.strip().lower())
    return value


def duplicate_blocks(files: Sequence[Path], root: Path) -> List[Issue]:
    seen: Dict[str, List[Tuple[str, int, str]]] = collections.defaultdict(list)
    for path in files:
        text = read_text(path)
        if text is None:
            continue
        lines = text.splitlines()
        current: List[str] = []
        start = 1
        blocks: List[Tuple[int, str]] = []
        for idx, line in enumerate(lines + [""], start=1):
            if line.strip():
                if not current:
                    start = idx
                current.append(line)
            elif current:
                paragraph = "\n".join(current)
                blocks.append((start, paragraph))
                current = []
        for line_number, paragraph in blocks:
            stripped = paragraph.lstrip()
            if stripped.startswith(("#", "|", "```")):
                continue
            normalized = normalize_paragraph(paragraph)
            if len(normalized) < 180 or len(normalized.split()) < 25:
                continue
            digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
            seen[digest].append((relative_str(root, path), line_number, normalized[:120]))
    issues: List[Issue] = []
    for locations in seen.values():
        distinct_files = {item[0] for item in locations}
        if len(distinct_files) < 2:
            continue
        first = locations[0]
        others = ", ".join(f"{p}:{line}" for p, line, _ in locations[1:4])
        issues.append(
            Issue(
                "warning",
                "duplicate-prose",
                f"A long paragraph is duplicated in {others}. Keep one canonical owner and link to it.",
                first[0],
                first[1],
            )
        )
        if len(issues) >= 10:
            break
    return issues


def strip_symbol_suffix(value: str) -> str:
    # Preserve Windows drive letters; remove common path:symbol or path:line suffixes.
    if re.match(r"^[A-Za-z]:[\\/]", value):
        return value
    match = re.match(r"^(.+?\.[A-Za-z0-9]{1,8}):(?:[A-Za-z_$][\w$.-]*|\d+(?::\d+)?)$", value)
    if match:
        return match.group(1)
    return value


def path_candidates(text: str) -> Iterable[Tuple[str, int]]:
    for number, line in enumerate(text.splitlines(), start=1):
        for match in re.finditer(r"`([^`\n]+)`", line):
            value = match.group(1).strip().strip(".,;()")
            if not value or " " in value or value.startswith(("http://", "https://", "mailto:")):
                continue
            if any(mark in value for mark in ("<", ">", "${", "$(")):
                continue
            value = strip_symbol_suffix(value)
            normalized = value[2:] if value.startswith("./") else value
            if normalized.startswith(PATH_PREFIXES):
                yield normalized, number


def check_inline_paths(path: Path, text: str, root: Path, issues: List[Issue]) -> None:
    reported: Set[Tuple[str, int]] = set()
    for value, line in path_candidates(text):
        key = (value, line)
        if key in reported:
            continue
        reported.add(key)
        if any(ch in value for ch in "*?["):
            root_matches = list(root.glob(value))
            local_matches = list(path.parent.glob(value))
            exists = bool(root_matches or local_matches)
        else:
            exists = (root / value).exists() or (path.parent / value).exists()
        if not exists:
            issues.append(
                Issue("warning", "stale-path", f"Referenced repository path does not exist: `{value}`.", relative_str(root, path), line)
            )
            if sum(1 for issue in issues if issue.code == "stale-path") >= 30:
                return


def validate_routing_cases(path: Path, root: Path, issues: List[Issue]) -> Dict[str, Any]:
    result = {"path": relative_str(root, path), "cases": 0, "present": path.is_file()}
    if not path.is_file():
        issues.append(Issue("warning", "routing-cases-missing", "No routing-cases JSON file was found.", result["path"]))
        return result
    text = read_text(path)
    if text is None:
        issues.append(Issue("error", "routing-cases-unreadable", "Routing cases file cannot be read.", result["path"]))
        return result
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        issues.append(Issue("error", "routing-cases-json", f"Invalid JSON: {exc.msg}.", result["path"], exc.lineno))
        return result
    cases = data.get("cases") if isinstance(data, dict) else None
    if not isinstance(cases, list):
        issues.append(Issue("error", "routing-cases-schema", "Expected a top-level `cases` array.", result["path"]))
        return result
    ids: Set[str] = set()
    for index, case in enumerate(cases):
        label = f"case {index + 1}"
        if not isinstance(case, dict):
            issues.append(Issue("error", "routing-case-schema", f"{label} is not an object.", result["path"]))
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            issues.append(Issue("error", "routing-case-id", f"{label} has no non-empty `id`.", result["path"]))
        elif case_id in ids:
            issues.append(Issue("error", "routing-case-id", f"Duplicate routing case id `{case_id}`.", result["path"]))
        else:
            ids.add(case_id)
        for field in ("task", "expected_primary", "expected_first_read"):
            if not isinstance(case.get(field), str) or not case[field].strip():
                issues.append(Issue("error", "routing-case-field", f"{label} has no non-empty `{field}`.", result["path"]))
        first_read = case.get("expected_first_read")
        if isinstance(first_read, str) and first_read and not any(ch in first_read for ch in "<>*"):
            if not (root / first_read).exists():
                issues.append(
                    Issue("error", "routing-case-target", f"{label} points to missing first-read file `{first_read}`.", result["path"])
                )
        code_roots = case.get("expected_code_roots", [])
        if code_roots is not None and not isinstance(code_roots, list):
            issues.append(Issue("error", "routing-case-field", f"{label} `expected_code_roots` must be an array.", result["path"]))
        elif isinstance(code_roots, list):
            for candidate in code_roots:
                if isinstance(candidate, str) and candidate and not any(ch in candidate for ch in "<>*"):
                    if not (root / candidate).exists():
                        issues.append(
                            Issue("warning", "routing-case-path", f"{label} references missing code root `{candidate}`.", result["path"])
                        )
    result["cases"] = len(cases)
    if len(cases) < 3:
        issues.append(Issue("warning", "routing-case-coverage", "Fewer than three routing cases are defined.", result["path"]))
    return result


def total_metrics(metrics: Sequence[Metrics]) -> Dict[str, int]:
    return {
        "files": len(metrics),
        "lines": sum(item.lines for item in metrics),
        "nonblank_lines": sum(item.nonblank_lines for item in metrics),
        "words": sum(item.words for item in metrics),
        "characters": sum(item.characters for item in metrics),
        "estimated_tokens": sum(item.estimated_tokens for item in metrics),
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"error: repository root is not a directory: {root}", file=sys.stderr)
        return 2

    docs_dir = root / args.docs_dir
    if args.entrypoints:
        entrypoint_paths = [root / value for value in args.entrypoints]
    else:
        entrypoint_paths = [root / value for value in DEFAULT_ENTRYPOINTS if (root / value).is_file()]

    issues: List[Issue] = []
    if not entrypoint_paths:
        issues.append(Issue("error", "entrypoint-missing", "No root agent instruction entrypoint was found."))
    for path in entrypoint_paths:
        if not path.is_file():
            issues.append(Issue("error", "entrypoint-missing", "Configured entrypoint does not exist.", relative_str(root, path)))

    index = docs_dir / "index.md"
    if not index.is_file():
        issues.append(Issue("error", "router-missing", "Required context router `index.md` was not found.", relative_str(root, index)))

    files = markdown_files(entrypoint_paths, docs_dir)
    metrics: List[Metrics] = []
    graph: Dict[str, Set[str]] = collections.defaultdict(set)
    docs_root_resolved = docs_dir.resolve()

    for path in files:
        text = read_text(path)
        if text is None:
            issues.append(Issue("error", "unreadable", "Markdown file cannot be read.", relative_str(root, path)))
            continue
        metric = compute_metrics(path, root)
        if metric:
            metrics.append(metric)
            if path in entrypoint_paths:
                if metric.nonblank_lines > 200:
                    issues.append(
                        Issue("warning", "entrypoint-large", f"Always-loaded entrypoint has {metric.nonblank_lines} nonblank lines; review domain detail for routing.", metric.path)
                    )
                elif metric.nonblank_lines > 150:
                    issues.append(
                        Issue("info", "entrypoint-size", f"Always-loaded entrypoint has {metric.nonblank_lines} nonblank lines; confirm each section earns its cost.", metric.path)
                    )
        add_secret_issues(path, text, root, issues)
        add_placeholder_issues(path, text, root, issues)
        if not args.no_path_check:
            check_inline_paths(path, text, root, issues)

        source_rel = relative_str(root, path)
        for raw, line in extract_markdown_links(text):
            target = resolve_local_link(path, raw, root)
            if target is None:
                continue
            target_rel = relative_str(root, target)
            graph[source_rel].add(target_rel)
            try:
                target.resolve().relative_to(root.resolve())
            except (OSError, ValueError):
                issues.append(Issue("warning", "external-file-link", f"Local link points outside the repository: `{raw}`.", source_rel, line))
                continue
            if not target.exists():
                issues.append(Issue("error", "broken-link", f"Broken local link: `{raw}`.", source_rel, line))

        if path in entrypoint_paths:
            lower = text.lower()
            if "docs/agent/index.md" not in lower and "docs/agent/" not in lower:
                issues.append(Issue("error", "router-not-linked", "Entrypoint does not direct agents to `docs/agent/index.md`.", source_rel))
            protocol_terms = [
                bool(re.search(r"\b(classif|clasific)", lower)),
                bool(re.search(r"\b(search|buscar|busca)", lower)),
                bool(re.search(r"\b(test|prueba)", lower)),
                bool(re.search(r"\b(smallest|minim|mínim|expand|ampli)", lower)),
            ]
            if sum(protocol_terms) < 3:
                issues.append(Issue("warning", "weak-reading-protocol", "Entrypoint may not clearly describe progressive search, tests, and context expansion.", source_rel))
            import_lines = [
                line for line in text.splitlines() if re.match(r"^\s*@(?:\.?/?docs/agent/)", line)
            ]
            if len(import_lines) > 2:
                issues.append(Issue("warning", "bulk-import", f"Entrypoint contains {len(import_lines)} direct imports from docs/agent; this may defeat on-demand loading.", source_rel))
            if re.search(r"(?i)\b(read|scan|load|lee|carga|escanea)\b.{0,30}\b(all|entire|every|todos?|completo)\b.{0,30}\b(docs?|repository|repo|archivos?)\b", text):
                issues.append(Issue("warning", "read-everything", "Entrypoint appears to instruct broad reading; confirm that this is not the default workflow.", source_rel))

    if index.is_file():
        index_text = read_text(index) or ""
        index_rel = relative_str(root, index)
        if not re.search(r"(?m)^\s*\|[^\n]*\|[^\n]*\|[^\n]*\|", index_text):
            issues.append(Issue("warning", "route-structure", "Router has no clear multi-column route table.", index_rel))
        lower = index_text.lower()
        if not re.search(r"fallback|unknown|unfamiliar|desconocid|sin ruta|no route", lower):
            issues.append(Issue("error", "fallback-missing", "Router does not define fallback behavior for unfamiliar tasks.", index_rel))
        if not re.search(r"test|prueba", lower):
            issues.append(Issue("warning", "tests-not-routed", "Router does not appear to route tasks toward related tests.", index_rel))
        if not re.search(r"overlay|transversal|cross-cutting|prece|prioridad", lower):
            issues.append(Issue("warning", "precedence-missing", "Router may not explain overlays or precedence for overlapping routes.", index_rel))

    # Reachability begins at the router, because on-demand docs should be discoverable there.
    if index.is_file():
        start = relative_str(root, index)
        reachable: Set[str] = set()
        queue = [start]
        while queue:
            node = queue.pop(0)
            if node in reachable:
                continue
            reachable.add(node)
            for target in graph.get(node, set()):
                if target not in reachable:
                    queue.append(target)
        if docs_dir.is_dir():
            for target in sorted(list(docs_dir.rglob("*.md")) + list(docs_dir.rglob("*.mdx")) + list(docs_dir.rglob("*.json"))):
                rel = relative_str(root, target)
                if rel == start:
                    continue
                if rel not in reachable:
                    issues.append(Issue("warning", "unreachable-doc", "Agent context file is not reachable by Markdown links from the router.", rel))

    issues.extend(duplicate_blocks(files, root))
    routing_result = validate_routing_cases(root / args.routing_cases, root, issues)

    entrypoint_metrics = [item for item in metrics if item.path in {relative_str(root, p) for p in entrypoint_paths}]
    docs_metrics = [item for item in metrics if item.path not in {relative_str(root, p) for p in entrypoint_paths}]
    counts = collections.Counter(issue.severity for issue in issues)
    status = "FAIL" if counts["error"] else ("WARN" if counts["warning"] else "PASS")

    report = {
        "schema_version": 1,
        "tool": {"name": "validate_context_setup.py", "version": VERSION},
        "root": str(root),
        "status": status,
        "entrypoints": [relative_str(root, path) for path in entrypoint_paths],
        "router": relative_str(root, index),
        "routing_cases": routing_result,
        "metrics": {
            "always_loaded": total_metrics(entrypoint_metrics),
            "routed_markdown": total_metrics(docs_metrics),
            "files": [asdict(item) for item in metrics],
            "token_note": "Estimated tokens use characters/4 and are not exact model or billing counts.",
        },
        "counts": {"error": counts["error"], "warning": counts["warning"], "info": counts["info"]},
        "issues": [asdict(issue) for issue in issues],
    }

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Context routing validation: {status}")
        print(f"Root: {root}")
        print("Entrypoints: " + (", ".join(report["entrypoints"]) or "none"))
        always = report["metrics"]["always_loaded"]
        routed = report["metrics"]["routed_markdown"]
        print(
            "Always-loaded aggregate: "
            f"{always['files']} files, {always['nonblank_lines']} nonblank lines, "
            f"~{always['estimated_tokens']} estimated tokens"
        )
        print(
            "Routed Markdown aggregate: "
            f"{routed['files']} files, {routed['nonblank_lines']} nonblank lines, "
            f"~{routed['estimated_tokens']} estimated tokens"
        )
        print("Token estimate: characters/4; use only for relative comparison.")
        print(
            f"Issues: {counts['error']} errors, {counts['warning']} warnings, {counts['info']} info"
        )
        if issues:
            print()
            order = {"error": 0, "warning": 1, "info": 2}
            for issue in sorted(issues, key=lambda item: (order[item.severity], item.path or "", item.line or 0, item.code)):
                location = ""
                if issue.path:
                    location = f" {issue.path}"
                    if issue.line:
                        location += f":{issue.line}"
                print(f"[{issue.severity.upper()}] {issue.code}:{location} — {issue.message}")

    if counts["error"]:
        return 1
    if args.strict and counts["warning"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
