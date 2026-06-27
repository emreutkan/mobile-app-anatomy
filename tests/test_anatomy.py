from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
ANATOMY = ROOT / "skills" / "mobile-app-anatomy" / "scripts" / "anatomy.py"
RENDER = ROOT / "skills" / "mobile-app-anatomy" / "scripts" / "render_readme.py"


class AnatomySmokeTest(unittest.TestCase):
    def run_cli(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ANATOMY), *args],
            cwd=cwd,
            check=True,
            text=True,
            capture_output=True,
        )

    def make_repo(self, root: Path) -> None:
        (root / "app").mkdir(parents=True)
        (root / "src" / "state").mkdir(parents=True)
        (root / "node_modules" / "ignored").mkdir(parents=True)
        (root / ".agents" / "skills" / "foreign-skill").mkdir(parents=True)
        (root / ".cursor" / "skills" / "foreign-skill").mkdir(parents=True)
        (root / "tools" / "non_product").mkdir(parents=True)
        (root / "android" / "app" / "build" / "generated" / "source").mkdir(parents=True)
        (root / "package.json").write_text(json.dumps({
            "dependencies": {
                "expo": "latest",
                "expo-router": "latest",
                "react-native": "latest",
            }
        }))
        (root / "app" / "_layout.tsx").write_text(
            "import { Stack } from 'expo-router';\n"
            "export default function Layout(){ return <Stack.Screen name=\"login\"/>; }\n"
        )
        (root / "app" / "login.tsx").write_text(
            "import { router } from 'expo-router';\n"
            "export default function LoginScreen(){ const signInWithApple = () => router.replace('/home'); return null; }\n"
        )
        (root / "src" / "state" / "session.ts").write_text(
            "export function restoreSession(){ return null; }\n"
        )
        (root / "node_modules" / "ignored" / "index.js").write_text("ignored")
        (root / ".agents" / "skills" / "foreign-skill" / "SKILL.md").write_text("# not product")
        (root / ".cursor" / "skills" / "foreign-skill" / "SKILL.md").write_text("# not product")
        (root / "tools" / "non_product" / "fixture.ts").write_text("export const fixture = true;\n")
        (root / "android" / "app" / "build" / "generated" / "source" / "Generated.kt").write_text(
            "class GeneratedThing {}\n"
        )

    def test_inventory_routes_entities_batches_and_forced_include(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            self.make_repo(repo)
            out = repo / "docs" / "mobile-app-anatomy"

            self.run_cli(
                "init", "--repo", str(repo), "--out", str(out),
                "--chunk-lines", "25",
                "--include-dir", "android/app/build/generated",
                "--exclude-dir", "tools/non_product",
            )

            ledger = json.loads((out / "machine" / "ledger.json").read_text())
            self.assertIn("app/login.tsx", ledger["files"])
            self.assertIn("android/app/build/generated/source/Generated.kt", ledger["files"])
            self.assertFalse(any(path.startswith("node_modules/") for path in ledger["files"]))
            self.assertFalse(any(path.startswith(".agents/") for path in ledger["files"]))
            self.assertFalse(any(path.startswith(".cursor/") for path in ledger["files"]))
            self.assertFalse(any(path.startswith("tools/non_product/") for path in ledger["files"]))
            self.assertIn("tools/non_product", ledger["exclude_dirs"])

            routes = json.loads((out / "machine" / "routes_seed.json").read_text())["routes"]
            self.assertTrue(any(route["target"] == "/login" for route in routes))
            self.assertTrue(any(route["target"] == "/home" for route in routes))

            entities = json.loads((out / "machine" / "entities.json").read_text())["entities"]
            self.assertTrue(any(e["kind"] == "screen_candidate" and e["title"] == "/login" for e in entities.values()))
            self.assertTrue(any(e["kind"] == "symbol_candidate" for e in entities.values()))
            self.assertIn("feature_candidate.authentication", entities)

            claimed = json.loads(self.run_cli(
                "claim-next", "--out", str(out), "--type", "line_shard",
                "--count", "100", "--agent", "test",
            ).stdout)
            manifest = []
            for unit in claimed:
                report = f"evidence/chunks/{unit['id']}.md"
                (out / report).write_text(f"# {unit['id']}\n")
                manifest.append({
                    "unit": unit["id"],
                    "report": report,
                    "evidence": [f"{unit['path']}:{unit['start_line']}-{unit['end_line']}"],
                })
            manifest_path = Path(tmp) / "batch.json"
            manifest_path.write_text(json.dumps(manifest))
            result = json.loads(self.run_cli(
                "complete-batch", "--out", str(out), "--manifest", str(manifest_path),
            ).stdout)
            self.assertEqual(result["count"], len(claimed))

    def test_refresh_preserves_custom_exclusions_and_unknown_unit_is_actionable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            self.make_repo(repo)
            out = repo / "docs" / "mobile-app-anatomy"

            self.run_cli(
                "init", "--repo", str(repo), "--out", str(out),
                "--exclude-dir", "tools/non_product",
            )
            self.run_cli("refresh", "--repo", str(repo), "--out", str(out))
            ledger = json.loads((out / "machine" / "ledger.json").read_text())
            self.assertIn("tools/non_product", ledger["exclude_dirs"])
            self.assertFalse(any(path.startswith("tools/non_product/") for path in ledger["files"]))

            failed = subprocess.run(
                [sys.executable, str(ANATOMY), "claim", "--out", str(out), "--unit", "u_stale"],
                text=True, capture_output=True, check=False,
            )
            self.assertEqual(failed.returncode, 2)
            self.assertIn("may be stale", failed.stderr)
            self.assertIn("claim-next", failed.stderr)

    def test_renderer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "atlas"
            (out / "00-product").mkdir(parents=True)
            (out / "00-product" / "overview.md").write_text("# Product\n\nDetails.\n")
            subprocess.run(
                [sys.executable, str(RENDER), "--out", str(out), "--title", "Test Atlas"],
                check=True,
                text=True,
                capture_output=True,
            )
            text = (out / "GOD_README.md").read_text()
            self.assertIn("# Test Atlas", text)
            self.assertIn("Product", text)


if __name__ == "__main__":
    unittest.main()
