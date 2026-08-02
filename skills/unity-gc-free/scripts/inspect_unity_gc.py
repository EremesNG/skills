#!/usr/bin/env python3
"""Emit bounded, read-only investigation leads for Unity GC allocation work."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence
from urllib.parse import unquote_plus


SCHEMA_VERSION = 1
REDACTION_MARKER = "REDACTED"

RELEVANT_PACKAGE_NAMES = {
    "com.cysharp.memorypack",
    "com.cysharp.observablecollections",
    "com.cysharp.r3",
    "com.cysharp.unitask",
    "com.cysharp.zlinq",
    "com.cysharp.zstring",
    "com.kyrylokuzyk.primetween",
    "com.neuecc.messagepack",
    "com.unity.addressables",
    "com.unity.burst",
    "com.unity.collections",
    "com.unity.nuget.system.buffers",
    "com.unity.test-framework.performance",
}

RELEVANT_PACKAGE_TOKENS = (
    "addressables",
    "arraypool",
    "burst",
    "collections",
    "dotween",
    "memorypack",
    "messagepack",
    "observablecollections",
    "performance-testing",
    "performancetesting",
    "primetween",
    "unitask",
    "zlinq",
    "zstring",
)

SENSITIVE_PARAMETER_NAMES = {
    "accesskey",
    "apikey",
    "auth",
    "authorization",
    "key",
    "passwd",
    "sig",
}

SENSITIVE_PARAMETER_SUFFIXES = (
    "credential",
    "password",
    "secret",
    "signature",
    "token",
)

URI_USERINFO_PATTERN = re.compile(
    r"(?P<prefix>[A-Za-z][A-Za-z0-9+.-]*://)[^/@\s]+@"
)

DEPENDENCY_ASSIGNMENT_PATTERN = re.compile(
    r"(?P<key>[A-Za-z0-9_.%+-]+)(?P<separator>\s*=\s*)(?P<value>[^&#;\s]+)"
)

EXCLUDED_DIRECTORY_NAMES = {
    ".git",
    ".hg",
    ".idea",
    ".svn",
    ".vs",
    ".vscode",
    "artifacts",
    "bin",
    "build",
    "builds",
    "cache",
    "generated",
    "generatedcode",
    "library",
    "logs",
    "memorycaptures",
    "obj",
    "recordings",
    "temp",
    "tmp",
    "usersettings",
}

SECRET_LIKE_DIRECTORY_NAMES = {
    ".secrets",
    "credentials",
    "private-keys",
    "private_keys",
    "secrets",
}

SECRET_LIKE_FILE_TOKENS = {
    "accesskey",
    "apikey",
    "clientsecret",
    "credential",
    "privatekey",
    "secret",
    "serviceaccount",
    "signingkey",
}

SIGNAL_PATTERNS = {
    "allocating_physics_queries": re.compile(
        r"\bPhysics(?:2D)?\.(?:RaycastAll|SphereCastAll|BoxCastAll|CapsuleCastAll|"
        r"OverlapSphere|OverlapBox|OverlapCapsule|OverlapCircleAll|OverlapPointAll)\s*\("
    ),
    "array_return_apis": re.compile(
        r"\bInput\.touches\b|\b\w+\.(?:vertices|triangles|normals|tangents|uv|contacts)\b"
    ),
    "coroutines": re.compile(r"\bIEnumerator\b|\bStartCoroutine\s*\("),
    "dotween": re.compile(r"\b(?:DOTween|DG\.Tweening)\b|\.DO[A-Z][A-Za-z0-9_]*\s*\("),
    "lambdas": re.compile(r"=>"),
    "logging": re.compile(
        r"\b(?:UnityEngine\.)?Debug\.(?:Log|LogWarning|LogError|LogException|LogFormat)\s*\("
    ),
    "native_containers": re.compile(
        r"\bNative(?:Array|List|HashMap|HashSet|Queue|Stream|Reference|Slice|ParallelHashMap)\s*<"
    ),
    "spawn_destroy": re.compile(
        r"\b(?:(?:UnityEngine\.)?Object\.)?(?:Instantiate|Destroy|DestroyImmediate)\s*\("
    ),
    "string_formatting": re.compile(
        r"(?:\$@|@\$|\$)[\"']|\bstring\.Format\s*\(|\.ToString\s*\("
    ),
    "system_linq": re.compile(
        r"\busing\s+System\.Linq\b|\bEnumerable\.|\.(?:Where|Select|SelectMany|"
        r"OrderBy|ThenBy|GroupBy|ToArray|ToList)\s*\("
    ),
    "temporary_collections": re.compile(
        r"\bnew\s+(?:List|Dictionary|HashSet|Queue|Stack|LinkedList)\s*<"
    ),
}


def non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect Unity allocation-risk signals without modifying the project."
    )
    parser.add_argument("--root", required=True, help="Unity project root")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument(
        "--max-samples",
        type=non_negative_int,
        default=5,
        help="Maximum relative paths retained for each category",
    )
    return parser.parse_args(argv)


def empty_report(root: Path) -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "root": str(root),
        "unity_detected": False,
        "unity_version": None,
        "scripting_backend_hints": [],
        "relevant_packages": [],
        "inventory": {},
        "signals": {},
        "warnings": [],
    }


def relative_path(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def read_unity_version(path: Path, root: Path, warnings: List[str]) -> Optional[str]:
    if not path.is_file():
        warnings.append("Missing metadata: {0}.".format(relative_path(root, path)))
        return None
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        warnings.append("Could not read metadata: {0}.".format(relative_path(root, path)))
        return None
    match = re.search(r"(?m)^m_EditorVersion:\s*(\S+)\s*$", content)
    if match:
        return match.group(1)
    warnings.append(
        "Malformed metadata: {0} has no m_EditorVersion value.".format(
            relative_path(root, path)
        )
    )
    return None


def read_backend_hints(path: Path, root: Path, warnings: List[str]) -> List[Dict[str, str]]:
    if not path.is_file():
        warnings.append("Missing optional metadata: {0}.".format(relative_path(root, path)))
        return []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        warnings.append("Could not read metadata: {0}.".format(relative_path(root, path)))
        return []

    hints: List[Dict[str, str]] = []
    found_header = False
    malformed = False
    for index, line in enumerate(lines):
        header = re.match(r"^(?P<indent>\s*)scriptingBackend:\s*(?P<scalar>\S*)\s*$", line)
        if not header:
            continue
        found_header = True
        scalar = header.group("scalar")
        if scalar:
            hints.append({"target": "default", "raw_value": scalar})
            continue
        header_indent = len(header.group("indent"))
        for child in lines[index + 1 :]:
            if not child.strip():
                continue
            child_indent = len(child) - len(child.lstrip())
            if child_indent <= header_indent:
                break
            entry = re.match(r"^\s*([^:#]+):\s*(\S+)\s*$", child)
            if not entry:
                malformed = True
                continue
            hints.append(
                {"target": entry.group(1).strip(), "raw_value": entry.group(2).strip()}
            )
        break

    if not found_header or malformed or not hints:
        warnings.append(
            "Malformed optional metadata: {0} has no complete scriptingBackend entries.".format(
                relative_path(root, path)
            )
        )
    if hints:
        warnings.append(
            "Raw scripting-backend values are configuration hints, not proof of the active build target or backend."
        )
    return sorted(hints, key=lambda item: (item["target"].casefold(), item["raw_value"]))


def is_sensitive_parameter(name: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]", "", unquote_plus(name).casefold())
    return normalized in SENSITIVE_PARAMETER_NAMES or normalized.endswith(
        SENSITIVE_PARAMETER_SUFFIXES
    )


def sanitize_dependency_value(value: Any) -> str:
    if not isinstance(value, str):
        return REDACTION_MARKER
    text = URI_USERINFO_PATTERN.sub(
        lambda match: "{0}{1}@".format(match.group("prefix"), REDACTION_MARKER),
        value,
    )

    def replace(match: re.Match[str]) -> str:
        if not is_sensitive_parameter(match.group("key")):
            return match.group(0)
        return "{0}{1}{2}".format(
            match.group("key"), match.group("separator"), REDACTION_MARKER
        )

    return DEPENDENCY_ASSIGNMENT_PATTERN.sub(replace, text)


def is_relevant_package(name: str) -> bool:
    normalized = name.casefold()
    return normalized in RELEVANT_PACKAGE_NAMES or any(
        token in normalized for token in RELEVANT_PACKAGE_TOKENS
    )


def read_relevant_packages(path: Path, root: Path, warnings: List[str]) -> List[Dict[str, str]]:
    if not path.is_file():
        warnings.append("Missing metadata: {0}.".format(relative_path(root, path)))
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        warnings.append(
            "Malformed metadata: {0} could not be parsed.".format(
                relative_path(root, path)
            )
        )
        return []
    dependencies = payload.get("dependencies", {}) if isinstance(payload, dict) else None
    if not isinstance(dependencies, dict):
        warnings.append(
            "Malformed metadata: {0} dependencies must be an object.".format(
                relative_path(root, path)
            )
        )
        return []
    return [
        {"name": str(name), "version": sanitize_dependency_value(version)}
        for name, version in sorted(
            dependencies.items(), key=lambda item: str(item[0]).casefold()
        )
        if is_relevant_package(str(name))
    ]


def bounded_paths(paths: Iterable[str], max_samples: int) -> Dict[str, Any]:
    ordered = sorted(set(paths), key=str.casefold)
    return {"count": len(ordered), "samples": ordered[:max_samples]}


def is_secret_like_filename(filename: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]", "", Path(filename).stem.casefold())
    return any(token in normalized for token in SECRET_LIKE_FILE_TOKENS)


def iter_csharp_files(source_root: Path) -> Iterable[Path]:
    for directory, child_directories, filenames in os.walk(str(source_root)):
        child_directories[:] = sorted(
            (
                name
                for name in child_directories
                if name.casefold() not in EXCLUDED_DIRECTORY_NAMES
                and name.casefold() not in SECRET_LIKE_DIRECTORY_NAMES
            ),
            key=str.casefold,
        )
        for filename in sorted(filenames, key=str.casefold):
            if (
                Path(filename).suffix.casefold() == ".cs"
                and not is_secret_like_filename(filename)
            ):
                yield Path(directory) / filename


def scan_sources(root: Path, max_samples: int, warnings: List[str]) -> Dict[str, Any]:
    source_files: List[Path] = []
    for source_root in (root / "Assets", root / "Packages"):
        if source_root.is_dir():
            source_files.extend(iter_csharp_files(source_root))

    ordered_files = sorted(
        source_files, key=lambda path: relative_path(root, path).casefold()
    )
    matching_paths: Dict[str, List[str]] = {name: [] for name in SIGNAL_PATTERNS}
    for source_file in ordered_files:
        source_path = relative_path(root, source_file)
        try:
            content = source_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            warnings.append("Could not inspect source path: {0}.".format(source_path))
            continue
        for name, pattern in SIGNAL_PATTERNS.items():
            if pattern.search(content):
                matching_paths[name].append(source_path)

    return {
        "inventory": {
            "csharp_files": bounded_paths(
                (relative_path(root, path) for path in ordered_files), max_samples
            )
        },
        "signals": {
            name: bounded_paths(paths, max_samples)
            for name, paths in sorted(matching_paths.items())
        },
    }


def emit(report: Dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(report, indent=2))
        return
    print("Unity GC allocation lead inspection")
    print("Root: {0}".format(report["root"]))
    print("Unity detected: {0}".format("yes" if report["unity_detected"] else "no"))
    if report["unity_detected"]:
        print("Unity version: {0}".format(report["unity_version"] or "unknown"))
        print("Relevant packages: {0}".format(len(report["relevant_packages"])))
        csharp_files = report["inventory"].get(
            "csharp_files", {"count": 0, "samples": []}
        )
        print("C# files: {0}".format(csharp_files["count"]))
        print("Signals are investigation leads, not diagnoses.")
        for name, summary in report["signals"].items():
            if not summary["count"]:
                continue
            print("{0}: {1}".format(name.replace("_", " "), summary["count"]))
            for sample in summary["samples"]:
                print("  - {0}".format(sample))
    for warning in report["warnings"]:
        print("Warning: {0}".format(warning))


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root = Path(args.root).expanduser().resolve()
    report = empty_report(root)
    if not root.is_dir() or not (root / "ProjectSettings").is_dir():
        report["warnings"].append(
            "Not a Unity project: expected a readable ProjectSettings directory."
        )
        emit(report, args.json)
        return 2

    report["unity_detected"] = True
    report["unity_version"] = read_unity_version(
        root / "ProjectSettings" / "ProjectVersion.txt", root, report["warnings"]
    )
    report["scripting_backend_hints"] = read_backend_hints(
        root / "ProjectSettings" / "ProjectSettings.asset", root, report["warnings"]
    )
    report["relevant_packages"] = read_relevant_packages(
        root / "Packages" / "manifest.json", root, report["warnings"]
    )
    source_report = scan_sources(root, args.max_samples, report["warnings"])
    report["inventory"] = source_report["inventory"]
    report["signals"] = source_report["signals"]
    emit(report, args.json)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - last-resort CLI contract
        print("Unexpected inspection failure: {0}".format(exc), file=sys.stderr)
        raise SystemExit(3)
