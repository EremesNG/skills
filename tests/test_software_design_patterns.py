from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "code-quality" / "software-design-patterns"
EXPECTED_REFERENCES = (
    "references/principles.md",
    "references/creational.md",
    "references/structural.md",
    "references/behavioral.md",
    "references/game-programming.md",
    "references/game-ai.md",
    "references/ecs-data-oriented.md",
    "references/application-architecture.md",
    "references/distributed-systems.md",
    "references/sources.md",
    "references/platforms/unreal.md",
    "references/platforms/unity.md",
    "references/platforms/godot.md",
    "references/platforms/roblox.md",
    "references/platforms/general-stacks.md",
)


def split_fenced_code(text: str) -> tuple[str, list[str]]:
    outside = []
    info_strings = []
    fence_character = ""
    fence_length = 0
    for line in text.splitlines():
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence_character:
            if (
                match
                and match.group(1)[0] == fence_character
                and len(match.group(1)) >= fence_length
                and not match.group(2).strip()
            ):
                fence_character = ""
            outside.append("")
        elif match:
            fence_character = match.group(1)[0]
            fence_length = len(match.group(1))
            info_strings.append(match.group(2).strip())
            outside.append("")
        else:
            outside.append(line)
    return "\n".join(outside), info_strings


def markdown_links(text: str) -> list[str]:
    # Destinations may be angle-bracketed, contain balanced parentheses, or
    # have an optional Markdown title. Reference-style definitions count too.
    destination = r"(?:<([^>\n]+)>|((?:[^\s()\\]|\\.|\([^()\n]*\))+))"
    inline = (
        r"\[[^\]\n]*\]\(\s*" + destination
        + r'''(?:\s+(?:"[^"\n]*"|'[^'\n]*'|\([^\n)]*\)))?\s*\)'''
    )
    definitions = r"(?m)^ {0,3}\[[^\]\n]+\]:[ \t]*" + destination
    return [
        match.group(1) or match.group(2)
        for pattern in (inline, definitions)
        for match in re.finditer(pattern, text)
    ]


def heading_slugs(text: str) -> set[str]:
    headings = re.findall(r"(?m)^ {0,3}#{1,6}[ \t]+(.+?)[ \t]*#*[ \t]*$", text)
    headings.extend(
        re.findall(r"(?m)^([^\n]+)\n {0,3}(?:=+|-+)[ \t]*$", text)
    )
    return {
        re.sub(r"[^\w -]|_", "", heading.lower()).replace(" ", "-")
        for heading in headings
    }


