from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "unity-developer"
INSPECTOR = SKILL_ROOT / "scripts" / "inspect_unity_project.py"


class UnityDeveloperEntryContractTests(unittest.TestCase):
    def test_entry_point_exposes_the_routed_professional_workflow(self) -> None:
        skill_file = SKILL_ROOT / "SKILL.md"
        self.assertTrue(skill_file.is_file(), "unity-developer/SKILL.md is missing")

        text = skill_file.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        _, frontmatter, body = text.split("---", 2)
        fields = re.findall(r"(?m)^([a-z][a-z0-9_-]*):\s*(.+)$", frontmatter)
        self.assertEqual([name for name, _ in fields], ["name", "description"])
        values = dict(fields)
        self.assertEqual(values["name"], "unity-developer")
        self.assertLessEqual(len(values["description"]), 1024)
        self.assertLess(len(body.splitlines()), 500)

        links = set(re.findall(r"\[[^\]]+\]\((references/[^)]+)\)", body))
        self.assertEqual(
            links,
            {
                "references/decision-framework.md",
                "references/design-patterns.md",
                "references/architecture.md",
                "references/ai-systems.md",
                "references/unity-engine-constraints.md",
                "references/sources.md",
            },
        )

        normalized = body.lower()
        for public_step in (
            "establish the unity context",
            "route only the needed knowledge",
            "choose proportionally",
            "implement behavior test-first",
            "verify honestly",
            "return contract",
        ):
            self.assertIn(public_step, normalized)

        for handoff_field in (
            "evidence",
            "decision",
            "rejected alternatives",
            "implementation",
            "verification",
            "risks",
        ):
            self.assertIn(handoff_field, normalized)

    def test_decision_framework_selects_the_smallest_sufficient_solution(self) -> None:
        reference = SKILL_ROOT / "references" / "decision-framework.md"
        self.assertTrue(reference.is_file(), "decision-framework.md is missing")

        text = reference.read_text(encoding="utf-8").lower()
        for section in (
            "problem classifier",
            "decision forces",
            "no-pattern gate",
            "option ladder",
            "compact decision record",
            "revisit triggers",
        ):
            self.assertIn(section, text)

        for force in (
            "change frequency",
            "ownership",
            "lifetime",
            "authoring",
            "determinism",
            "network authority",
            "frame budget",
            "testability",
        ):
            self.assertIn(force, text)

        for decision_field in (
            "evidence",
            "selected option",
            "rejected alternatives",
            "consequences",
            "revisit when",
        ):
            self.assertIn(decision_field, text)

    def test_pattern_reference_covers_selection_not_just_names(self) -> None:
        reference = SKILL_ROOT / "references" / "design-patterns.md"
        self.assertTrue(reference.is_file(), "design-patterns.md is missing")

        text = reference.read_text(encoding="utf-8").lower()
        for family in (
            "creational patterns",
            "structural patterns",
            "behavioral patterns",
            "architectural patterns",
            "optimization patterns",
        ):
            self.assertIn(family, text)

        for pattern in (
            "factory",
            "builder",
            "prototype",
            "singleton",
            "adapter",
            "bridge",
            "composite",
            "decorator",
            "facade",
            "flyweight",
            "proxy",
            "chain of responsibility",
            "command",
            "mediator",
            "memento",
            "observer",
            "state",
            "strategy",
            "dependency injection",
            "service locator",
            "mvp",
            "scriptableobject architecture",
            "broker chain",
            "specification",
            "dirty flag",
            "object pool",
            "spatial partition",
        ):
            self.assertIn(pattern, text)

        for selection_dimension in (
            "use when",
            "avoid when",
            "unity hazards",
            "useful composition",
        ):
            self.assertIn(selection_dimension, text)

    def test_openai_metadata_is_discoverable_and_invokes_the_skill_explicitly(self) -> None:
        metadata = SKILL_ROOT / "agents" / "openai.yaml"
        self.assertTrue(metadata.is_file(), "agents/openai.yaml is missing")

        text = metadata.read_text(encoding="utf-8")
        fields = dict(
            re.findall(
                r'(?m)^  (display_name|short_description|default_prompt):\s*"([^"]+)"$',
                text,
            )
        )
        self.assertEqual(set(fields), {"display_name", "short_description", "default_prompt"})
        self.assertEqual(fields["display_name"], "Unity Developer")
        self.assertGreaterEqual(len(fields["short_description"]), 25)
        self.assertLessEqual(len(fields["short_description"]), 64)
        self.assertIn("$unity-developer", fields["default_prompt"])
        self.assertIn("Unity", fields["default_prompt"])
        self.assertIn("C#", fields["default_prompt"])

    def test_evaluations_cover_three_substantive_professional_decisions(self) -> None:
        eval_file = SKILL_ROOT / "evals" / "evals.json"
        self.assertTrue(eval_file.is_file(), "evals/evals.json is missing")

        payload = json.loads(eval_file.read_text(encoding="utf-8"))
        self.assertEqual(payload["skill_name"], "unity-developer")
        evals = payload["evals"]
        self.assertEqual(len(evals), 3)
        self.assertEqual({case["id"] for case in evals}, {1, 2, 3})
        self.assertEqual(len({case["prompt"] for case in evals}), 3)
        for case in evals:
            self.assertGreaterEqual(len(case["prompt"]), 300)
            self.assertGreaterEqual(len(case["expected_output"]), 180)
            assertions = case.get("assertions", [])
            self.assertIsInstance(assertions, list)
            self.assertGreaterEqual(len(assertions), 7)
            self.assertTrue(all(isinstance(item, str) and item for item in assertions))

        combined = "\n".join(case["prompt"].lower() for case in evals)
        for scenario_marker in (
            "health",
            "domain reload",
            "gamemanager",
            "scriptableobject",
            "server-authoritative",
            "squad",
            "frame budget",
        ):
            self.assertIn(scenario_marker, combined)

    def test_readme_catalogs_installs_and_demonstrates_unity_developer(self) -> None:
        text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("catalog currently contains four skills", text.lower())
        self.assertIn(
            "| `unity-developer` |",
            text,
        )
        self.assertIn(
            "[`SKILL.md`](skills/unity-developer/SKILL.md)",
            text,
        )
        self.assertIn("### Remote installation: `unity-developer`", text)
        self.assertIn(
            "npx skills add https://github.com/EremesNG/skills --skill unity-developer",
            text,
        )
        self.assertIn("### Usage example: `unity-developer`", text)
        self.assertIn("Use unity-developer", text)
        discovery_paragraph = re.search(
            r"It currently discovers (.+?)\.\n",
            text,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(discovery_paragraph)
        self.assertIn("unity-developer", discovery_paragraph.group(1))  # type: ignore[union-attr]

    def test_ci_compiles_every_bundled_script_without_shell_globs(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "validate.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn('python-version: ["3.9", "3.13"]', workflow)
        self.assertNotIn("*.py", workflow)
        for script in (
            "skills/progressive-context-router/scripts/context_budget.py",
            "skills/progressive-context-router/scripts/repo_inventory.py",
            "skills/progressive-context-router/scripts/validate_context_setup.py",
            "skills/unity-developer/scripts/inspect_unity_project.py",
        ):
            self.assertIn(script, workflow)
        self.assertIn("python -m unittest discover -s tests -v", workflow)


class UnityProjectInspectorTests(unittest.TestCase):
    def write(self, root: Path, relative: str, content: str) -> Path:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def create_unity_project(self, root: Path) -> None:
        self.write(
            root,
            "ProjectSettings/ProjectVersion.txt",
            "m_EditorVersion: 6000.0.15f1\nm_EditorVersionWithRevision: 6000.0.15f1 (abc123)\n",
        )
        self.write(
            root,
            "Packages/manifest.json",
            json.dumps(
                {
                    "dependencies": {
                        "com.example.local": "file:../LocalPackage",
                        "com.unity.ai.navigation": "2.0.5",
                    }
                }
            ),
        )

    def snapshot_tree(self, root: Path) -> dict[str, tuple[int, int, str]]:
        snapshot: dict[str, tuple[int, int, str]] = {}
        for path in sorted((item for item in root.rglob("*") if item.is_file())):
            stat = path.stat()
            snapshot[path.relative_to(root).as_posix()] = (
                stat.st_size,
                stat.st_mtime_ns,
                hashlib.sha256(path.read_bytes()).hexdigest(),
            )
        return snapshot

    def run_inspector(self, root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(INSPECTOR), "--root", str(root), *extra],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_non_unity_root_returns_stable_json_and_exit_2(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = self.run_inspector(root, "--json")

        self.assertEqual(result.returncode, 2, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["schema_version"], 1)
        self.assertFalse(report["unity_detected"])
        self.assertEqual(report["unity_version"], None)
        self.assertIn("not a unity project", " ".join(report["warnings"]).lower())

    def test_valid_project_reports_version_packages_assemblies_tests_and_signals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_unity_project(root)
            self.write(root, "Assets/Game/Game.asmdef", '{"name":"Game.Runtime"}')
            self.write(
                root,
                "Assets/Tests/Game.Tests.asmdef",
                '{"name":"Game.Tests","optionalUnityReferences":["TestAssemblies"]}',
            )
            self.write(
                root,
                "Assets/Game/Enemy.cs",
                "public class Enemy { void Update() { GameObject.Find(\"Player\"); } }",
            )
            self.write(root, "Assets/Tests/EnemyTests.cs", "public class EnemyTests {}")

            result = self.run_inspector(root, "--json")

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["unity_detected"])
        self.assertEqual(report["unity_version"], "6000.0.15f1")
        self.assertEqual(
            report["packages"],
            [
                {"name": "com.example.local", "version": "file:../LocalPackage"},
                {"name": "com.unity.ai.navigation", "version": "2.0.5"},
            ],
        )
        self.assertEqual(report["inventory"]["csharp_files"]["count"], 2)
        self.assertEqual(report["inventory"]["assembly_definitions"]["count"], 2)
        self.assertEqual(report["inventory"]["test_assemblies"]["count"], 1)
        self.assertEqual(report["signals"]["scene_lookup"]["count"], 1)
        self.assertEqual(report["signals"]["frame_callbacks"]["count"], 1)

    def test_package_dependency_url_userinfo_is_redacted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_unity_project(root)
            self.write(
                root,
                "Packages/manifest.json",
                json.dumps(
                    {
                        "dependencies": {
                            "com.example.private": (
                                "https://build-user:SENTINEL_PASSWORD@"
                                "packages.example.com/repository.git?path=/Package"
                            )
                        }
                    }
                ),
            )

            result = self.run_inspector(root, "--json")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("SENTINEL_PASSWORD", result.stdout)
        self.assertNotIn("build-user", result.stdout)
        report = json.loads(result.stdout)
        self.assertEqual(
            report["packages"],
            [
                {
                    "name": "com.example.private",
                    "version": (
                        "https://REDACTED@packages.example.com/"
                        "repository.git?path=/Package"
                    ),
                }
            ],
        )

    def test_package_dependency_query_fragment_and_fallback_secrets_are_redacted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_unity_project(root)
            self.write(
                root,
                "Packages/manifest.json",
                json.dumps(
                    {
                        "dependencies": {
                            "com.example.fallback": (
                                "channel=beta&client_secret=SENTINEL_FALLBACK"
                            ),
                            "com.example.query": (
                                "https://packages.example.com/repository.git"
                                "?token=SENTINEL_QUERY&path=/Package"
                                "#access_token=SENTINEL_FRAGMENT"
                            ),
                        }
                    }
                ),
            )

            json_result = self.run_inspector(root, "--json")
            human_result = self.run_inspector(root)

        self.assertEqual(json_result.returncode, 0, json_result.stderr)
        self.assertEqual(human_result.returncode, 0, human_result.stderr)
        for sentinel in (
            "SENTINEL_FALLBACK",
            "SENTINEL_QUERY",
            "SENTINEL_FRAGMENT",
        ):
            self.assertNotIn(sentinel, json_result.stdout)
            self.assertNotIn(sentinel, human_result.stdout)
        report = json.loads(json_result.stdout)
        self.assertEqual(
            report["packages"],
            [
                {
                    "name": "com.example.fallback",
                    "version": "channel=beta&client_secret=REDACTED",
                },
                {
                    "name": "com.example.query",
                    "version": (
                        "https://packages.example.com/repository.git"
                        "?token=REDACTED&path=/Package"
                        "#access_token=REDACTED"
                    ),
                },
            ],
        )

    def test_malformed_metadata_is_reported_without_aborting_inspection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_unity_project(root)
            self.write(root, "ProjectSettings/ProjectVersion.txt", "not-an-editor-version")
            self.write(root, "Packages/manifest.json", "{")
            self.write(root, "Assets/Broken.asmdef", "{")

            result = self.run_inspector(root, "--json")

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["unity_version"], None)
        self.assertEqual(report["packages"], [])
        self.assertEqual(report["inventory"]["assembly_definitions"]["count"], 1)
        warnings = "\n".join(report["warnings"])
        self.assertIn("ProjectSettings/ProjectVersion.txt", warnings)
        self.assertIn("Packages/manifest.json", warnings)
        self.assertIn("Assets/Broken.asmdef", warnings)

    def test_generated_cache_build_vcs_and_ide_paths_are_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_unity_project(root)
            self.write(root, "Assets/Runtime/Keep.cs", "class Keep { void Run() { Destroy(this); } }")
            self.write(root, "Packages/com.example.embedded/Runtime/KeepToo.cs", "class KeepToo {}")
            for relative in (
                "Assets/Generated/Generated.cs",
                "Assets/Build/PlayerCode.cs",
                "Assets/.idea/Indexed.cs",
                "Packages/com.example.embedded/obj/Compiled.cs",
                "Packages/com.example.embedded/.git/Tracked.cs",
                "Library/Cache.cs",
                "Temp/Transient.cs",
                "Logs/Logged.cs",
            ):
                self.write(root, relative, "class Excluded { void Update() {} }")

            result = self.run_inspector(root, "--json", "--max-samples", "20")

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["inventory"]["csharp_files"]["count"], 2)
        self.assertEqual(
            report["inventory"]["csharp_files"]["samples"],
            ["Assets/Runtime/Keep.cs", "Packages/com.example.embedded/Runtime/KeepToo.cs"],
        )
        self.assertEqual(report["signals"]["frame_callbacks"]["count"], 0)
        self.assertEqual(report["signals"]["spawn_destroy"]["count"], 1)

    def test_secret_like_paths_and_all_source_values_are_not_disclosed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_unity_project(root)
            self.write(
                root,
                "Assets/Runtime/Player.cs",
                'class Player { const string DebugMarker = "NEVER-EMIT-THIS"; void Update() {} }',
            )
            self.write(
                root,
                "Assets/Secrets/ApiKeys.cs",
                'class ApiKeys { string Value = "TOP-SECRET-VALUE"; void Run() { GameObject.Find("P"); } }',
            )
            self.write(
                root,
                "Packages/com.example.embedded/Runtime/Credentials.cs",
                'class Credentials { string Token = "ANOTHER-SECRET"; }',
            )

            result = self.run_inspector(root, "--json", "--max-samples", "20")

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["inventory"]["csharp_files"]["count"], 1)
        self.assertEqual(
            report["inventory"]["csharp_files"]["samples"],
            ["Assets/Runtime/Player.cs"],
        )
        self.assertEqual(report["signals"]["scene_lookup"]["count"], 0)
        for sensitive in (
            "Secrets",
            "Credentials.cs",
            "NEVER-EMIT-THIS",
            "TOP-SECRET-VALUE",
            "ANOTHER-SECRET",
        ):
            self.assertNotIn(sensitive, result.stdout)

    def test_json_is_deterministic_bounded_and_uses_the_documented_key_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_unity_project(root)
            self.write(root, "Assets/Zeta.cs", "class Zeta { void Update() {} }")
            self.write(root, "Assets/alpha.cs", "class Alpha { void Update() {} }")

            first = self.run_inspector(root, "--json", "--max-samples", "1")
            second = self.run_inspector(root, "--json", "--max-samples", "1")

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(first.stdout, second.stdout)
        report = json.loads(first.stdout)
        self.assertEqual(
            list(report),
            [
                "schema_version",
                "root",
                "unity_detected",
                "unity_version",
                "packages",
                "inventory",
                "signals",
                "warnings",
            ],
        )
        self.assertEqual(report["inventory"]["csharp_files"]["count"], 2)
        self.assertEqual(report["inventory"]["csharp_files"]["samples"], ["Assets/alpha.cs"])
        self.assertEqual(report["signals"]["frame_callbacks"]["count"], 2)
        self.assertEqual(report["signals"]["frame_callbacks"]["samples"], ["Assets/alpha.cs"])

    def test_human_output_summarizes_inventory_and_labels_signals_as_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_unity_project(root)
            self.write(
                root,
                "Assets/Loader.cs",
                "class Loader { async void Load() { Resources.Load(\"Level\"); } }",
            )

            result = self.run_inspector(root)

        self.assertEqual(result.returncode, 0, result.stderr)
        for expected in (
            "Unity project inspection",
            "Unity version: 6000.0.15f1",
            "Declared packages: 2",
            "C# files: 1",
            "Assembly definitions: 0",
            "Test assemblies: 0",
            "async void: 1",
            "resource loading: 1",
            "Signals are investigation leads, not diagnoses.",
            "Assets/Loader.cs",
        ):
            self.assertIn(expected, result.stdout)

    def test_inspection_does_not_mutate_the_project_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_unity_project(root)
            self.write(root, "Assets/Runtime/Actor.cs", "class Actor { void Update() {} }")
            self.write(root, "Assets/Runtime/Actor.asmdef", '{"name":"Actor.Runtime"}')
            before = self.snapshot_tree(root)

            result = self.run_inspector(root, "--json")

            after = self.snapshot_tree(root)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(after, before)


