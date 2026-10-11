"""Real artifact execution and persisted acceptance boundaries."""
import base64
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
try:
    from service import Product
except ImportError:
    Product = None


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(Product, "The persisted product service must exist.")
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.product = Product(Path(self.temp.name))

    def build(self, features=None):
        created = self.product.action("create", {"brand": "Northline", "brief": "Build a considered stationery and objects storefront with a useful shopping bag.", "features": features or ["item_details", "category_filter", "cart_total", "search"]})
        identifier = created["active_run_id"]
        for action in ("plan", "design", "build"):
            created = self.product.action(action, {"run_id": identifier})
        return identifier, created["run"]

    def test_build_writes_independent_files_and_state_survives_restart(self):
        identifier, run = self.build()
        folder = Path(run["workspace_path"])
        self.assertTrue((folder / "index.html").is_file())
        self.assertTrue((folder / "catalog.mjs").is_file())
        self.assertIn("Northline", (folder / "index.html").read_text())
        reopened = Product(Path(self.temp.name)).state()
        self.assertEqual(reopened["active_run_id"], identifier)
        self.assertEqual(reopened["run"]["stage"], "built")

    def test_real_fault_blocks_acceptance_and_repair_records_diff(self):
        identifier, run = self.build()
        self.product.action("inject", {"run_id": identifier, "fault": "wrong_total"})
        result = self.product.action("qa", {"run_id": identifier})["run"]
        self.assertFalse(result["qa"]["passed"])
        self.assertNotEqual(result["qa"]["exit_code"], 0)
        self.assertIn("84", result["qa"]["stdout"])
        with self.assertRaises(RuntimeError):
            self.product.action("accept", {"run_id": identifier})
        repaired = self.product.action("repair", {"run_id": identifier})["run"]
        self.assertIn("totalMultiplier", repaired["diff"])
        checked = self.product.action("qa", {"run_id": identifier})["run"]
        self.assertTrue(checked["qa"]["passed"], checked["qa"]["stdout"])
        accepted = self.product.action("accept", {"run_id": identifier, "note": "Reviewed the live artifact and executable QA."})["run"]
        self.assertEqual(accepted["stage"], "accepted")
        archive = self.product.action("export", {"run_id": identifier})
        with zipfile.ZipFile(io.BytesIO(base64.b64decode(archive["base64"]))) as bundle:
            self.assertIn("Northline/catalog.mjs", bundle.namelist())
            self.assertIn("Northline/acceptance.json", bundle.namelist())

    def test_changed_source_invalidates_prior_qa_and_cannot_be_exported(self):
        identifier, _ = self.build()
        self.product.action("qa", {"run_id": identifier})
        self.product.action("accept", {"run_id": identifier})
        self.product.action("inject", {"run_id": identifier, "fault": "leak_cost"})
        with self.assertRaises(RuntimeError):
            self.product.action("export", {"run_id": identifier})
        reviewed = self.product.action("qa", {"run_id": identifier})["run"]
        self.assertFalse(reviewed["qa"]["passed"])
        self.assertTrue(any(check["id"] == "public-fields" and not check["passed"] for check in reviewed["qa"]["checks"]))

    def test_workspace_tampering_after_acceptance_is_detected(self):
        identifier, run = self.build()
        self.product.action("qa", {"run_id": identifier})
        self.product.action("accept", {"run_id": identifier})
        source = Path(run["workspace_path"]) / "catalog.mjs"
        source.write_text(source.read_text() + "\n// edited outside the workspace UI", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "changed"):
            self.product.action("export", {"run_id": identifier})

    def test_payload_validation_prevents_arbitrary_command_and_path_actions(self):
        with self.assertRaises(ValueError):
            self.product.action("create", {"brand": "Test", "brief": "Valid sample brief for a storefront", "features": ["arbitrary-code"]})
        with self.assertRaises(ValueError):
            self.product.action("execute", {"command": "echo unsafe"})
        with self.assertRaises(ValueError):
            self.product.action("plan", {"run_id": "../../"})

    def test_optional_features_change_the_generated_artifact(self):
        identifier, run = self.build(["category_filter"])
        self.assertNotIn('id="cart-panel"', run["preview_html"])
        self.assertNotIn('id="search-input"', run["preview_html"])
        checked = self.product.action("qa", {"run_id": identifier})["run"]
        self.assertTrue(checked["qa"]["passed"])
        self.assertNotIn("cart-total", [check["id"] for check in checked["qa"]["checks"]])

    def test_exported_artifact_executes_without_the_product_workspace(self):
        identifier, _ = self.build()
        self.product.action("qa", {"run_id": identifier})
        self.product.action("accept", {"run_id": identifier})
        archive = self.product.action("export", {"run_id": identifier})
        destination = Path(self.temp.name) / "copied-release"
        with zipfile.ZipFile(io.BytesIO(base64.b64decode(archive["base64"]))) as bundle:
            bundle.extractall(destination)
        result = subprocess.run([shutil.which("node"), "qa.mjs"], cwd=destination / "Northline", capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("11/11 checks passed", result.stdout)
        self.assertTrue((destination / "Northline/fonts/dm-sans.ttf").is_file())

    def test_edited_brand_is_in_the_browser_contract_and_preview_font_is_self_contained(self):
        state = self.product.action("create", {"brand": "Studio Goods", "brief": "Build an everyday collection with searchable items and a shopping bag.", "features": ["search", "cart_total"]})
        identifier = state["active_run_id"]
        for action in ("plan", "design", "build"):
            state = self.product.action(action, {"run_id": identifier})
        files = {file["name"]: file["content"] for file in state["run"]["files"]}
        self.assertEqual(json.loads(files["catalog.json"]).get("brand"), "Studio Goods")
        self.assertIn("safe(brand.toUpperCase())", files["app.mjs"])
        self.assertIn("data:font/ttf;base64,", state["run"]["preview_html"])

    def test_cli_completes_under_windows_legacy_console_encoding(self):
        result = subprocess.run([sys.executable, str(ROOT / "cli.py"), "--data-dir", str(Path(self.temp.name) / "cli-state"), "--out", str(Path(self.temp.name) / "release"), "--exercise-repair"], capture_output=True, env={**os.environ, "PYTHONIOENCODING": "cp1252"})
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        self.assertIn(b"accepted:", result.stdout)
        self.assertEqual(len(list((Path(self.temp.name) / "release").glob("*.zip"))), 1)


if __name__ == "__main__":
    unittest.main()
