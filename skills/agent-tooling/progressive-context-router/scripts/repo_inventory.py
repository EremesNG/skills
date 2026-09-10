#!/usr/bin/env python3
"""Create a read-only inventory for designing repository context routing.

The script reads filenames, selected manifests, and declared task scripts. It
never imports or executes repository code and does not require network access.
"""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

VERSION = "1.0.0"

IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "vendor",
    "dist",
    "build",
    "out",
    "target",
    "coverage",
    ".coverage",
    ".next",
    ".nuxt",
    ".output",
    ".turbo",
    ".cache",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    "__pycache__",
    "bin",
    "obj",
}

SECRET_BASENAMES = {
    ".env",
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "credentials",
    "credentials.json",
    "service-account.json",
    "secrets.yml",
    "secrets.yaml",
}

SAFE_ENV_SUFFIXES = {".example", ".sample", ".template", ".dist"}

MANIFEST_NAMES = {
    "package.json",
    "pnpm-workspace.yaml",
    "pnpm-workspace.yml",
    "yarn.lock",
    "pnpm-lock.yaml",
    "package-lock.json",
    "bun.lock",
    "bun.lockb",
    "turbo.json",
    "nx.json",
    "lerna.json",
    "pyproject.toml",
    "poetry.lock",
    "uv.lock",
    "requirements.txt",
    "Pipfile",
    "setup.py",
    "setup.cfg",
    "Cargo.toml",
    "Cargo.lock",
    "go.mod",
    "go.sum",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "settings.gradle",
    "settings.gradle.kts",
    "Gemfile",
    "composer.json",
    "mix.exs",
    "deno.json",
    "deno.jsonc",
    "Makefile",
    "makefile",
    "GNUmakefile",
    "justfile",
    "Justfile",
    "Taskfile.yml",
    "Taskfile.yaml",
}

INSTRUCTION_BASENAMES = {
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "CONVENTIONS.md",
}

TEST_CONFIG_NAMES = {
    "pytest.ini",
    "tox.ini",
    "jest.config.js",
    "jest.config.cjs",
    "jest.config.mjs",
    "jest.config.ts",
    "vitest.config.js",
    "vitest.config.mjs",
    "vitest.config.ts",
    "playwright.config.js",
    "playwright.config.ts",
    "cypress.config.js",
    "cypress.config.ts",
    "phpunit.xml",
    "phpunit.xml.dist",
    ".rspec",
}

CI_BASENAMES = {
    ".gitlab-ci.yml",
    ".gitlab-ci.yaml",
    "Jenkinsfile",
    "azure-pipelines.yml",
    "azure-pipelines.yaml",
    "buildkite.yml",
    "buildkite.yaml",
    "circle.yml",
}

LANGUAGE_BY_SUFFIX = {
    ".py": "Python",
    ".pyi": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".mts": "TypeScript",
    ".cts": "TypeScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".cs": "C#",
    ".fs": "F#",
    ".fsx": "F#",
    ".rb": "Ruby",
    ".php": "PHP",
    ".ex": "Elixir",
    ".exs": "Elixir",
    ".swift": "Swift",
    ".scala": "Scala",
    ".c": "C",
    ".h": "C/C++ header",
    ".cc": "C++",
    ".cpp": "C++",
    ".cxx": "C++",
    ".hpp": "C++ header",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".fish": "Shell",
    ".sql": "SQL",
    ".vue": "Vue",
    ".svelte": "Svelte",
    ".dart": "Dart",
    ".lua": "Lua",
    ".r": "R",
    ".R": "R",
    ".clj": "Clojure",
    ".cljs": "ClojureScript",
    ".tf": "Terraform",
    ".proto": "Protocol Buffers",
}

DOC_SUFFIXES = {".md", ".mdx", ".rst", ".adoc"}


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a safe repository inventory for progressive context routing."
    )
    parser.add_argument("--root", default=".", help="Repository root (default: current directory).")
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--json", action="store_true", help="Print JSON to stdout.")
    output.add_argument("--markdown", action="store_true", help="Print Markdown to stdout (default).")
    parser.add_argument("--json-out", help="Also write the JSON inventory to this path.")
    parser.add_argument("--markdown-out", help="Also write the Markdown inventory to this path.")
    parser.add_argument(
        "--include-untracked",
        action="store_true",
        help="When Git is available, include untracked non-ignored files.",
    )
    parser.add_argument(
        "--filesystem",
        action="store_true",
        help="Walk the filesystem instead of using git ls-files.",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=50000,
        help="Maximum number of files to inventory (default: 50000).",
    )
    parser.add_argument("--version", action="version", version=VERSION)
    args = parser.parse_args(argv)
    if args.max_files < 1:
        parser.error("--max-files must be positive")
    return args


