#!/usr/bin/env python3
"""Produce a bounded, read-only inventory of a Unity project."""

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

SENSITIVE_DEPENDENCY_PARAMETER_NAMES = {
    "accesskey",
    "apikey",
    "auth",
    "authorization",
    "key",
    "passwd",
    "sig",
}

SENSITIVE_DEPENDENCY_PARAMETER_SUFFIXES = (
    "credential",
    "password",
    "secret",
    "signature",
    "token",
)

DEPENDENCY_ASSIGNMENT_PATTERN = re.compile(
    r"(?P<key>[A-Za-z0-9_.%+-]+)(?P<separator>\s*=\s*)(?P<value>[^&#;\s]+)"
)

URI_USERINFO_PATTERN = re.compile(
    r"(?P<prefix>[A-Za-z][A-Za-z0-9+.-]*://)[^/@\s]+@"
)

EXCLUDED_DIRECTORY_NAMES = {
    ".git",
    ".hg",
    ".idea",
    ".svn",
    ".vs",
    ".vscode",
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
    "scene_lookup": re.compile(
        r"\b(?:GameObject\.Find|FindObjectOfType|FindObjectsOfType|"
        r"FindFirstObjectByType|FindAnyObjectByType|FindObjectsByType)\s*(?:<|\()"
    ),
    "global_lifetime": re.compile(r"\bDontDestroyOnLoad\s*\("),
    "static_events": re.compile(r"\bstatic\s+event\b"),
    "frame_callbacks": re.compile(
        r"\b(?:void\s+)?(?:Update|FixedUpdate|LateUpdate)\s*\("
    ),
    "spawn_destroy": re.compile(r"\b(?:Instantiate|Destroy)\s*\("),
    "resource_loading": re.compile(r"\bResources\.Load(?:Async)?\s*(?:<|\()"),
    "async_void": re.compile(r"\basync\s+void\b"),
}


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect Unity project metadata and source layout without modifying it."
    )
    parser.add_argument("--root", required=True, help="Unity project root")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument(
        "--max-samples",
        type=int,
        default=5,
        help="Maximum paths retained for each inventory or signal category",
    )
    return parser.parse_args(argv)


def empty_report(root: Path) -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "root": str(root),
        "unity_detected": False,
        "unity_version": None,
        "packages": [],
        "inventory": {},
        "signals": {},
        "warnings": [],
    }


def relative_path(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def bounded_paths(paths: Iterable[str], max_samples: int) -> Dict[str, Any]:
    ordered = sorted(set(paths), key=str.casefold)
    return {"count": len(ordered), "samples": ordered[:max_samples]}


def bounded_records(records: Iterable[Dict[str, str]], max_samples: int) -> Dict[str, Any]:
    ordered = sorted(records, key=lambda item: (item["path"].casefold(), item["name"]))
    return {"count": len(ordered), "samples": ordered[:max_samples]}


def is_secret_like_filename(filename: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]", "", Path(filename).stem.casefold())
    return any(token in normalized for token in SECRET_LIKE_FILE_TOKENS)


def iter_source_files(source_root: Path) -> Iterable[Path]:
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
                Path(filename).suffix.casefold() in {".asmdef", ".cs"}
                and not is_secret_like_filename(filename)
            ):
                yield Path(directory) / filename


def read_unity_version(
    project_file: Path, root: Path, warnings: List[str]
) -> Optional[str]:
    if not project_file.is_file():
        warnings.append(
            "Missing metadata: {0}.".format(relative_path(root, project_file))
        )
        return None
    try:
        content = project_file.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        warnings.append(
            "Could not read {0}: {1}.".format(relative_path(root, project_file), exc)
        )
        return None
    for line in content.splitlines():
        if line.startswith("m_EditorVersion:"):
            value = line.partition(":")[2].strip()
            if value:
                return value
            break
    warnings.append(
        "Malformed metadata: {0} has no m_EditorVersion value.".format(
            relative_path(root, project_file)
        )
    )
    return None


def is_sensitive_dependency_parameter(name: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]", "", unquote_plus(name).casefold())
    return normalized in SENSITIVE_DEPENDENCY_PARAMETER_NAMES or normalized.endswith(
        SENSITIVE_DEPENDENCY_PARAMETER_SUFFIXES
    )


