from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "architectural-grilling"


class ArchitecturalGrillingPackageTests(unittest.TestCase):
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

        expected = [
            SKILL_ROOT / "agents" / "openai.yaml",
            SKILL_ROOT / "references" / "decision-lenses.md",
            SKILL_ROOT / "references" / "blueprint-format.md",
            SKILL_ROOT / "evals" / "evals.json",
        ]
        for path in expected:
            self.assertTrue(path.is_file(), str(path))

    def test_operating_invariants_are_explicit(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
        required_phrases = (
            "exactly one material question per turn",
            "clear recommended answer with every question",
            "investigate discoverable facts before asking",
            "living decision map",
            "blocks only its descendants",
            "do not implement",
            "do not build",
            "pre-mortem",
            "no `open` branch",
            "explicit confirmation",
        )
        for phrase in required_phrases:
            self.assertIn(phrase, text)

    def test_references_are_linked_and_metadata_is_consistent(self) -> None:
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        links = re.findall(r"\[[^\]]+\]\((references/[^)]+)\)", skill_text)
        self.assertEqual(
            set(links),
            {"references/decision-lenses.md", "references/blueprint-format.md"},
        )
        for link in links:
            self.assertTrue((SKILL_ROOT / link).is_file())

        metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Architectural Grilling"', metadata)
        self.assertIn("$architectural-grilling", metadata)
        short_description = re.search(r'short_description: "([^"]+)"', metadata)
        self.assertIsNotNone(short_description)
        self.assertGreaterEqual(len(short_description.group(1)), 25)  # type: ignore[union-attr]
        self.assertLessEqual(len(short_description.group(1)), 64)  # type: ignore[union-attr]

    def test_evals_cover_core_failure_modes(self) -> None:
        data = json.loads((SKILL_ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))
        self.assertEqual(data["skill_name"], "architectural-grilling")
        evals = data["evals"]
        self.assertGreaterEqual(len(evals), 5)
        self.assertEqual(len({case["id"] for case in evals}), len(evals))
        for case in evals:
            self.assertTrue(case["prompt"])
            self.assertTrue(case["expected_output"])
            self.assertGreaterEqual(len(case["assertions"]), 4)

        prompts = " ".join(case["prompt"].lower() for case in evals)
        for scenario in ("microservices", "legacy", "you decide everything", "ai agent", "stop"):
            self.assertIn(scenario, prompts)


if __name__ == "__main__":
    unittest.main()