def run_git(root: Path, args: Sequence[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def git_available(root: Path) -> bool:
    try:
        result = run_git(root, ["rev-parse", "--is-inside-work-tree"])
    except OSError:
        return False
    return result.returncode == 0 and result.stdout.strip() == b"true"


def is_secret_like(relative: Path) -> bool:
    name = relative.name
    lower = name.lower()
    if lower in SECRET_BASENAMES:
        return True
    if lower.startswith(".env."):
        suffix = lower[len(".env") :]
        return suffix not in SAFE_ENV_SUFFIXES
    if lower.endswith((".pem", ".p12", ".pfx", ".key")):
        return True
    if "secret" in lower and lower not in {"secrets.example.yml", "secrets.example.yaml"}:
        return True
    return False


def ignored_path(relative: Path) -> bool:
    return any(part in IGNORED_DIRS for part in relative.parts[:-1])


def list_files_from_git(root: Path, include_untracked: bool) -> Tuple[List[Path], str]:
    git_args = ["ls-files", "-z"]
    if include_untracked:
        git_args = ["ls-files", "-co", "--exclude-standard", "-z"]
    result = run_git(root, git_args)
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"git ls-files failed: {message}")
    paths = [Path(os.fsdecode(item)) for item in result.stdout.split(b"\0") if item]
    return paths, "git"


def list_files_from_fs(root: Path) -> Tuple[List[Path], str]:
    paths: List[Path] = []
    for current, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        current_path = Path(current)
        for name in names:
            absolute = current_path / name
            try:
                relative = absolute.relative_to(root)
            except ValueError:
                continue
            paths.append(relative)
    return paths, "filesystem"


def safe_file_list(root: Path, raw_paths: Iterable[Path], max_files: int) -> Tuple[List[Path], Dict[str, int]]:
    result: List[Path] = []
    stats = {"ignored": 0, "secret_like_redacted": 0, "missing": 0, "truncated": 0}
    seen = set()
    for relative in raw_paths:
        if relative.is_absolute() or ".." in relative.parts:
            stats["ignored"] += 1
            continue
        normalized = Path(*[part for part in relative.parts if part not in {"", "."}])
        key = normalized.as_posix()
        if not key or key in seen:
            continue
        seen.add(key)
        if ignored_path(normalized):
            stats["ignored"] += 1
            continue
        if is_secret_like(normalized):
            stats["secret_like_redacted"] += 1
            continue
        absolute = root / normalized
        if not absolute.is_file() or absolute.is_symlink():
            stats["missing"] += 1
            continue
        result.append(normalized)
        if len(result) >= max_files:
            stats["truncated"] = 1
            break
    result.sort(key=lambda p: p.as_posix().lower())
    return result, stats


def read_text_limited(path: Path, max_bytes: int = 1_000_000) -> Optional[str]:
    try:
        if path.stat().st_size > max_bytes:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def classify_paths(paths: Sequence[Path]) -> Dict[str, List[str]]:
    groups: Dict[str, List[str]] = {
        "manifests": [],
        "instructions": [],
        "documentation": [],
        "test_config": [],
        "ci": [],
    }
    for path in paths:
        posix = path.as_posix()
        name = path.name
        if name in MANIFEST_NAMES:
            groups["manifests"].append(posix)
        if name in INSTRUCTION_BASENAMES or posix == ".github/copilot-instructions.md" or posix.startswith(".cursor/rules/"):
            groups["instructions"].append(posix)
        if path.suffix.lower() in DOC_SUFFIXES and (
            name.lower().startswith("readme")
            or posix.startswith("docs/")
            or posix.startswith("documentation/")
        ):
            groups["documentation"].append(posix)
        if name in TEST_CONFIG_NAMES or re.search(r"(^|/)(tests?|specs?|__tests__)(/|$)", posix, flags=re.I):
            groups["test_config"].append(posix)
        if name in CI_BASENAMES or posix.startswith(".github/workflows/") or posix.startswith(".circleci/"):
            groups["ci"].append(posix)
    for key in groups:
        groups[key] = groups[key][:200]
    return groups


def collect_languages(paths: Sequence[Path]) -> List[Dict[str, Any]]:
    counts: collections.Counter[str] = collections.Counter()
    for path in paths:
        language = LANGUAGE_BY_SUFFIX.get(path.suffix)
        if language:
            counts[language] += 1
    return [
        {"language": language, "files": count}
        for language, count in counts.most_common()
    ]


def collect_top_level(paths: Sequence[Path]) -> List[Dict[str, Any]]:
    counts: collections.Counter[str] = collections.Counter()
    code_counts: collections.Counter[str] = collections.Counter()
    manifests: collections.Counter[str] = collections.Counter()
    tests: collections.Counter[str] = collections.Counter()
    for path in paths:
        top = path.parts[0] if len(path.parts) > 1 else "(root)"
        counts[top] += 1
        if path.suffix in LANGUAGE_BY_SUFFIX:
            code_counts[top] += 1
        if path.name in MANIFEST_NAMES:
            manifests[top] += 1
        if re.search(r"(^|/)(tests?|specs?|__tests__)(/|$)", path.as_posix(), flags=re.I):
            tests[top] += 1
    rows = []
    for top, count in counts.most_common():
        rows.append(
            {
                "area": top,
                "files": count,
                "code_files": code_counts[top],
                "manifests": manifests[top],
                "test_files": tests[top],
            }
        )
    return rows




def sanitize_declared_command(command: str) -> str:
    """Redact credential-like values from a manifest command before reporting it."""
    value = command
    value = re.sub(
        r"(?i)\b(password|passwd|token|api[_-]?key|secret)(\s*[:=]\s*)([^\s'\"]+)",
        lambda match: f"{match.group(1)}{match.group(2)}<redacted>",
        value,
    )
    value = re.sub(r"https?://[^/@\s:]+:[^/@\s]+@", "https://<redacted>@", value)
    value = re.sub(r"\bAKIA[0-9A-Z]{16}\b", "<redacted-aws-key>", value)
    value = re.sub(r"\b(?:sk-|gh[pousr]_)[A-Za-z0-9_-]{20,}\b", "<redacted-token>", value)
    return value[:500]

def parse_package_json(root: Path, paths: Sequence[Path]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    packages: List[Dict[str, Any]] = []
    declared_scripts: List[Dict[str, Any]] = []
    for relative in paths:
        if relative.name != "package.json":
            continue
        text = read_text_limited(root / relative)
        if text is None:
            packages.append({"path": relative.as_posix(), "error": "file too large or unreadable"})
            continue
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            packages.append({"path": relative.as_posix(), "error": f"invalid JSON: {exc.msg}"})
            continue
        if not isinstance(data, dict):
            packages.append({"path": relative.as_posix(), "error": "JSON root is not an object"})
            continue
        workspaces = data.get("workspaces")
        if isinstance(workspaces, dict):
            workspaces = workspaces.get("packages")
        package = {
            "path": relative.as_posix(),
            "name": data.get("name"),
            "private": data.get("private"),
            "package_manager": data.get("packageManager"),
            "workspaces": workspaces if isinstance(workspaces, list) else None,
        }
        packages.append(package)
        scripts = data.get("scripts", {})
        if isinstance(scripts, dict):
            for name, command in sorted(scripts.items()):
                if isinstance(name, str) and isinstance(command, str):
                    declared_scripts.append(
                        {
                            "manifest": relative.as_posix(),
                            "name": name,
                            "command": sanitize_declared_command(command),
                        }
                    )
    return packages, declared_scripts[:500]


def collect_make_targets(root: Path, paths: Sequence[Path]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    pattern = re.compile(r"^([A-Za-z0-9][A-Za-z0-9_.-]*):(?:\s|$)")
    excluded = {"all", ".PHONY", "FORCE"}
    for relative in paths:
        if relative.name not in {"Makefile", "makefile", "GNUmakefile"}:
            continue
        text = read_text_limited(root / relative)
        if text is None:
            continue
        targets = []
        for line in text.splitlines():
            if line.startswith((" ", "\t", "#")):
                continue
            match = pattern.match(line)
            if match and match.group(1) not in excluded and "%" not in match.group(1):
                targets.append(match.group(1))
        if targets:
            rows.append({"manifest": relative.as_posix(), "targets": sorted(set(targets))[:100]})
    return rows


def build_inventory(root: Path, paths: Sequence[Path], mode: str, scan_stats: Dict[str, int]) -> Dict[str, Any]:
    groups = classify_paths(paths)
    packages, scripts = parse_package_json(root, paths)
    make_targets = collect_make_targets(root, paths)
    monorepo_hints = []
    path_set = {p.as_posix() for p in paths}
    for candidate in ["pnpm-workspace.yaml", "pnpm-workspace.yml", "turbo.json", "nx.json", "lerna.json"]:
        if candidate in path_set:
            monorepo_hints.append(candidate)
    for package in packages:
        if package.get("workspaces"):
            monorepo_hints.append(f"{package['path']}:workspaces")

    return {
        "schema_version": 1,
        "tool": {"name": "repo_inventory.py", "version": VERSION},
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "root": str(root),
        "scan_mode": mode,
        "file_count": len(paths),
        "scan_stats": scan_stats,
        "top_level_areas": collect_top_level(paths),
        "languages": collect_languages(paths),
        "important_paths": groups,
        "package_manifests": packages,
        "declared_package_scripts": scripts,
        "declared_make_targets": make_targets,
        "monorepo_hints": sorted(set(monorepo_hints)),
        "notes": [
            "Commands are extracted from manifests but are not executed or proven to succeed.",
            "Secret-like filenames and common generated or third-party directories are excluded.",
            "Directory and language counts are discovery signals, not context-domain decisions.",
        ],
    }


def markdown_table(headers: Sequence[str], rows: Iterable[Sequence[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    count = 0
    for row in rows:
        lines.append("| " + " | ".join(str(value).replace("|", "\\|") for value in row) + " |")
        count += 1
    if count == 0:
        return "_None found._"
    return "\n".join(lines)


def to_markdown(data: Dict[str, Any]) -> str:
    lines = [
        "# Repository inventory",
        "",
        f"- Root: `{data['root']}`",
        f"- Generated: `{data['generated_at_utc']}`",
        f"- Scan mode: `{data['scan_mode']}`",
        f"- Files inventoried: **{data['file_count']}**",
        f"- Secret-like filenames redacted: **{data['scan_stats']['secret_like_redacted']}**",
    ]
    if data["scan_stats"].get("truncated"):
        lines.append("- Warning: file list reached `--max-files` and was truncated.")

    lines.extend(["", "## Top-level areas", ""])
    lines.append(
        markdown_table(
            ["Area", "Files", "Code files", "Manifests", "Test files"],
            (
                (r["area"], r["files"], r["code_files"], r["manifests"], r["test_files"])
                for r in data["top_level_areas"][:30]
            ),
        )
    )

    lines.extend(["", "## Languages", ""])
    lines.append(
        markdown_table(
            ["Language", "Files"],
            ((r["language"], r["files"]) for r in data["languages"][:20]),
        )
    )

    labels = [
        ("instructions", "Existing agent instructions"),
        ("manifests", "Manifests and task runners"),
        ("test_config", "Test configuration and test paths"),
        ("ci", "CI configuration"),
        ("documentation", "Documentation candidates"),
    ]
    for key, title in labels:
        lines.extend(["", f"## {title}", ""])
        values = data["important_paths"][key]
        if values:
            lines.extend(f"- `{value}`" for value in values[:100])
            if len(values) > 100:
                lines.append(f"- … {len(values) - 100} more")
        else:
            lines.append("_None found._")

    lines.extend(["", "## Package manifests", ""])
    package_rows = []
    for package in data["package_manifests"]:
        package_rows.append(
            (
                f"`{package['path']}`",
                package.get("name") or "",
                package.get("package_manager") or "",
                ", ".join(package.get("workspaces") or [])[:200],
                package.get("error") or "",
            )
        )
    lines.append(markdown_table(["Path", "Name", "Package manager", "Workspaces", "Issue"], package_rows))

    lines.extend(["", "## Declared package scripts", ""])
    script_rows = (
        (f"`{row['manifest']}`", f"`{row['name']}`", f"`{row['command']}`")
        for row in data["declared_package_scripts"][:100]
    )
    lines.append(markdown_table(["Manifest", "Script", "Declared command"], script_rows))
    if len(data["declared_package_scripts"]) > 100:
        lines.append(f"\n_{len(data['declared_package_scripts']) - 100} additional scripts omitted from this view._")

    lines.extend(["", "## Declared Make targets", ""])
    if data["declared_make_targets"]:
        for row in data["declared_make_targets"]:
            lines.append(f"- `{row['manifest']}`: " + ", ".join(f"`{target}`" for target in row["targets"]))
    else:
        lines.append("_None found._")

    lines.extend(["", "## Monorepo signals", ""])
    if data["monorepo_hints"]:
        lines.extend(f"- `{hint}`" for hint in data["monorepo_hints"])
    else:
        lines.append("_No explicit workspace signal found._")

    lines.extend(["", "## Interpretation notes", ""])
    lines.extend(f"- {note}" for note in data["notes"])
    return "\n".join(lines) + "\n"


def write_output(path_value: str, content: str) -> None:
    path = Path(path_value).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"error: repository root is not a directory: {root}", file=sys.stderr)
        return 2

    try:
        if not args.filesystem and git_available(root):
            raw_paths, mode = list_files_from_git(root, args.include_untracked)
        else:
            raw_paths, mode = list_files_from_fs(root)
        paths, scan_stats = safe_file_list(root, raw_paths, args.max_files)
        data = build_inventory(root, paths, mode, scan_stats)
    except (OSError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    json_text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    markdown_text = to_markdown(data)

    if args.json_out:
        write_output(args.json_out, json_text)
    if args.markdown_out:
        write_output(args.markdown_out, markdown_text)

    if args.json:
        sys.stdout.write(json_text)
    else:
        sys.stdout.write(markdown_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
