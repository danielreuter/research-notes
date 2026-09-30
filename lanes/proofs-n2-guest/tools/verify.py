"""proofs-n2-guest: check one job's output and record it as done/<id>.json (atomically), else exit 1 with verify-failed.json.

    verify.py stage|chunk RUN_DIR DONE_JSON RC T0 T1 SHAPE IDX START COUNT GATE BIN_SHA

A stage job is done when staged.jsonl holds the shape with its statement staged. A chunk is done when its summary (73-sweep-shape.sh
SUMMARY) says rc 0, one shape proved, COUNT statements timed and COUNT accepted by the loopback verifier, on the pinned prover binary;
a gate chunk also needs every selftest to pass, the GPU cases (gpu_paths_agree, gpu_proofs_match_cpu) among them.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROW = "llama32-1b__bf16__rtxpro6000__tp1__b1__i1024__o128__mixed__greedy__bi-eager"
GPU_CASES = {"gpu_paths_agree", "gpu_proofs_match_cpu"}
LABEL = ("measurement on #554's draft prover key (4d568a3cb558b005); the 4x4 tile statement isn't reviewed yet; not a verified "
         "table row")
ENV_CHECK = ("matches node 1: driver 580.173.02, the same flock-circuit resolving libcudart 13.0.96, SM clocks locked node-wide at "
             "2,100 MHz (note:20260930T2205Z-report-env-check-and-classes)")


def iso(t: int) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def gpu() -> dict:
    vis = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    out = {"cuda_visible_devices": vis, "gpu_lease_uuid": os.environ.get("GPU_LEASE_UUID", ""), "fill_job": os.environ.get("FILL_JOB", "")}
    host = Path(os.environ.get("RESEARCH_RUN_DIR", "."), "out", "host.txt")
    if host.exists():
        for ln in host.read_text().splitlines():
            f = [x.strip() for x in ln.split(",")]
            if len(f) >= 2 and f[0] == vis:
                out["gpu_name"], out["driver"] = f[1], f[2] if len(f) > 2 else None
    return out


def main() -> int:
    kind, run, done, rc, t0, t1, shape, idx, start, count, gate, bin_sha = sys.argv[1:13]
    run, done, rc, t0, t1 = Path(run), Path(done), int(rc), int(t0), int(t1)
    rec = {"id": done.stem, "kind": kind, "row": ROW, "shape": shape, "shape_index": int(idx), "node": "vy-nebius-2",
           "lane": "proofs-n2-guest", "owner": "bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4", "run_dir": str(run), "rc": rc,
           "t_start": iso(t0), "t_end": iso(t1), "job_s": t1 - t0, "label": LABEL,
           "question": os.environ.get("PN2G_QUESTION", ""), "env_check": ENV_CHECK}
    why: list[str] = []
    if kind == "stage":
        p = run / "out" / "1" / "classes" / "staged.jsonl"
        recs = [json.loads(ln) for ln in p.read_text().splitlines() if ln.strip()] if p.exists() else []
        r = next((x for x in recs if x.get("shape") == shape), None)
        if rc != 0:
            why.append(f"job rc {rc}")
        if not r or "stage" not in r:
            why.append(f"not staged: {(r or {}).get('broke') or 'no record'}")
        else:
            st = r["stage"]
            rec["stage"] = {k: st.get(k) for k in ("n", "coords_per_instance", "k_log", "ands", "vus_per_block", "circuit_sha512")}
            rec.update(stage_s=r.get("stage_s"), row_units=r.get("row_units"), definition=r.get("definition"))
    else:
        start, count, is_gate = int(start), int(count), gate == "1"
        sp = run / "summary.json"
        s = json.loads(sp.read_text()) if sp.exists() else {}
        res = run / "out" / "1" / "classes" / "results.jsonl"
        recs = [json.loads(ln) for ln in res.read_text().splitlines() if ln.strip()] if res.exists() else []
        r = next((x for x in recs if x.get("shape") == shape), {})
        checks = {"job rc 0": rc == 0, "summary rc 0": s.get("rc") == 0, "mode shape": s.get("mode") == "shape",
                  "one shape proved": s.get("shapes") == 1 and s.get("proved") == 1 and not s.get("not_proved"),
                  f"{count} statements timed": s.get("statements") == count,
                  f"{count} statements accepted": s.get("accepted_statements") == count,
                  "pinned prover binary": bin_sha in (s.get("binary_sha256") or [])}
        if is_gate:
            checks.update({"selftest ran": (s.get("selftests") or 0) >= 1,
                           "every selftest passed": s.get("selftests_pass") == s.get("selftests"),
                           "GPU cases ran": GPU_CASES <= set(s.get("gpu_case_names") or []),
                           "every GPU case passed": (s.get("gpu_cases") or 0) >= 2 and s.get("gpu_cases_pass") == s.get("gpu_cases")})
        why = [k for k, ok in checks.items() if not ok]
        st, live = r.get("stage") or {}, r.get("live") or {}
        n = s.get("statements") or 0
        rec.update(start=start, count=count, end=start + count, gate=is_gate, summary=s, gpu=gpu(),
                   stage={k: st.get(k) for k in ("n", "coords_per_instance", "k_log", "ands")}, row_units=r.get("row_units"),
                   stage_cached=r.get("stage_cached"), stage_s=r.get("stage_s"),
                   live={k: live.get(k) for k in ("k_log", "prover", "instances", "proof_bytes", "prover_peak_gb", "verifier_peak_gb",
                                                   "statement_digest", "pipeline_depth")},
                   selftest=r.get("selftest"),
                   e2e_s_per_statement=round(s["e2e_s"] / n, 6) if n else None,
                   prove_s_per_statement=round(s["prove_total_s"] / n, 6) if n else None,
                   binary_sha256=(run / "out" / "1" / "binary.sha256").read_text() if (run / "out" / "1" / "binary.sha256").exists() else None)
    if why:
        rec["why"] = why
        (run / "verify-failed.json").write_text(json.dumps(rec, indent=1, default=str))
        print("VERIFY FAILED", done.stem, why, flush=True)
        return 1
    tmp = done.with_name(f".{done.name}.tmp")
    tmp.write_text(json.dumps(rec, indent=1, default=str))
    os.replace(tmp, done)
    print("VERIFIED", done.stem, json.dumps({k: rec.get(k) for k in ("job_s", "start", "count", "e2e_s_per_statement", "stage")}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
