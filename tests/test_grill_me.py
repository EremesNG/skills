from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "productivity" / "grill-me"


class GrillMePackageTests(unittest.TestCase):
    def test_frontmatter_and_package_layout(self) -> None:
        skill_file = SKILL_ROOT / "SKILL.md"
        text = skill_file.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        _, frontmatter, body = text.split("---", 2)

        fields = re.findall(r"(?m)^([a-z][a-z0-9_-]*):[ \t]*(.*)$", frontmatter)
        values = dict(fields)
        self.assertTrue({"name", "description"}.issubset(values))
        self.assertTrue(set(values).issubset({
            "name", "description", "license", "compatibility", "metadata", "allowed-tools",
        }))
        self.assertEqual(values["name"], SKILL_ROOT.name)
        self.assertRegex(values["name"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertLessEqual(len(values["name"]), 64)
        self.assertLessEqual(len(values["description"]), 1024)
        self.assertLessEqual(len(text.splitlines()), 112)
        self.assertEqual(values["license"], "MIT")
        for field in ('author: EremesNG', 'version: "2.0.0"',
                      'repository: https://github.com/EremesNG/skills'):
            self.assertIn(field, frontmatter)
        for trigger in ('grill', 'stress-test', 'architecture', 'tech stack', 'product'):
            self.assertIn(trigger, values["description"])
        self.assertIn("mattpocock/skills", body)

        expected = [
            SKILL_ROOT / "agents" / "openai.yaml",
            SKILL_ROOT / "references" / "decision-lenses.md",
            SKILL_ROOT / "references" / "architecture-and-stack.md",
            SKILL_ROOT / "references" / "delivery-and-risk.md",
            SKILL_ROOT / "references" / "blueprint-format.md",
            SKILL_ROOT / "evals" / "evals.json",
        ]
        for path in expected:
            self.assertTrue(path.is_file(), str(path))

    def test_operating_invariants_are_explicit(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
        required_phrases = (
            "design tree", "frontier", "all independent", "number", "recommended answer",
            '"yes"', "prerequisites", "sub-agent", "do not implement", "user's language",
            "same execution", "never end", "empty response is not consent",
            "build now", "prepare cheaply", "defer until", "least complex",
            "explicit confirmation", "only blocked branches remain",
        )
        for phrase in required_phrases:
            self.assertIn(phrase, text)

    def test_rich_question_transport_is_explicit(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("## use the richest question transport", text)
        for phrase in (
            "2–4", "one-line trade-off", "conservative baseline", "defer",
            "native recommended flag", "never preselect", "previews", "multi-select",
            "free text", "evidence", "truly binary", "closure confirmation", "plain text",
        ):
            self.assertIn(phrase, text)

        data = json.loads((SKILL_ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))
        rich_cases = [case for case in data["evals"] if "rich question tool" in case["prompt"].lower()]
        self.assertTrue(rich_cases, "Missing structured-question evaluation")
        assertions = " ".join(rich_cases[0]["assertions"]).lower()
        for phrase in ("alternatives", "trade-off", "recommended flag", "preselect",
                       "preview", "multi-select", "free text", "binary", "closure"):
            self.assertIn(phrase, assertions)

    def test_references_are_linked_and_metadata_is_consistent(self) -> None:
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        links = re.findall(r"\[[^\]]+\]\((references/[^)]+)\)", skill_text)
        self.assertEqual(
            set(links),
            {
                "references/decision-lenses.md",
                "references/blueprint-format.md",
                "references/architecture-and-stack.md",
                "references/delivery-and-risk.md",
            },
        )
        for link in links:
            self.assertTrue((SKILL_ROOT / link).is_file())

        metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Grill Me"', metadata)
        self.assertIn("$grill-me", metadata)
        short_description = re.search(r'short_description: "([^"]+)"', metadata)
        self.assertIsNotNone(short_description)
        self.assertGreaterEqual(len(short_description.group(1)), 25)  # type: ignore[union-attr]
        self.assertLessEqual(len(short_description.group(1)), 64)  # type: ignore[union-attr]

    def test_all_package_markdown_links_resolve(self) -> None:
        for path in SKILL_ROOT.rglob("*.md"):
            for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                if "://" not in link and not link.startswith("#"):
                    self.assertTrue((path.parent / link.split("#", 1)[0]).exists(), (path, link))

    def test_evals_cover_core_failure_modes(self) -> None:
        data = json.loads((SKILL_ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))
        self.assertEqual(data["skill_name"], "grill-me")
        evals = data["evals"]
        self.assertGreaterEqual(len(evals), 5)
        self.assertEqual(len({case["id"] for case in evals}), len(evals))
        for case in evals:
            self.assertTrue(case["prompt"])
            self.assertTrue(case["expected_output"])
            self.assertGreaterEqual(len(case["assertions"]), 4)

        contracts = " ".join(str(case) for case in evals).lower()
        self.assertNotIn("exactly one material question", contracts)
        self.assertNotIn("exactly one question per call", contracts)
        self.assertIn("frontier", contracts)
        self.assertIn("same execution", contracts)
        self.assertIn("without a final response", contracts)
        for reference in ("architecture-and-stack.md", "blueprint-format.md", "delivery-and-risk.md"):
            self.assertIn(reference, contracts)

        prompts = " ".join(case["prompt"].lower() for case in evals)
        for scenario in ("microservices", "legacy", "you decide everything", "ai agent", "stop"):
            self.assertIn(scenario, prompts)


if __name__ == "__main__":
    unittest.main()