def redact_sensitive_dependency_assignments(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        if not is_sensitive_dependency_parameter(match.group("key")):
            return match.group(0)
        return "{0}{1}{2}".format(
            match.group("key"),
            match.group("separator"),
            REDACTION_MARKER,
        )

    return DEPENDENCY_ASSIGNMENT_PATTERN.sub(replace, text)


def sanitize_dependency_value(value: Any) -> str:
    if not isinstance(value, str):
        return REDACTION_MARKER
    text = URI_USERINFO_PATTERN.sub(
        lambda match: "{0}{1}@".format(
            match.group("prefix"), REDACTION_MARKER
        ),
        value,
    )
    return redact_sensitive_dependency_assignments(text)


def read_packages(
    manifest_file: Path, root: Path, warnings: List[str]
) -> List[Dict[str, str]]:
    if not manifest_file.is_file():
        warnings.append(
            "Missing metadata: {0}.".format(relative_path(root, manifest_file))
        )
        return []
    try:
        payload = json.loads(manifest_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        warnings.append(
            "Malformed metadata: {0} could not be parsed ({1}).".format(
                relative_path(root, manifest_file), exc
            )
        )
        return []
    if not isinstance(payload, dict):
        warnings.append(
            "Malformed metadata: {0} must contain a JSON object.".format(
                relative_path(root, manifest_file)
            )
        )
        return []
    dependencies = payload.get("dependencies", {})
    if not isinstance(dependencies, dict):
        warnings.append(
            "Malformed metadata: {0} dependencies must be an object.".format(
                relative_path(root, manifest_file)
            )
        )
        return []
    return [
        {"name": str(name), "version": sanitize_dependency_value(version)}
        for name, version in sorted(
            dependencies.items(), key=lambda item: str(item[0]).casefold()
        )
    ]


def is_test_assembly(payload: Dict[str, Any]) -> bool:
    optional = payload.get("optionalUnityReferences", [])
    constraints = payload.get("defineConstraints", [])
    name = payload.get("name", "")
    return (
        (isinstance(optional, list) and "TestAssemblies" in optional)
        or (isinstance(constraints, list) and "UNITY_INCLUDE_TESTS" in constraints)
        or (isinstance(name, str) and name.lower().endswith((".tests", ".test")))
    )


def inspect_project(root: Path, max_samples: int) -> Dict[str, Any]:
    report = empty_report(root)
    report["unity_detected"] = True
    report["unity_version"] = read_unity_version(
        root / "ProjectSettings" / "ProjectVersion.txt", root, report["warnings"]
    )
    report["packages"] = read_packages(
        root / "Packages" / "manifest.json", root, report["warnings"]
    )

    csharp_files: List[Path] = []
    assembly_records: List[Dict[str, str]] = []
    test_assembly_records: List[Dict[str, str]] = []
    for source_root in (root / "Assets", root / "Packages"):
        if not source_root.is_dir():
            continue
        for source_path in iter_source_files(source_root):
            if source_path.suffix.casefold() == ".cs":
                csharp_files.append(source_path)
                continue
            asmdef = source_path
            try:
                payload = json.loads(asmdef.read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                report["warnings"].append(
                    "Malformed assembly definition: {0} could not be parsed ({1}).".format(
                        relative_path(root, asmdef), exc
                    )
                )
                payload = {}
            if not isinstance(payload, dict):
                report["warnings"].append(
                    "Malformed assembly definition: {0} must contain a JSON object.".format(
                        relative_path(root, asmdef)
                    )
                )
                payload = {}
            name = payload.get("name")
            record = {
                "name": str(name or asmdef.stem),
                "path": relative_path(root, asmdef),
            }
            assembly_records.append(record)
            if is_test_assembly(payload):
                test_assembly_records.append(record)

    csharp_paths = [relative_path(root, path) for path in csharp_files]
    report["inventory"] = {
        "csharp_files": bounded_paths(csharp_paths, max_samples),
        "assembly_definitions": bounded_records(assembly_records, max_samples),
        "test_assemblies": bounded_records(test_assembly_records, max_samples),
    }

    matching_paths: Dict[str, List[str]] = {name: [] for name in SIGNAL_PATTERNS}
    for source_file in sorted(
        csharp_files, key=lambda path: relative_path(root, path).casefold()
    ):
        content = source_file.read_text(encoding="utf-8", errors="replace")
        source_path = relative_path(root, source_file)
        for name, pattern in SIGNAL_PATTERNS.items():
            if pattern.search(content):
                matching_paths[name].append(source_path)
    report["signals"] = {
        name: bounded_paths(paths, max_samples)
        for name, paths in sorted(matching_paths.items())
    }
    return report


def emit(report: Dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(report, indent=2))
        return

    print("Unity project inspection")
    print("Root: {0}".format(report["root"]))
    print("Unity detected: {0}".format("yes" if report["unity_detected"] else "no"))
    if report["unity_detected"]:
        print("Unity version: {0}".format(report["unity_version"] or "unknown"))
        print("Declared packages: {0}".format(len(report["packages"])))
        inventory_labels = (
            ("csharp_files", "C# files"),
            ("assembly_definitions", "Assembly definitions"),
            ("test_assemblies", "Test assemblies"),
        )
        for key, label in inventory_labels:
            summary = report["inventory"].get(key, {"count": 0, "samples": []})
            print("{0}: {1}".format(label, summary["count"]))

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

    report = inspect_project(root, max(0, args.max_samples))
    emit(report, args.json)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - last-resort CLI contract
        print("Unexpected inspection failure: {0}".format(exc), file=sys.stderr)
        raise SystemExit(3)
