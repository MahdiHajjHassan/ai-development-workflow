"""Persisted local delivery workflow with executable artifacts and acceptance hashes."""
import base64
from contextlib import closing, contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import difflib
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import uuid
import zipfile

from artifacts import APP_SOURCE, FEATURES, ROOT, generate, module_source, preview


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def require_text(value, name, minimum=1, maximum=2000):
    if not isinstance(value, str) or not minimum <= len(value.strip()) <= maximum:
        raise ValueError(f"{name} needs {minimum} to {maximum} characters.")
    return value.strip()


@contextmanager
def connection(path):
    with closing(sqlite3.connect(path)) as db:
        db.row_factory = sqlite3.Row
        with db:
            yield db


class Product:
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir).resolve()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "agentcrew.sqlite3"
        self.workspace = self.data_dir / "workspace"
        self.workspace.mkdir(exist_ok=True)
        with connection(self.db_path) as db:
            db.executescript("CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, body TEXT NOT NULL, updated_at TEXT NOT NULL); CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);")
        # A real initial artifact makes the primary result visible immediately.
        if not self._runs():
            fixture = json.loads((ROOT / "fixtures/brief.json").read_text(encoding="utf-8"))
            run = self._create(fixture)
            for action in ("plan", "design", "build"):
                self.action(action, {"run_id": run["id"]})

    def _runs(self):
        with connection(self.db_path) as db:
            return [json.loads(row["body"]) for row in db.execute("SELECT body FROM runs ORDER BY updated_at DESC, rowid DESC")]

    def _get(self, identifier=None):
        if identifier is None:
            with connection(self.db_path) as db:
                row = db.execute("SELECT value FROM settings WHERE key='active'").fetchone()
                identifier = row[0] if row else None
        if not isinstance(identifier, str) or not re.fullmatch(r"ac-[a-f0-9]{10}", identifier):
            raise ValueError("Choose an existing workflow run.")
        with connection(self.db_path) as db:
            row = db.execute("SELECT body FROM runs WHERE id=?", (identifier,)).fetchone()
        if not row:
            raise ValueError("This workflow run does not exist.")
        return json.loads(row[0])

    def _write(self, run, select=True):
        run["updated_at"] = now()
        with connection(self.db_path) as db:
            db.execute("INSERT INTO runs VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET body=excluded.body,updated_at=excluded.updated_at", (run["id"], json.dumps(run), run["updated_at"]))
            if select:
                db.execute("INSERT INTO settings VALUES('active',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (run["id"],))

    def _trace(self, run, action, title, detail, worker):
        run["trace"].append({"action": action, "title": title, "detail": detail, "worker": worker, "at": now(), "revision": run["revision"]})

    def _create(self, payload):
        brand = require_text(payload.get("brand", "Northline"), "Store name", 2, 50)
        brief = require_text(payload.get("brief"), "Product brief", 20, 4000)
        features = payload.get("features", list(FEATURES))
        if not isinstance(features, list) or not features or any(not isinstance(f, str) or f not in FEATURES for f in features):
            raise ValueError("Select one or more supported storefront features.")
        run = {"id": "ac-" + uuid.uuid4().hex[:10], "brand": brand, "brief": brief, "features": list(dict.fromkeys(features)), "stage": "brief", "revision": 1, "created_at": now(), "updated_at": now(), "tasks": [], "criteria": [], "design": [], "trace": [], "qa": None, "decision": None, "fault": "none", "diff": "", "snapshots": [], "workspace_path": ""}
        self._trace(run, "create", "Brief created", "Owner defined a product brief and feature scope.", "Product owner")
        self._write(run)
        return run

    def _folder(self, run):
        folder = self.workspace / run["id"] / f"r{run['revision']:02}"
        if not folder.resolve().is_relative_to(self.workspace):
            raise ValueError("Invalid workspace path.")
        return folder

    def _files(self, run):
        if not run["workspace_path"]:
            return {}
        folder = self._folder(run)
        return {p.name: p.read_text(encoding="utf-8") for p in sorted(folder.iterdir()) if p.is_file() and p.suffix in {".html", ".css", ".mjs", ".json", ".md"}}

    def _hash(self, run):
        digest = hashlib.sha256()
        folder = self._folder(run)
        for file in sorted(folder.rglob("*")):
            if file.is_file() and file.name != "acceptance.json":
                digest.update(file.relative_to(folder).as_posix().encode())
                digest.update(file.read_bytes())
        return digest.hexdigest()

    def state(self):
        runs = self._runs()
        run = self._get() if runs else None
        if run:
            files = self._files(run)
            run["files"] = [{"name": name, "content": content, "bytes": len(content.encode())} for name, content in files.items()]
            run["preview_html"] = preview(files) if "index.html" in files else ""
            run["source_hash"] = self._hash(run) if files else None
        return {"active_run_id": run["id"] if run else None, "run": run, "runs": [{k: r[k] for k in ("id", "brand", "stage", "revision", "updated_at")} for r in runs], "features": [{"id": key, **value} for key, value in FEATURES.items()], "workers": [{"name": "Planner", "kind": "Deterministic local worker"}, {"name": "Architect", "kind": "Deterministic local worker"}, {"name": "Builder", "kind": "Fixed source templates"}, {"name": "Reviewer", "kind": "Executable Node.js checks"}], "provider": {"mode": "offline", "configured": False, "label": "Offline deterministic workers"}}

    def _require(self, run, stages, message):
        if run["stage"] not in stages:
            raise RuntimeError(message)

    def _build(self, run, fault="none", note="Generated storefront source."):
        old = self._files(run)
        if old:
            run["snapshots"].append({"revision": run["revision"], "stage": run["stage"], "qa": deepcopy(run["qa"]), "hash": self._hash(run), "fault": run["fault"]})
            run["revision"] += 1
        files = generate(run, fault)
        folder = self._folder(run)
        folder.mkdir(parents=True, exist_ok=True)
        for name, content in files.items():
            (folder / name).write_text(content, encoding="utf-8")
        fonts = folder / "fonts"
        fonts.mkdir(exist_ok=True)
        for name in ("dm-sans.ttf", "DM-Sans-OFL.txt"):
            shutil.copyfile(ROOT / "public/fonts" / name, fonts / name)
        run["workspace_path"] = str(folder)
        run["fault"] = fault
        run["qa"] = None
        run["decision"] = None
        run["stage"] = "built"
        run["diff"] = "\n".join(''.join(difflib.unified_diff(old.get(name, '').splitlines(True), content.splitlines(True), fromfile=f"r{run['revision']-1:02}/{name}", tofile=f"r{run['revision']:02}/{name}")) for name, content in files.items() if old.get(name, '') != content) if old else ""
        for task in run["tasks"]:
            task["status"] = "built"
        self._trace(run, "build" if not old else "revision", "Source written", note + f" {len(files)} source files written to r{run['revision']:02}.", "Builder")

    def _qa(self, run):
        node = shutil.which("node")
        if not node:
            raise RuntimeError("Node.js is required for executable QA. Install Node, then run checks again.")
        files = self._files(run)
        # API actions only emit these fixed executable templates. Refuse external code edits.
        if files.get("catalog.mjs") not in {module_source(), module_source("wrong_total")} or files.get("app.mjs") != APP_SOURCE:
            raise RuntimeError("Executable source changed outside the builder. Rebuild before running fixed QA.")
        completed = subprocess.run([node, str(ROOT / "qa_runner.mjs"), str(self._folder(run))], capture_output=True, text=True, encoding="utf-8", timeout=20, shell=False)
        report_lines = [line for line in completed.stdout.splitlines() if line.startswith("AGENTCREW_REPORT=")]
        report = json.loads(report_lines[-1].split("=", 1)[1]) if report_lines else {"passed": False, "checks": []}
        syntax = subprocess.run([node, "--check", str(self._folder(run) / "app.mjs")], capture_output=True, text=True, encoding="utf-8", timeout=20, shell=False)
        report["checks"].append({"id": "syntax", "title": "Browser module passes Node syntax check", "passed": syntax.returncode == 0, "observed": syntax.stderr or "node --check app.mjs → exit 0"})
        report["passed"] = bool(report["passed"] and completed.returncode == 0 and syntax.returncode == 0)
        report.update({"executed_at": now(), "command": "node qa.mjs && node --check app.mjs", "exit_code": completed.returncode or syntax.returncode, "stdout": completed.stdout.split("AGENTCREW_REPORT=")[0].strip() + "\n" + ("PASS  Browser module syntax" if syntax.returncode == 0 else syntax.stderr), "stderr": completed.stderr, "source_hash": self._hash(run), "runner": "Node.js subprocess / fixed local QA runner"})
        run["qa"] = report
        run["stage"] = "reviewed"
        run["decision"] = None
        for task in run["tasks"]:
            task["status"] = "verified" if report["passed"] else "needs repair"
        passed = sum(c["passed"] for c in report["checks"])
        self._trace(run, "qa", "Checks completed", f"{passed}/{len(report['checks'])} checks passed. Exit code {report['exit_code']}.", "Reviewer")

    def action(self, name, payload):
        if name == "create":
            self._create(payload)
            return self.state()
        allowed = {"select", "plan", "design", "build", "qa", "inject", "repair", "accept", "export", "revise"}
        if name not in allowed:
            raise ValueError("Unknown workflow action.")
        run = self._get(payload.get("run_id"))
        if name == "select":
            self._write(run)
            return self.state()
        if name == "plan":
            self._require(run, {"brief"}, "Start a new brief before planning.")
            run["criteria"] = ["The public catalog contains four priced objects.", "Invalid and unknown IDs return useful responses.", "Internal purchasing costs stay out of public source."] + [FEATURES[f]["description"] for f in run["features"]]
            run["tasks"] = [{"id": f"AC-{i+1:02}", "title": FEATURES[f]["title"], "feature": f, "owner": "Builder", "status": "planned"} for i, f in enumerate(run["features"])]
            run["stage"] = "planned"
            self._trace(run, name, "Delivery plan prepared", f"{len(run['tasks'])} tasks and {len(run['criteria'])} acceptance criteria derived from selected scope.", "Planner")
        elif name == "design":
            self._require(run, {"planned"}, "Prepare the delivery plan before design.")
            run["design"] = ["Independent HTML storefront with CSS, data and ES modules.", "Public catalog schema: id, name, category, price, description, material, color, label, edition.", "A shared module implements lookup, filtering, search and exact cent arithmetic.", "Node.js exercises the same module used by the browser.", "Acceptance binds the observed QA result to a SHA-256 source hash."]
            run["stage"] = "designed"
            self._trace(run, name, "Technical design settled", "Defined the public contract, module boundaries, theme controls and executable checks.", "Architect")
        elif name == "build":
            self._require(run, {"designed"}, "Complete technical design before building.")
            self._build(run)
        elif name == "revise":
            self._require(run, {"built", "reviewed", "accepted"}, "Build an artifact before revising it.")
            run["brief"] = require_text(payload.get("brief", run["brief"]), "Product brief", 20, 4000)
            run["brand"] = require_text(payload.get("brand", run["brand"]), "Store name", 2, 50)
            self._build(run, note="Owner requested a content revision.")
        elif name == "inject":
            self._require(run, {"built", "reviewed", "accepted"}, "Build source before introducing a defect.")
            fault = payload.get("fault", "wrong_total")
            if fault not in {"wrong_total", "leak_cost"}:
                raise ValueError("Choose a supported defect.")
            if fault == "wrong_total" and "cart_total" not in run["features"]:
                raise ValueError("The total defect needs the shopping bag feature.")
            self._build(run, fault, "Introduced a deliberate " + ("10% arithmetic defect." if fault == "wrong_total" else "public supplier-cost leak."))
        elif name == "repair":
            self._require(run, {"built", "reviewed", "accepted"}, "Build source before requesting repair.")
            if run["fault"] == "none":
                raise RuntimeError("There is no injected defect to repair.")
            self._build(run, note="Repaired the generated module/data and invalidated prior QA.")
        elif name == "qa":
            self._require(run, {"built", "reviewed", "accepted"}, "Build the storefront before running checks.")
            self._qa(run)
        elif name == "accept":
            self._require(run, {"reviewed"}, "Run executable checks before acceptance.")
            if not run["qa"] or not run["qa"]["passed"]:
                raise RuntimeError("Failed checks block acceptance. Repair the source and run checks again.")
            if run["qa"]["source_hash"] != self._hash(run):
                raise RuntimeError("Source changed since QA. Run checks again.")
            note = require_text(payload.get("note", "Reviewed the storefront preview and executable QA results."), "Acceptance note", 5, 1000)
            run["decision"] = {"at": now(), "note": note, "source_hash": self._hash(run), "decision": "accepted locally"}
            run["stage"] = "accepted"
            self._trace(run, name, "Artifact accepted", note, "Product owner")
        elif name == "export":
            self._require(run, {"accepted"}, "Accept the reviewed artifact before downloading the release source.")
            if not run["decision"] or run["decision"]["source_hash"] != self._hash(run):
                raise RuntimeError("Source changed after acceptance. Run checks and accept the current source again.")
            output = io.BytesIO()
            slug = re.sub(r"[^A-Za-z0-9_-]", "-", run["brand"]).strip("-") or "storefront"
            with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
                for file in sorted(self._folder(run).rglob("*")):
                    if file.is_file():
                        archive.writestr(slug + "/" + file.relative_to(self._folder(run)).as_posix(), file.read_bytes())
                archive.writestr(slug + "/acceptance.json", json.dumps({"run_id": run["id"], "revision": run["revision"], "decision": run["decision"], "qa": run["qa"]}, indent=2))
            return {"filename": f"{slug}-r{run['revision']:02}.zip", "mime": "application/zip", "base64": base64.b64encode(output.getvalue()).decode(), "source_hash": run["decision"]["source_hash"]}
        self._write(run)
        return self.state()