class UnityDeveloperReferenceContractTests(unittest.TestCase):

    def test_sources_define_authority_and_version_drift_rules(self) -> None:
        reference = SKILL_ROOT / "references" / "sources.md"
        self.assertTrue(reference.is_file(), "sources.md is missing")

        text = reference.read_text(encoding="utf-8").lower()
        for supplied_source in (
            "patrones de programación de videojuegos en unity.docx",
            "https://www.unitydesignpatterns.com/",
            "rmyndharis/antigravity-skills",
        ):
            self.assertIn(supplied_source, text)

        for official_topic in (
            "scriptableobject",
            "serializereference",
            "domain reload",
            "assembly definitions",
            "test framework",
            "target device",
            "objectpool",
            "ai navigation",
            "unity behavior",
            "ml-agents",
            "sentis",
        ):
            self.assertIn(official_topic, text)

        for invariant in (
            "accessed 2026-08-01",
            "authority order",
            "version-matched",
            "secondary sources do not override",
            "refresh when",
        ):
            self.assertIn(invariant, text)

    def test_architecture_reference_makes_ownership_and_framework_costs_explicit(self) -> None:
        reference = SKILL_ROOT / "references" / "architecture.md"
        self.assertTrue(reference.is_file(), "architecture.md is missing")

        text = reference.read_text(encoding="utf-8").lower()
        for architectural_surface in (
            "composition root",
            "ownership and lifetime",
            "dependency direction",
            "messaging",
            "ui architecture",
            "scriptableobject data",
            "scene boundaries",
            "assembly definitions",
            "dependency injection",
            "ecs/dots",
        ):
            self.assertIn(architectural_surface, text)

        for invariant in (
            "one owner",
            "initialization",
            "teardown",
            "plain c#",
            "authored data",
            "runtime state",
            "adoption gate",
            "do not adopt",
        ):
            self.assertIn(invariant, text)

    def test_engine_constraints_cover_unity_specific_failure_modes(self) -> None:
        reference = SKILL_ROOT / "references" / "unity-engine-constraints.md"
        self.assertTrue(reference.is_file(), "unity-engine-constraints.md is missing")

        text = reference.read_text(encoding="utf-8").lower()
        for engine_surface in (
            "destroyed unity objects",
            "awake",
            "onenable",
            "start",
            "ondisable",
            "ondestroy",
            "domain reload",
            "serializereference",
            "scriptableobject",
            "async",
            "main thread",
            "pool reset",
            "determinism",
            "editmode",
            "playmode",
            "target device",
        ):
            self.assertIn(engine_surface, text)

        for safeguard in (
            "subscribe and unsubscribe",
            "static reset",
            "cancellationtoken",
            "plain c# seam",
            "measure before",
            "representative build",
            "do not claim",
        ):
            self.assertIn(safeguard, text)

    def test_ai_reference_selects_complete_systems_under_game_constraints(self) -> None:
        reference = SKILL_ROOT / "references" / "ai-systems.md"
        self.assertTrue(reference.is_file(), "ai-systems.md is missing")

        text = reference.read_text(encoding="utf-8").lower()
        for pipeline_stage in (
            "perception",
            "memory",
            "decision",
            "action",
            "navigation",
            "animation",
        ):
            self.assertIn(pipeline_stage, text)

        for approach in (
            "direct rules",
            "finite state machine",
            "hierarchical finite state machine",
            "behavior tree",
            "utility ai",
            "goap",
            "specification",
            "ml-agents",
            "sentis",
            "hybrid",
        ):
            self.assertIn(approach, text)

        for selection_dimension in (
            "authoring",
            "observability",
            "determinism",
            "network authority",
            "scheduling budget",
            "save and replay",
            "measurable budget",
        ):
            self.assertIn(selection_dimension, text)


if __name__ == "__main__":
    unittest.main()
