from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "progressive-context-router"
SCRIPTS = SKILL_ROOT / "scripts"


def run_script(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class SkillPackageTests(unittest.TestCase):
    def test_frontmatter_and_layout(self) -> None:
        skill_file = SKILL_ROOT / "SKILL.md"
        text = skill_file.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        _, frontmatter, body = text.split("---", 2)
        name_match = re.search(r"(?m)^name:\s*([^\n]+)$", frontmatter)
        description_match = re.search(r"(?m)^description:\s*([^\n]+)$", frontmatter)
        self.assertIsNotNone(name_match)
        self.assertIsNotNone(description_match)
        name = name_match.group(1).strip()  # type: ignore[union-attr]
        description = description_match.group(1).strip()  # type: ignore[union-attr]
        self.assertEqual(name, SKILL_ROOT.name)
        self.assertRegex(name, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertLessEqual(len(name), 64)
        self.assertLessEqual(len(description), 1024)
        self.assertLess(len(body.splitlines()), 500)
        for directory in ("assets", "references", "scripts", "evals"):
            self.assertTrue((SKILL_ROOT / directory).is_dir())

    def test_inventory_redacts_secret_files_and_extracts_scripts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "main.py").write_text("print('ok')\n", encoding="utf-8")
            (root / ".env").write_text("TOKEN=hidden\n", encoding="utf-8")
            (root / ".env.example").write_text("TOKEN=example\n", encoding="utf-8")
            (root / "package.json").write_text(
                json.dumps({"name": "fixture", "scripts": {"test": "echo test", "deploy": "tool --token=supersecretvalue123456789"}}),
                encoding="utf-8",
            )
            result = run_script("repo_inventory.py", "--root", str(root), "--filesystem", "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertGreaterEqual(data["scan_stats"]["secret_like_redacted"], 1)
            self.assertTrue(any(row["name"] == "test" for row in data["declared_package_scripts"]))
            deploy = next(row for row in data["declared_package_scripts"] if row["name"] == "deploy")
            self.assertIn("<redacted>", deploy["command"])
            self.assertNotIn("supersecretvalue", deploy["command"])
            all_paths = [path for values in data["important_paths"].values() for path in values]
            self.assertNotIn(".env", all_paths)

    def test_validator_accepts_grounded_router(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._create_valid_fixture(Path(tmp))
            result = run_script("validate_context_setup.py", "--root", str(root), "--strict")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("PASS", result.stdout)

    def test_validator_rejects_broken_link(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._create_valid_fixture(Path(tmp))
            index = root / "docs" / "agent" / "index.md"
            index.write_text(index.read_text(encoding="utf-8") + "\n[Broken](missing.md)\n", encoding="utf-8")
            result = run_script("validate_context_setup.py", "--root", str(root))
            self.assertEqual(result.returncode, 1)
            self.assertIn("broken-link", result.stdout)

    def test_budget_snapshot_comparison(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._create_valid_fixture(Path(tmp))
            snapshot = root / "baseline.json"
            first = run_script(
                "context_budget.py",
                "--root",
                str(root),
                "--snapshot-out",
                str(snapshot),
                "--json",
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            agents = root / "AGENTS.md"
            agents.write_text(agents.read_text(encoding="utf-8") + "\nAdditional durable rule.\n", encoding="utf-8")
            second = run_script(
                "context_budget.py",
                "--root",
                str(root),
                "--compare",
                str(snapshot),
                "--json",
            )
            self.assertEqual(second.returncode, 0, second.stderr)
            data = json.loads(second.stdout)
            self.assertGreater(data["comparison"]["always_loaded_delta"]["characters"], 0)

    @staticmethod
    def _create_valid_fixture(root: Path) -> Path:
        (root / "docs" / "agent" / "modules").mkdir(parents=True)
        (root / "src" / "auth").mkdir(parents=True)
        (root / "tests" / "auth").mkdir(parents=True)
        (root / "migrations").mkdir()
        (root / "src" / "auth" / "session.py").write_text("def validate(): pass\n", encoding="utf-8")
        (root / "tests" / "auth" / "test_session.py").write_text("def test_session(): pass\n", encoding="utf-8")
        (root / "migrations" / ".keep").write_text("", encoding="utf-8")
        (root / "AGENTS.md").write_text(
            """# Agent operating guide

This repository provides a sample API.

Read [`docs/agent/index.md`](docs/agent/index.md) before broad exploration.

## Progressive context protocol

1. Classify the task by domain.
2. Search symbols, paths, imports, and related tests.
3. Read the smallest relevant entrypoint and tests first.
4. Expand context only for a concrete unresolved question.

## Repository map

- `src/auth/`: authentication behavior
- `tests/auth/`: authentication tests
- `docs/agent/`: routed agent documentation

## Definition of done

Relevant tests pass and uncertainty is reported.
""",
            encoding="utf-8",
        )
        (root / "docs" / "agent" / "index.md").write_text(
            """# Agent context router

## Routes

| Task signals | Read first | Code roots | Tests | Overlays |
|---|---|---|---|---|
| login, session | [`modules/auth.md`](modules/auth.md) | `src/auth/` | `tests/auth/` | database for schema changes |

## Route precedence and overlays

Explicit paths take precedence. Authentication is primary; database is an overlay for schema work.

## Fallback route

For an unfamiliar task, search the named symbol and nearby tests before widening scope.

## Shared references

- [`architecture.md`](architecture.md)
- [`testing.md`](testing.md)
- [`task-template.md`](task-template.md)
- [`routing-cases.json`](routing-cases.json)
""",
            encoding="utf-8",
        )
        (root / "docs" / "agent" / "modules" / "auth.md").write_text(
            """# Authentication

## Responsibility

Owns login and session lifecycle.

## Entry points and code roots

- `src/auth/`: implementation

## Tests and verification

- `tests/auth/`: focused tests
""",
            encoding="utf-8",
        )
        (root / "docs" / "agent" / "architecture.md").write_text(
            "# Architecture context\n\nAuthentication is rooted in `src/auth/`.\n",
            encoding="utf-8",
        )
        (root / "docs" / "agent" / "testing.md").write_text(
            "# Testing context\n\nAuthentication tests live in `tests/auth/`.\n",
            encoding="utf-8",
        )
        (root / "docs" / "agent" / "task-template.md").write_text(
            "# Task handoff\n\n## Objective\n\nState the current objective.\n",
            encoding="utf-8",
        )
        routing_cases = {
            "version": 1,
            "cases": [
                {
                    "id": "auth-bug",
                    "task": "Fix a login session bug",
                    "expected_primary": "auth",
                    "expected_first_read": "docs/agent/modules/auth.md",
                    "expected_overlays": [],
                    "expected_code_roots": ["src/auth/"],
                },
                {
                    "id": "auth-schema",
                    "task": "Change persisted session schema",
                    "expected_primary": "auth",
                    "expected_first_read": "docs/agent/modules/auth.md",
                    "expected_overlays": ["database"],
                    "expected_code_roots": ["src/auth/", "migrations/"],
                },
                {
                    "id": "fallback",
                    "task": "Investigate UnknownCoordinator",
                    "expected_primary": "fallback",
                    "expected_first_read": "docs/agent/index.md",
                    "expected_overlays": [],
                    "expected_code_roots": [],
                },
            ],
        }
        (root / "docs" / "agent" / "routing-cases.json").write_text(
            json.dumps(routing_cases, indent=2) + "\n",
            encoding="utf-8",
        )
        return root


if __name__ == "__main__":
    unittest.main()
