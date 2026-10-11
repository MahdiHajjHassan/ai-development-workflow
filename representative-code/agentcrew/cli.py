"""Run the storefront delivery journey without the browser."""
import argparse
import base64
import json
import sys
from pathlib import Path
from service import Product, ROOT


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Build, check and export an AgentCrew storefront")
    parser.add_argument("--data-dir", type=Path, default=ROOT / ".product-data")
    parser.add_argument("--brief", type=Path, default=ROOT / "fixtures/brief.json")
    parser.add_argument("--out", type=Path, default=ROOT / ".product-data/releases")
    parser.add_argument("--exercise-repair", action="store_true", help="Inject a real total defect, observe QA fail, then repair it")
    args = parser.parse_args()
    product = Product(args.data_dir)
    state = product.action("create", json.loads(args.brief.read_text(encoding="utf-8")))
    run_id = state["active_run_id"]
    for action in ("plan", "design", "build"):
        state = product.action(action, {"run_id": run_id})
        print(f"{action}: {state['run']['stage']}")
    if args.exercise_repair:
        product.action("inject", {"run_id": run_id, "fault": "wrong_total"})
        state = product.action("qa", {"run_id": run_id})
        print(state["run"]["qa"]["stdout"])
        if state["run"]["qa"]["passed"]:
            raise RuntimeError("The deliberately broken source unexpectedly passed QA.")
        product.action("repair", {"run_id": run_id})
    state = product.action("qa", {"run_id": run_id})
    print(state["run"]["qa"]["stdout"])
    if not state["run"]["qa"]["passed"]:
        raise SystemExit(1)
    state = product.action("accept", {"run_id": run_id, "note": "CLI operator accepted the generated artifact after executable QA."})
    output = product.action("export", {"run_id": run_id})
    args.out.mkdir(parents=True, exist_ok=True)
    archive = args.out / output["filename"]
    archive.write_bytes(base64.b64decode(output["base64"]))
    manifest = args.out / f"{run_id}-report.json"
    manifest.write_text(json.dumps({"run_id": run_id, "workspace": state["run"]["workspace_path"], "qa": state["run"]["qa"], "decision": state["run"]["decision"], "release": str(archive)}, indent=2), encoding="utf-8")
    print(f"accepted: {run_id} / revision {state['run']['revision']}\nworkspace: {state['run']['workspace_path']}\nrelease: {archive}\nreport: {manifest}")


if __name__ == "__main__":
    main()
