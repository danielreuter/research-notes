"""Write a research/result/v0.1 result.json for a red-team CPU attack run (no import of `research`)."""
import json, os


def write(name, measurements, details, *, status="passed", checker="red-team-pouw", detail=""):
    run_dir = os.environ.get("RESEARCH_RUN_DIR")
    run_id = os.environ.get("RESEARCH_RUN_ID")
    if not run_dir or not run_id:
        return None
    with open(os.path.join(run_dir, "details.json"), "w") as f:
        json.dump(details, f, indent=2)
    doc = {
        "schema": "research/result/v0.1",
        "run_id": run_id,
        "workload_fingerprint": {"attack": name, "by": "red-team-pouw"},
        "validation": {"status": status, "checker": checker, "detail": detail, "evidence": ["details.json"]},
        "measurements": [{"name": k, "value": v, "unit": u} for k, v, u in measurements],
        "measurement_files": ["details.json"],
        "artifacts": ["details.json"],
    }
    tmp = os.path.join(run_dir, "result.json.tmp")
    with open(tmp, "w") as f:
        json.dump(doc, f, indent=2)
    os.replace(tmp, os.path.join(run_dir, "result.json"))
    return os.path.join(run_dir, "result.json")
