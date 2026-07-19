from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "simplify"


class SimplifyPackageTests(unittest.TestCase):
    def test_frontmatter_and_package_layout(self) -> None:
        skill_file = SKILL_ROOT / "SKILL.md"
        text = skill_file.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        _, frontmatter, body = text.split("---", 2)

        fields = re.findall(r"(?m)^([a-z][a-z0-9_-]*):\s*(.+)$", frontmatter)
        self.assertEqual([name for name, _ in fields], ["name", "description"])
        values = dict(fields)
        self.assertEqual(values["name"], SKILL_ROOT.name)
        self.assertRegex(values["name"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertLessEqual(len(values["name"]), 64)
        self.assertLessEqual(len(values["description"]), 1024)
        self.assertLess(len(body.splitlines()), 500)
        self.assertTrue((SKILL_ROOT / "evals" / "evals.json").is_file())

    def test_behavior_preservation_and_scope_invariants_are_explicit(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
        required_phrases = (
            "recent diff",
            "observable behavior",
            "unrelated changes",
            "public api",
            "error contracts",
            "one coherent simplification",
            "run the nearest relevant check",
            "stop when",
            "behavior preserved",
            "deferred",
        )
        for phrase in required_phrases:
            self.assertIn(phrase, text)

    def test_evals_cover_bounded_cleanup_failure_modes(self) -> None:
        data = json.loads(
            (SKILL_ROOT / "evals" / "evals.json").read_text(encoding="utf-8")
        )
        self.assertEqual(data["skill_name"], "simplify")
        evals = data["evals"]
        self.assertGreaterEqual(len(evals), 3)
        self.assertEqual(len({case["id"] for case in evals}), len(evals))
        for case in evals:
            self.assertTrue(case["prompt"])
            self.assertTrue(case["expected_output"])
            self.assertGreaterEqual(len(case["assertions"]), 3)

        prompts = " ".join(case["prompt"].lower() for case in evals)
        for scenario in (
            "unrelated edits",
            "deeply nested",
            "public api",
        ):
            self.assertIn(scenario, prompts)

    def test_readme_catalogs_and_installs_simplify(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("| `simplify` |", readme)
        self.assertIn(
            "npx skills add https://github.com/EremesNG/skills --skill simplify",
            readme,
        )


if __name__ == "__main__":
    unittest.main()
