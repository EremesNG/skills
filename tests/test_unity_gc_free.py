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
SKILL_ROOT = REPO_ROOT / "skills" / "game-dev" / "unity-gc-free"
INSPECTOR = SKILL_ROOT / "scripts" / "inspect_unity_gc.py"


class UnityGcFreeEntryContractTests(unittest.TestCase):
    def test_entry_point_exposes_the_measured_routed_workflow(self) -> None:
        skill_file = SKILL_ROOT / "SKILL.md"
        self.assertTrue(skill_file.is_file(), "unity-gc-free/SKILL.md is missing")

        text = skill_file.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        _, frontmatter, body = text.split("---", 2)
        fields = re.findall(r"(?m)^([a-z][a-z0-9_-]*):[ \t]*(.*)$", frontmatter)
        values = dict(fields)
        self.assertTrue({"name", "description"}.issubset(values))
        self.assertTrue(set(values).issubset({
            "name", "description", "license", "compatibility", "metadata", "allowed-tools",
        }))
        self.assertEqual(values["name"], "unity-gc-free")
        self.assertLessEqual(len(values["description"]), 1024)
        self.assertLess(len(body.splitlines()), 500)

        links = set(re.findall(r"\[[^\]]+\]\((references/[^)]+)\)", body))
        self.assertEqual(
            links,
            {
                "references/allocation-contract.md",
                "references/hotspot-catalog.md",
                "references/library-matrix.md",
                "references/pooling-and-buffers.md",
                "references/native-memory.md",
                "references/migration-playbook.md",
                "references/sources.md",
            },
        )

        normalized = body.lower()
        for public_step in (
            "define the allocation contract",
            "inspect the evidence",
            "route only needed knowledge",
            "select the smallest compatible change",
            "migrate one measured source",
            "verify in the target player",
            "return contract",
        ):
            self.assertIn(public_step, normalized)

        for response_field in (
            "context and scope",
            "allocation contract",
            "evidence",
            "decision",
            "ownership and lifecycle",
            "implementation",
            "verification",
            "risks",
        ):
            self.assertIn(response_field, normalized)

    def test_entry_keeps_evaluation_discovered_compatibility_costs_explicit(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
        for guard in (
            "installed manifest/lock",
            "playerloop injection or reinjection",
            "ecs",
            "native physics memory",
            "deferred versus eager execution",
            "unitask first-step",
            "use-after-return red test",
            "awaitable continuation thread",
            "no simultaneous semantic changes",
        ):
            self.assertIn(guard, text)

    def test_openai_metadata_is_discoverable_and_invokes_the_skill(self) -> None:
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
        self.assertEqual(fields["display_name"], "Unity GC-Free")
        self.assertGreaterEqual(len(fields["short_description"]), 25)
        self.assertLessEqual(len(fields["short_description"]), 64)
        self.assertIn("$unity-gc-free", fields["default_prompt"])
        self.assertIn("managed allocations", fields["default_prompt"].lower())
        self.assertIn("target player", fields["default_prompt"].lower())

    def test_evaluations_cover_diagnosis_selection_and_safe_migration(self) -> None:
        eval_file = SKILL_ROOT / "evals" / "evals.json"
        self.assertTrue(eval_file.is_file(), "evals/evals.json is missing")

        payload = json.loads(eval_file.read_text(encoding="utf-8"))
        self.assertEqual(payload["skill_name"], "unity-gc-free")
        evals = payload["evals"]
        self.assertEqual(len(evals), 3)
        self.assertEqual({case["id"] for case in evals}, {1, 2, 3})
        self.assertEqual(len({case["prompt"] for case in evals}), 3)
        for case in evals:
            self.assertGreaterEqual(len(case["prompt"]), 300)
            self.assertGreaterEqual(len(case["expected_output"]), 180)
            assertions = case.get("assertions", [])
            self.assertIsInstance(assertions, list)
            self.assertGreaterEqual(len(assertions), 8)
            self.assertTrue(all(isinstance(item, str) and item for item in assertions))

        combined = "\n".join(case["prompt"].lower() for case in evals)
        for scenario_marker in (
            "development player",
            "gc.alloc",
            "warm-up",
            "il2cpp",
            "zlinq",
            "unitask",
            "primetween",
            "addressables",
            "full buffer",
            "pool",
        ):
            self.assertIn(scenario_marker, combined)

    def test_readme_catalogs_installs_and_demonstrates_unity_gc_free(self) -> None:
        text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("catalog currently contains six skills", text.lower())
        self.assertIn("| `unity-gc-free` |", text)
        self.assertIn("[`SKILL.md`](skills/game-dev/unity-gc-free/SKILL.md)", text)
        self.assertIn("### Remote installation: `unity-gc-free`", text)
        self.assertIn(
            "npx skills add https://github.com/EremesNG/skills --skill unity-gc-free",
            text,
        )
        self.assertIn("### Usage example: `unity-gc-free`", text)
        self.assertIn("Use unity-gc-free", text)
        discovery_paragraph = re.search(r"It currently discovers (.+?)\.\n", text, flags=re.DOTALL)
        self.assertIsNotNone(discovery_paragraph)
        discovered = discovery_paragraph.group(1)  # type: ignore[union-attr]
        self.assertIn("unity-developer", discovered)
        self.assertIn("unity-gc-free", discovered)

    def test_ci_and_local_commands_compile_the_inspector_explicitly(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "validate.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn('python-version: ["3.9", "3.13"]', workflow)
        self.assertNotIn("*.py", workflow)
        self.assertIn("skills/game-dev/unity-gc-free/scripts/inspect_unity_gc.py", workflow)
        self.assertIn("skills/game-dev/unity-developer/scripts/inspect_unity_project.py", workflow)
        self.assertIn("python -m unittest discover -s tests -v", workflow)

        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("skills/game-dev/unity-gc-free/scripts/inspect_unity_gc.py", readme)


class UnityGcFreeReferenceContractTests(unittest.TestCase):
    def test_allocation_contract_scopes_and_measures_the_claim(self) -> None:
        reference = SKILL_ROOT / "references" / "allocation-contract.md"
        self.assertTrue(reference.is_file(), "allocation-contract.md is missing")

        text = reference.read_text(encoding="utf-8").lower()
        for section in (
            "scope the workload",
            "separate the cost domains",
            "measurement protocol",
            "budget template",
            "evidence classification",
            "success gate",
        ):
            self.assertIn(section, text)

        for invariant in (
            "0 managed bytes",
            "gc.alloc",
            "managed heap",
            "native allocation",
            "retained memory",
            "cpu time",
            "warm-up",
            "capacity",
            "sample window",
            "all relevant threads",
            "development player",
            "release player",
            "profilerrecorder",
            "call stacks",
            "editor-only",
            "provisional",
            "first-use",
            "exception path",
        ):
            self.assertIn(invariant, text)

        for template_field in (
            "workload:",
            "environment:",
            "warm-up:",
            "capacity state:",
            "measurement window:",
            "managed allocation budget:",
            "preserved behavior:",
            "other budgets:",
        ):
            self.assertIn(template_field, text)

    def test_sources_record_primary_authority_and_freshness_limits(self) -> None:
        reference = SKILL_ROOT / "references" / "sources.md"
        self.assertTrue(reference.is_file(), "sources.md is missing")

        text = reference.read_text(encoding="utf-8")
        normalized = text.lower()
        direct_urls = re.findall(r"https://[^\s)>]+", text)
        self.assertGreaterEqual(len(set(direct_urls)), 20)

        for provenance_guard in (
            "accessed 2026-08-02",
            "authority order",
            "primary sources",
            "version-matched",
            "observed target-player",
            "project-authored benchmark",
            "refresh when",
            "not mit",
            "version conflict",
            "maintenance status",
        ):
            self.assertIn(provenance_guard, normalized)

        for source_family in (
            "profilerrecorder",
            "objectpool",
            "awaitable",
            "nativecontainer",
            "addressables",
            "zlinq",
            "unitask",
            "primetween",
            "zstring",
            "memorypack",
            "messagepack-csharp",
            "r3",
            "observablecollections",
            "arraypool",
            "collections.pooled",
        ):
            self.assertIn(source_family, normalized)

    def test_hotspot_catalog_is_broad_but_never_a_blanket_ban(self) -> None:
        reference = SKILL_ROOT / "references" / "hotspot-catalog.md"
        self.assertTrue(reference.is_file(), "hotspot-catalog.md is missing")

        text = reference.read_text(encoding="utf-8").lower()
        for section in (
            "locate the measured hot path",
            "managed-language hotspots",
            "unity api hotspots",
            "qualification rules",
        ):
            self.assertIn(section, text)

        for family in (
            "strings",
            "logging",
            "closures",
            "delegates",
            "boxing",
            "params",
            "iterators",
            "linq",
            "arrays",
            "collections",
            "coroutines",
            "async",
            "exceptions",
            "physics",
            "collision",
            "input",
            "mesh",
            "renderer",
            "ui",
            "reflection",
            "runtime object churn",
        ):
            self.assertIn(family, text)

        for qualification in (
            "allocation boundary",
            "evidence check",
            "version-sensitive",
            "not automatically a defect",
            "concrete array",
            "interface conversion",
            "stringbuilder.tostring",
            "getcomponent",
            "unity 6",
            "measure",
        ):
            self.assertIn(qualification, text)

    def test_library_matrix_requires_semantic_and_compatibility_fit(self) -> None:
        reference = SKILL_ROOT / "references" / "library-matrix.md"
        self.assertTrue(reference.is_file(), "library-matrix.md is missing")

        text = reference.read_text(encoding="utf-8").lower()
        for tool in (
            "direct/built-in",
            "zlinq",
            "awaitable",
            "unitask",
            "primetween",
            "zstring",
            "memorypack",
            "messagepack-csharp",
            "r3",
            "observablecollections",
            "arraypool",
        ):
            self.assertIn(tool, text)

        for dimension in (
            "fit",
            "allocation boundary",
            "semantic contract",
            "compatibility",
            "lifecycle",
            "platform/aot/threading",
            "provenance/license",
            "avoid when",
            "revisit when",
        ):
            self.assertIn(dimension, text)

        for caveat in (
            "single-await",
            "playerloop",
            "captured closure",
            "non-reusable",
            "overwrite",
            "final string",
            "final output",
            "source generation",
            "il2cpp",
            "dispose",
            "not mit",
            "webgl",
            "pin the exact",
        ):
            self.assertIn(caveat, text)

    def test_pooling_reference_defines_ownership_capacity_and_teardown(self) -> None:
        reference = SKILL_ROOT / "references" / "pooling-and-buffers.md"
        self.assertTrue(reference.is_file(), "pooling-and-buffers.md is missing")

        text = reference.read_text(encoding="utf-8").lower()
        for pool_kind in (
            "unityengine.pool",
            "object pooling",
            "collection reuse",
            "arraypool",
            "caller-owned buffers",
            "addressables",
        ):
            self.assertIn(pool_kind, text)

        for contract in (
            "capacity",
            "warm-up",
            "get",
            "release",
            "reset",
            "destroy",
            "overflow",
            "exhaustion",
            "double return",
            "use after return",
            "full-buffer",
            "truncation",
            "ordering",
            "fallback",
            "not thread-safe",
            "clear retained references",
            "subscriptions",
            "cancellation",
            "reference count",
            "scene unload",
            "domain reload",
            "telemetry",
            "memory cap",
        ):
            self.assertIn(contract, text)

    def test_native_memory_reference_keeps_unmanaged_ownership_explicit(self) -> None:
        reference = SKILL_ROOT / "references" / "native-memory.md"
        self.assertTrue(reference.is_file(), "native-memory.md is missing")

        text = reference.read_text(encoding="utf-8").lower()
        for concept in (
            "nativearray",
            "nativelist",
            "nativecontainer",
            "managed allocation",
            "native allocation",
            "allocator.temp",
            "same frame",
            "allocator.tempjob",
            "four frames",
            "allocator.persistent",
            "iscreated",
            "dispose",
            "alias",
            "safety system",
            "job dependency",
            "complete",
            "burst",
            "fixedstring",
            "local adoption",
            "does not require ecs",
            "cpu cost",
            "leak",
        ):
            self.assertIn(concept, text)

    def test_migration_playbook_requires_functional_and_allocation_evidence(self) -> None:
        reference = SKILL_ROOT / "references" / "migration-playbook.md"
        self.assertTrue(reference.is_file(), "migration-playbook.md is missing")

        text = reference.read_text(encoding="utf-8").lower()
        for stage in (
            "one-source vertical slice",
            "functional red",
            "allocation red",
            "green functional",
            "green allocation",
            "representative target player",
            "rollback",
            "success gate",
        ):
            self.assertIn(stage, text)

        for behavior in (
            "result values",
            "ordering",
            "timing",
            "exception",
            "cancellation",
            "thread affinity",
            "owner lifecycle",
            "full-buffer",
            "overflow",
            "warm-up",
            "all relevant threads",
        ):
            self.assertIn(behavior, text)

        for migration in (
            "linq / zlinq",
            "coroutine / async",
            "dotween / primetween",
            "pooling",
            "native container",
        ):
            self.assertIn(migration, text)


class UnityGcFreeInspectorTests(unittest.TestCase):
    def write(self, root: Path, relative: str, content: str) -> Path:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def create_unity_project(self, root: Path) -> None:
        self.write(
            root,
            "ProjectSettings/ProjectVersion.txt",
            "m_EditorVersion: 6000.0.15f1\n",
        )
        self.write(root, "Packages/manifest.json", '{"dependencies": {}}')

    def snapshot_tree(self, root: Path) -> dict[str, tuple[int, int, str]]:
        snapshot: dict[str, tuple[int, int, str]] = {}
        for path in sorted(item for item in root.rglob("*") if item.is_file()):
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
            result = self.run_inspector(Path(tmp), "--json")

        self.assertEqual(result.returncode, 2, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(
            list(report),
            [
                "schema_version",
                "root",
                "unity_detected",
                "unity_version",
                "scripting_backend_hints",
                "relevant_packages",
                "inventory",
                "signals",
                "warnings",
            ],
        )
        self.assertEqual(report["schema_version"], 1)
        self.assertFalse(report["unity_detected"])
        self.assertEqual(report["unity_version"], None)
        self.assertEqual(report["scripting_backend_hints"], [])
        self.assertIn("not a unity project", " ".join(report["warnings"]).lower())

    def test_valid_metadata_reports_raw_backend_hints_and_relevant_packages(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_unity_project(root)
            self.write(
                root,
                "ProjectSettings/ProjectSettings.asset",
                "PlayerSettings:\n  scriptingBackend:\n    Standalone: 0\n    Android: 1\n",
            )
            self.write(
                root,
                "Packages/manifest.json",
                json.dumps(
                    {
                        "dependencies": {
                            "com.example.unrelated": "1.0.0",
                            "com.unity.collections": "2.6.0",
                            "com.cysharp.zlinq": "1.5.6",
                            "com.cysharp.unitask": "https://github.com/Cysharp/UniTask.git?path=src/UniTask/Assets/Plugins/UniTask",
                        }
                    }
                ),
            )

            result = self.run_inspector(root, "--json")

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["unity_version"], "6000.0.15f1")
        self.assertEqual(
            report["scripting_backend_hints"],
            [
                {"target": "Android", "raw_value": "1"},
                {"target": "Standalone", "raw_value": "0"},
            ],
        )
        self.assertEqual(
            [item["name"] for item in report["relevant_packages"]],
            ["com.cysharp.unitask", "com.cysharp.zlinq", "com.unity.collections"],
        )
        self.assertNotIn("com.example.unrelated", result.stdout)
        self.assertIn("raw scripting-backend values", " ".join(report["warnings"]).lower())

    def test_relevant_package_coordinates_are_sanitized(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_unity_project(root)
            self.write(
                root,
                "Packages/manifest.json",
                json.dumps(
                    {
                        "dependencies": {
                            "com.cysharp.zlinq": (
                                "https://build-user:SENTINEL_PASSWORD@packages.example/"
                                "zlinq.git?token=SENTINEL_QUERY&path=/Package"
                            )
                        }
                    }
                ),
            )

            result = self.run_inspector(root, "--json")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("SENTINEL_PASSWORD", result.stdout)
        self.assertNotIn("SENTINEL_QUERY", result.stdout)
        self.assertNotIn("build-user", result.stdout)
        report = json.loads(result.stdout)
        self.assertEqual(
            report["relevant_packages"],
            [
                {
                    "name": "com.cysharp.zlinq",
                    "version": (
                        "https://REDACTED@packages.example/zlinq.git"
                        "?token=REDACTED&path=/Package"
                    ),
                }
            ],
        )

    def test_malformed_optional_metadata_warns_without_aborting(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_unity_project(root)
            self.write(root, "ProjectSettings/ProjectVersion.txt", "not-a-version\n")
            self.write(
                root,
                "ProjectSettings/ProjectSettings.asset",
                "PlayerSettings:\n  scriptingBackend:\n    BrokenEntry\n",
            )
            self.write(root, "Packages/manifest.json", "{")

            result = self.run_inspector(root, "--json")

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["unity_version"], None)
        self.assertEqual(report["scripting_backend_hints"], [])
        self.assertEqual(report["relevant_packages"], [])
        warnings = "\n".join(report["warnings"])
        self.assertIn("ProjectSettings/ProjectVersion.txt", warnings)
        self.assertIn("ProjectSettings/ProjectSettings.asset", warnings)
        self.assertIn("Packages/manifest.json", warnings)

    def test_scan_emits_all_eleven_bounded_signal_families(self) -> None:
        source = """
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using Unity.Collections;
class AllocationSignals {
    IEnumerator Run() { yield return null; }
    void Tick() {
        var filtered = values.Where(value => value > 0);
        DOTween.Sequence();
        var spawned = Instantiate(prefab);
        Destroy(spawned);
        var hits = Physics.RaycastAll(ray);
        var copiedVertices = mesh.vertices;
        var scratch = new List<int>();
        var label = $"Score: {score}";
        Debug.Log(label);
        var native = new NativeArray<int>(8, Allocator.Temp);
    }
}
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_unity_project(root)
            self.write(root, "Assets/Runtime/AllocationSignals.cs", source)

            result = self.run_inspector(root, "--json", "--max-samples", "20")

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(
            list(report["signals"]),
            [
                "allocating_physics_queries",
                "array_return_apis",
                "coroutines",
                "dotween",
                "lambdas",
                "logging",
                "native_containers",
                "spawn_destroy",
                "string_formatting",
                "system_linq",
                "temporary_collections",
            ],
        )
        for summary in report["signals"].values():
            self.assertEqual(summary["count"], 1)
            self.assertEqual(summary["samples"], ["Assets/Runtime/AllocationSignals.cs"])

    def test_scan_excludes_generated_cache_build_vcs_ide_and_secret_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_unity_project(root)
            self.write(root, "Assets/Runtime/Keep.cs", "class Keep { void Run() { Destroy(this); } }")
            self.write(
                root,
                "Packages/com.example.embedded/Runtime/KeepToo.cs",
                "class KeepToo { void Run() { Destroy(this); } }",
            )
            for relative in (
                "Assets/Generated/Generated.cs",
                "Assets/Build/PlayerCode.cs",
                "Assets/Cache/Cached.cs",
                "Assets/.idea/Indexed.cs",
                "Assets/.git/Tracked.cs",
                "Packages/com.example.embedded/obj/Compiled.cs",
                "Packages/com.example.embedded/.vscode/Editor.cs",
                "Assets/Secrets/Private.cs",
            ):
                self.write(root, relative, "class Excluded { void Run() { Destroy(this); } }")

            result = self.run_inspector(root, "--json", "--max-samples", "20")

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["inventory"]["csharp_files"]["count"], 2)
        self.assertEqual(
            report["inventory"]["csharp_files"]["samples"],
            ["Assets/Runtime/Keep.cs", "Packages/com.example.embedded/Runtime/KeepToo.cs"],
        )
        self.assertEqual(report["signals"]["spawn_destroy"]["count"], 2)
        self.assertNotIn("Excluded", result.stdout)
        self.assertNotIn("Secrets", result.stdout)

    def test_scan_never_emits_source_values_or_secret_like_filenames(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_unity_project(root)
            self.write(
                root,
                "Assets/Runtime/Player.cs",
                'class Player { const string Marker = "NEVER-EMIT-THIS"; void Run() { Debug.Log(Marker); } }',
            )
            self.write(
                root,
                "Assets/Runtime/ApiCredentials.cs",
                'class ApiCredentials { const string Value = "TOP-SECRET-VALUE"; }',
            )

            result = self.run_inspector(root, "--json", "--max-samples", "20")

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["inventory"]["csharp_files"]["count"], 1)
        self.assertEqual(report["signals"]["logging"]["count"], 1)
        for sensitive in (
            "NEVER-EMIT-THIS",
            "TOP-SECRET-VALUE",
            "ApiCredentials.cs",
        ):
            self.assertNotIn(sensitive, result.stdout)

    def test_json_is_deterministic_ordered_and_sample_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_unity_project(root)
            self.write(root, "Assets/Zeta.cs", "class Zeta { void Run() { Debug.Log(1); } }")
            self.write(root, "Assets/alpha.cs", "class Alpha { void Run() { Debug.Log(2); } }")

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
                "scripting_backend_hints",
                "relevant_packages",
                "inventory",
                "signals",
                "warnings",
            ],
        )
        self.assertEqual(report["inventory"]["csharp_files"]["count"], 2)
        self.assertEqual(report["inventory"]["csharp_files"]["samples"], ["Assets/alpha.cs"])
        self.assertEqual(report["signals"]["logging"]["count"], 2)
        self.assertEqual(report["signals"]["logging"]["samples"], ["Assets/alpha.cs"])

    def test_negative_max_samples_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_unity_project(root)
            result = self.run_inspector(root, "--json", "--max-samples", "-1")

        self.assertEqual(result.returncode, 2)
        self.assertIn("--max-samples", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_human_output_labels_paths_as_leads_not_diagnoses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_unity_project(root)
            self.write(root, "Assets/Runtime/Logger.cs", "class Logger { void Run() { Debug.Log(1); } }")

            result = self.run_inspector(root)

        self.assertEqual(result.returncode, 0, result.stderr)
        for expected in (
            "Unity GC allocation lead inspection",
            "Unity version: 6000.0.15f1",
            "Relevant packages: 0",
            "C# files: 1",
            "Signals are investigation leads, not diagnoses.",
            "logging: 1",
            "Assets/Runtime/Logger.cs",
        ):
            self.assertIn(expected, result.stdout)
        for forbidden in ("Diagnosis:", "must replace", "confirmed allocation"):
            self.assertNotIn(forbidden, result.stdout)

    def test_inspection_does_not_mutate_the_project_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.create_unity_project(root)
            self.write(root, "Assets/Runtime/Actor.cs", "class Actor { void Run() { Destroy(this); } }")
            before = self.snapshot_tree(root)

            result = self.run_inspector(root, "--json")

            after = self.snapshot_tree(root)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