class SoftwareDesignPatternsPackageTests(unittest.TestCase):
    def test_frontmatter_and_package_layout(self) -> None:
        skill_file = SKILL_ROOT / "SKILL.md"
        self.assertTrue(skill_file.is_file(), "software-design-patterns/SKILL.md is missing")
        text = skill_file.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        _, frontmatter, body = text.split("---", 2)

        fields = re.findall(r"(?m)^([a-z][a-z0-9_-]*):[ \t]*(.*)$", frontmatter)
        values = dict(fields)
        self.assertTrue({"name", "description", "license", "metadata"}.issubset(values))
        self.assertTrue(set(values).issubset({
            "name", "description", "license", "compatibility", "metadata", "allowed-tools",
        }))
        self.assertEqual(values["name"], SKILL_ROOT.name)
        self.assertRegex(values["name"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertLessEqual(len(values["name"]), 64)
        self.assertLessEqual(len(values["description"]), 1024)
        self.assertEqual(values["license"], "MIT")
        self.assertLess(len(body.splitlines()), 500)

        metadata_block = re.search(r"(?m)^metadata:[ \t]*\n((?:[ \t]+[^\n]*\n?)*)", frontmatter)
        self.assertIsNotNone(metadata_block)
        metadata = dict(re.findall(
            r"(?m)^  ([a-z][a-z0-9_-]*):[ \t]*([^\n]+)$",
            metadata_block.group(1),  # type: ignore[union-attr]
        ))
        for field in ("author", "version", "repository"):
            with self.subTest(metadata=field):
                self.assertIn(field, metadata)
                value = metadata[field].strip()
                self.assertTrue(value)
                if value.startswith(('"', "'")):
                    self.assertGreater(len(value), 2)
                    self.assertEqual(value[-1], value[0])
                else:
                    self.assertNotIn(value.lower(), {"null", "~", "true", "false", "yes", "no", "on", "off"})
                    self.assertFalse(value.startswith(("[", "{", "|", ">")))
                    self.assertNotRegex(value, r"(?i)^[+-]?(?:\d[\d_.]*(?:e[+-]?\d+)?|\.inf|\.nan)$")
                if field == "version":
                    self.assertRegex(value, r'''^(?:"[^"]+"|'[^']+')$''')

    def test_openai_metadata_exists(self) -> None:
        self.assertTrue(
            (SKILL_ROOT / "agents" / "openai.yaml").is_file(),
            "agents/openai.yaml is missing",
        )

    def test_evals_have_unique_ids_and_substantive_assertions(self) -> None:
        eval_file = SKILL_ROOT / "evals" / "evals.json"
        self.assertTrue(eval_file.is_file(), "evals/evals.json is missing")
        data = json.loads(eval_file.read_text(encoding="utf-8"))
        self.assertEqual(data["skill_name"], "software-design-patterns")
        evals = data["evals"]
        self.assertGreaterEqual(len(evals), 3)
        self.assertEqual(len({case["id"] for case in evals}), len(evals))
        for case in evals:
            with self.subTest(eval_id=case["id"]):
                self.assertTrue(case["prompt"])
                self.assertTrue(case["expected_output"])
                self.assertGreaterEqual(len(case["assertions"]), 3)

    def test_expected_reference_files_exist(self) -> None:
        for relative in EXPECTED_REFERENCES:
            with self.subTest(reference=relative):
                self.assertTrue((SKILL_ROOT / relative).is_file(), relative)

    def test_entry_point_links_every_reference(self) -> None:
        skill_file = SKILL_ROOT / "SKILL.md"
        self.assertTrue(skill_file.is_file(), "software-design-patterns/SKILL.md is missing")
        text, _ = split_fenced_code(skill_file.read_text(encoding="utf-8"))
        links = set()
        for link in markdown_links(text):
            parsed = urlsplit(link)
            if not parsed.scheme and not parsed.netloc and not parsed.path.startswith("/"):
                links.add((SKILL_ROOT / unquote(parsed.path)).resolve())
        for relative in EXPECTED_REFERENCES:
            with self.subTest(reference=relative):
                self.assertIn((SKILL_ROOT / relative).resolve(), links)

    def test_all_package_markdown_links_and_fragments_resolve(self) -> None:
        markdown_files = sorted(SKILL_ROOT.rglob("*.md"))
        self.assertTrue(markdown_files, "No package Markdown files found")
        for path in markdown_files:
            text, _ = split_fenced_code(path.read_text(encoding="utf-8"))
            for link in markdown_links(text):
                with self.subTest(source=path.relative_to(SKILL_ROOT), link=link):
                    parsed = urlsplit(link)
                    if parsed.scheme or parsed.netloc or parsed.path.startswith("/"):
                        continue
                    target = path.parent / unquote(parsed.path) if parsed.path else path
                    self.assertTrue(target.is_file(), f"{path}: missing target {link}")
                    if parsed.fragment:
                        target_text, _ = split_fenced_code(target.read_text(encoding="utf-8"))
                        self.assertIn(
                            unquote(parsed.fragment),
                            heading_slugs(target_text),
                            f"{path}: missing heading for {link}",
                        )

    def test_long_references_have_a_contents_heading(self) -> None:
        references = sorted((SKILL_ROOT / "references").rglob("*.md"))
        self.assertTrue(references, "No reference Markdown files found")
        for path in references:
            with self.subTest(reference=path.relative_to(SKILL_ROOT)):
                text = path.read_text(encoding="utf-8")
                if len(text.splitlines()) > 300:
                    outside, _ = split_fenced_code(text)
                    self.assertRegex(outside, r"(?m)^## Contents[ \t]*#*[ \t]*$")

    def test_readme_catalogs_and_installs_software_design_patterns(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("| `software-design-patterns` |", readme)
        self.assertIn(
            "npx skills add https://github.com/EremesNG/skills --skill software-design-patterns",
            readme,
        )

    def test_non_platform_references_use_only_text_or_bare_fences(self) -> None:
        references = sorted((SKILL_ROOT / "references").glob("*.md"))
        self.assertTrue(references, "No non-platform reference Markdown files found")
        for path in references:
            _, info_strings = split_fenced_code(path.read_text(encoding="utf-8"))
            for info in info_strings:
                with self.subTest(reference=path.relative_to(SKILL_ROOT), fence=info):
                    self.assertIn(info, {"", "text"})


if __name__ == "__main__":
    unittest.main()
