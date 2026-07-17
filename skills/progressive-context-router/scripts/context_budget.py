#!/usr/bin/env python3
"""Measure approximate context size for repository agent instructions.

Token counts are deliberately labeled estimates and use characters/4. The
script is intended for before/after comparison, not billing or model limits.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import re
import sys
import urllib.parse
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

VERSION = "1.0.0"
DEFAULT_ENTRYPOINTS = ["AGENTS.md", "CLAUDE.md", ".github/copilot-instructions.md"]


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Measure approximate context size for agent instructions.")
    parser.add_argument("--root", default=".", help="Repository root (default: current directory).")
    parser.add_argument("--docs-dir", default="docs/agent", help="On-demand agent documentation directory.")
    parser.add_argument(
        "--always",
        action="append",
        help="Always-loaded file path; repeat for multiple files. Auto-detected when omitted.",
    )
    parser.add_argument("--router", default="docs/agent/index.md", help="Router document path.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown.")
    parser.add_argument("--snapshot-out", help="Write the JSON measurement to this path.")
    parser.add_argument("--compare", help="Compare against a prior JSON snapshot.")
    parser.add_argument("--version", action="version", version=VERSION)
    return parser.parse_args(argv)


def metrics(path: Path, root: Path) -> Optional[Dict[str, Any]]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    lines = text.splitlines()
    try:
        rel = path.resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        rel = str(path)
    return {
        "path": rel,
        "lines": len(lines),
        "nonblank_lines": sum(1 for line in lines if line.strip()),
        "words": len(re.findall(r"\S+", text)),
        "characters": len(text),
        "estimated_tokens": math.ceil(len(text) / 4),
    }


def sum_metrics(items: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    rows = list(items)
    return {
        "files": len(rows),
        "lines": sum(row["lines"] for row in rows),
        "nonblank_lines": sum(row["nonblank_lines"] for row in rows),
        "words": sum(row["words"] for row in rows),
        "characters": sum(row["characters"] for row in rows),
        "estimated_tokens": sum(row["estimated_tokens"] for row in rows),
    }


def extract_local_links(router: Path, root: Path, docs_dir: Path) -> List[Path]:
    try:
        text = router.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    result: List[Path] = []
    seen: Set[Path] = set()
    for match in re.finditer(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", text):
        raw = match.group(1).strip()
        if raw.startswith(("http://", "https://", "mailto:", "#")):
            continue
        raw = raw.split("#", 1)[0].split("?", 1)[0]
        raw = urllib.parse.unquote(raw)
        target = (router.parent / raw).resolve()
        try:
            target.relative_to(docs_dir.resolve())
        except (OSError, ValueError):
            continue
        if target.is_file() and target not in seen:
            seen.add(target)
            result.append(target)
    return result


def delta(current: Dict[str, int], baseline: Dict[str, int]) -> Dict[str, int]:
    keys = {"files", "lines", "nonblank_lines", "words", "characters", "estimated_tokens"}
    return {key: current.get(key, 0) - baseline.get(key, 0) for key in keys}


def percent_change(current: int, baseline: int) -> Optional[float]:
    if baseline == 0:
        return None
    return ((current - baseline) / baseline) * 100


def build_report(root: Path, always_paths: Sequence[Path], docs_dir: Path, router: Path) -> Dict[str, Any]:
    always_files = [row for path in always_paths if (row := metrics(path, root))]
    router_row = metrics(router, root) if router.is_file() else None

    docs_paths: List[Path] = []
    if docs_dir.is_dir():
        for pattern in ("*.md", "*.mdx", "*.json"):
            docs_paths.extend(docs_dir.rglob(pattern))
    docs_rows = []
    always_resolved = {path.resolve() for path in always_paths if path.exists()}
    for path in sorted(set(docs_paths)):
        if path.resolve() in always_resolved or path.resolve() == router.resolve():
            continue
        row = metrics(path, root)
        if row:
            docs_rows.append(row)

    base_bundle_rows = list(always_files)
    always_metric_paths = {row["path"] for row in always_files}
    if router_row and router_row["path"] not in always_metric_paths:
        base_bundle_rows.append(router_row)
    base_bundle = sum_metrics(base_bundle_rows)

    route_bundles = []
    for target in extract_local_links(router, root, docs_dir):
        target_row = metrics(target, root)
        if not target_row:
            continue
        bundle = sum_metrics([*base_bundle_rows, target_row])
        route_bundles.append(
            {
                "first_read": target_row["path"],
                "bundle": bundle,
                "increment_over_entrypoints": bundle["estimated_tokens"] - sum_metrics(always_files)["estimated_tokens"],
            }
        )

    return {
        "schema_version": 1,
        "tool": {"name": "context_budget.py", "version": VERSION},
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "root": str(root),
        "estimate_method": "ceil(characters / 4) per file",
        "estimate_warning": "Token values are approximate and are not model, billing, or client measurements.",
        "always_loaded": {"files": always_files, "total": sum_metrics(always_files)},
        "router": router_row,
        "on_demand": {"files": docs_rows, "total": sum_metrics(docs_rows)},
        "entrypoints_plus_router": base_bundle,
        "representative_route_bundles": route_bundles,
    }


def compare_report(current: Dict[str, Any], snapshot_path: Path) -> Dict[str, Any]:
    try:
        baseline = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"error": f"Could not read baseline snapshot: {exc}"}
    current_always = current.get("always_loaded", {}).get("total", {})
    baseline_always = baseline.get("always_loaded", {}).get("total", {})
    current_bundle = current.get("entrypoints_plus_router", {})
    baseline_bundle = baseline.get("entrypoints_plus_router", {})
    return {
        "baseline": str(snapshot_path),
        "always_loaded_delta": delta(current_always, baseline_always),
        "entrypoints_plus_router_delta": delta(current_bundle, baseline_bundle),
        "always_loaded_estimated_tokens_percent": percent_change(
            current_always.get("estimated_tokens", 0), baseline_always.get("estimated_tokens", 0)
        ),
        "entrypoints_plus_router_estimated_tokens_percent": percent_change(
            current_bundle.get("estimated_tokens", 0), baseline_bundle.get("estimated_tokens", 0)
        ),
    }


def markdown_table(headers: Sequence[str], rows: Iterable[Sequence[Any]]) -> str:
    rows = list(rows)
    if not rows:
        return "_None._"
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(value).replace("|", "\\|") for value in row) + " |")
    return "\n".join(lines)


def to_markdown(report: Dict[str, Any]) -> str:
    always = report["always_loaded"]["total"]
    on_demand = report["on_demand"]["total"]
    bundle = report["entrypoints_plus_router"]
    lines = [
        "# Agent context budget",
        "",
        f"- Root: `{report['root']}`",
        f"- Generated: `{report['generated_at_utc']}`",
        f"- Estimate: `{report['estimate_method']}`",
        f"- Warning: {report['estimate_warning']}",
        f"- Selection: {report.get('selection_note', '')}",
        "",
        "## Summary",
        "",
        markdown_table(
            ["Layer", "Files", "Nonblank lines", "Characters", "Estimated tokens"],
            [
                ("Always-loaded entrypoints", always["files"], always["nonblank_lines"], always["characters"], always["estimated_tokens"]),
                ("Router", 1 if report["router"] else 0, report["router"]["nonblank_lines"] if report["router"] else 0, report["router"]["characters"] if report["router"] else 0, report["router"]["estimated_tokens"] if report["router"] else 0),
                ("Entrypoints + router", bundle["files"], bundle["nonblank_lines"], bundle["characters"], bundle["estimated_tokens"]),
                ("Other on-demand resources", on_demand["files"], on_demand["nonblank_lines"], on_demand["characters"], on_demand["estimated_tokens"]),
            ],
        ),
        "",
        "## Always-loaded files",
        "",
        markdown_table(
            ["File", "Nonblank lines", "Characters", "Estimated tokens"],
            ((row["path"], row["nonblank_lines"], row["characters"], row["estimated_tokens"]) for row in report["always_loaded"]["files"]),
        ),
        "",
        "## Direct router-link bundles",
        "",
        markdown_table(
            ["Linked resource", "Bundle files", "Bundle nonblank lines", "Bundle estimated tokens", "Increment after entrypoints"],
            (
                (
                    row["first_read"],
                    row["bundle"]["files"],
                    row["bundle"]["nonblank_lines"],
                    row["bundle"]["estimated_tokens"],
                    row["increment_over_entrypoints"],
                )
                for row in report["representative_route_bundles"]
            ),
        ),
    ]
    comparison = report.get("comparison")
    if comparison:
        lines.extend(["", "## Baseline comparison", ""])
        if comparison.get("error"):
            lines.append(f"- Error: {comparison['error']}")
        else:
            lines.append(f"- Baseline: `{comparison['baseline']}`")
            d = comparison["always_loaded_delta"]
            lines.append(
                f"- Always-loaded delta: {d['nonblank_lines']:+d} nonblank lines, "
                f"{d['characters']:+d} characters, {d['estimated_tokens']:+d} estimated tokens."
            )
            pct = comparison.get("always_loaded_estimated_tokens_percent")
            if pct is not None:
                lines.append(f"- Always-loaded estimated-token change: {pct:+.1f}%.")
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"error: repository root is not a directory: {root}", file=sys.stderr)
        return 2
    if args.always:
        always_paths = [root / value for value in args.always]
    else:
        always_paths = [root / value for value in DEFAULT_ENTRYPOINTS if (root / value).is_file()]
    docs_dir = root / args.docs_dir
    router = root / args.router
    report = build_report(root, always_paths, docs_dir, router)
    report["selection_note"] = (
        "Always-loaded totals use the explicitly supplied --always files."
        if args.always
        else "Always-loaded totals aggregate all detected entrypoint files; use --always for a client-specific measurement."
    )
    if args.compare:
        report["comparison"] = compare_report(report, Path(args.compare).expanduser())
    json_text = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.snapshot_out:
        output = Path(args.snapshot_out).expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json_text, encoding="utf-8")
    if args.json:
        sys.stdout.write(json_text)
    else:
        sys.stdout.write(to_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
