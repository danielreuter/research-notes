#!/usr/bin/env python3
"""rec-ksweep: the recursion overhead curve from 85-rec-reprice.sh's per-step summaries (rec-step2 b6139d9b6).

    python3 curve.py --runs ~/.research/runs --out curve.json --table curve.md \
        --point K=4096,N=2048,build=R,inner=R,vstage=R,oprove=R[+R..],lean=R[+R..] ...

Each run id names a fetched run dir whose out/summary-<step>.json the step wrote. A step split across runs joins them with
'+' (later runs' statements win). The overhead is (inner M0 against the rec proxy + V*'s total --zk prove) / today's --zk
prove, each term also reported alone; V* is every honest staged statement (L*, alg-p*), forgeries reported apart.
"""
import argparse
import json
import re
import statistics
from pathlib import Path


def load(runs: Path, ids: str, step: str) -> tuple[dict, list[str]]:
    merged: dict = {}
    names = [r for r in ids.split("+") if r]
    for r in names:
        s = json.loads((runs / r / "out" / f"summary-{step}.json").read_text())
        for k, v in s.items():
            if k == "levels" and isinstance(v, dict):
                merged.setdefault("levels", {}).update(v)
            else:
                merged[k] = v
    return merged, names


def held_s(lease: list[str] | None) -> float:
    t = 0.0
    for line in lease or []:
        m = re.search(r"held (\d+)m(\d+)s", line)
        if m:
            t += int(m.group(1)) * 60 + int(m.group(2))
    return t


def sizes(text: str) -> dict:
    out = {}
    for line in (text or "").splitlines():
        b, _, p = line.partition("\t")
        if b.strip().isdigit():
            out[p.strip()] = int(b)
    return out


def waits(runs: Path, names: list[str], rel: str) -> dict:
    """Medians over the timed sessions of a prove's LIVE records (out/<rel>/prove.tsv; the first WARM are untimed): the
    prover's wait for the verifier's coins on its critical path (wait_e2e_s) and prove_total_s less it (compute_s)."""
    for r in reversed(names):
        f = runs / r / "out" / rel / "prove.tsv"
        if not f.exists():
            continue
        rows = [json.loads(l.split("\t", 2)[2]) for l in f.read_text().splitlines() if "\tLIVE\t" in l]
        w = runs / r / "out" / rel / "warm.txt"
        warm = int(w.read_text().strip()) if w.exists() else 1
        timed = [x for x in rows[warm:] if isinstance(x.get("prove_total_s"), (int, float))]
        if not timed:
            return {}
        return {"wait_e2e_s": round(statistics.median(x.get("wait_e2e_s", 0) for x in timed), 6),
                "compute_s": round(statistics.median(x["prove_total_s"] - x.get("wait_e2e_s", 0) for x in timed), 6)}
    return {}


def live_row(v: dict, extra: dict | None = None) -> dict:
    pb = v.get("proof_bytes") or []
    return {"prove_s": v.get("prove_total_s"), "session_s": v.get("session_s"), "serve_verify_s": v.get("serve_verify_s"),
            "proof_bytes": sum(pb) if isinstance(pb, list) else pb, "m": v.get("dense_m"), "k_log": v.get("k_log"),
            "host_peak_gb": v.get("prover_peak_gb"), "gpu_peak_mib": v.get("gpu_peak_mib"), "accepted": v.get("accepted"),
            "serve_accepted": v.get("serve_accepted"), "prover_cores_busy_before": v.get("prover_cores_busy_before"),
            "zkrank_s": v.get("zkrank_s"), "gpu_held_s": held_s(v.get("lease"))} | (extra or {})


def ssum(rows: list[dict], key: str):
    xs = [r.get(key) for r in rows]
    return round(sum(xs), 6) if xs and all(isinstance(x, (int, float)) for x in xs) else None


def smax(rows: list[dict], key: str):
    xs = [r.get(key) for r in rows if isinstance(r.get(key), (int, float))]
    return max(xs) if xs else None


def point(runs: Path, spec: dict) -> dict:
    K, N = int(spec["K"]), int(spec["N"])
    p: dict = {"K": K, "N": N, "runs": {}}
    if spec.get("label"):
        p["label"] = spec["label"]
    b, p["runs"]["build"] = load(runs, spec["build"], "build")
    st = (b.get("staged") or [{}])[0]
    stmt = {}
    m = re.search(r"STATEMENT\t(\{.*\})", b.get("statement") or "")
    if m:
        stmt = json.loads(m.group(1))
    p["inner_statement"] = {"definition": st.get("definition"), "ands_per_instance": st.get("ands"), "instances": stmt.get("instances"),
                            "k_log": stmt.get("k_log"), "nbl": stmt.get("nbl"), "statement_digest": (stmt.get("statement_digest") or "")[:16],
                            "binary": (b.get("binary") or "")[:16], "lean": (b.get("lean") or "")[:16], "stage_wall": b.get("stage_wall"),
                            "stage_peak_gb": b.get("stage_peak_gb")}
    i, p["runs"]["inner"] = load(runs, spec["inner"], "inner")
    inner = {n: live_row(i[n], waits(runs, p["runs"]["inner"], f"inner/{n}")) for n in ("proxy", "m0", "zk")
             if isinstance(i.get(n), dict) and "error" not in i[n]}
    p["inner"] = inner
    p["inner"]["replay_proxy"] = (i.get("replay_proxy") or {}).get("verdict")
    p["inner"]["replay_zk"] = (i.get("replay_zk") or {}).get("verdict")
    # proxy=R: the inner M0 against the rec proxy re-measured alone (INNER_LOOPBACK=0, its own data tag over the same staged
    # statement); the first run's row, whose session V*'s statements were staged over, stays as proxy_first
    if spec.get("proxy"):
        pr, p["runs"]["proxy"] = load(runs, spec["proxy"], "inner")
        inner["proxy_first"] = inner.pop("proxy", None)
        inner["proxy"] = live_row(pr["proxy"], waits(runs, p["runs"]["proxy"], "inner/proxy"))
        p["inner"]["replay_proxy_remeasure"] = (pr.get("replay_proxy") or {}).get("verdict")
    if inner.get("proxy"):
        p["inner_statement"]["m"] = inner["proxy"]["m"]
    v, p["runs"]["vstage"] = load(runs, spec["vstage"], "vstage")
    sz = sizes(v.get("sizes", ""))
    stage = {}
    for name, x in (v.get("statements") or {}).items():
        stage[name] = {"wall": x.get("wall"), "peak_gb": x.get("peak_gb")}
        s = x.get("stage")
        if isinstance(s, dict) and s.get("algebra"):
            stage[name]["parts"] = [{k: a.get(k) for k in ("part", "k_log", "instances", "nv", "nw", "holds", "of_residuals", "circuit_bytes",
                                                            "build_s", "regions", "ports", "products", "unit_rows")} for a in s["algebra"]]
        if isinstance(s, dict) and s.get("levels"):
            stage[name]["levels"] = {l: {k: y.get(k) for k in ("instances", "k_log", "H", "LANES", "compressions", "opened", "not_summed")}
                                     for l, y in s["levels"].items()}
        if isinstance(s, dict) and s.get("verifier"):
            stage[name]["verifier"] = s["verifier"]
    p["vstage"] = {"points": v.get("points"), "fold": v.get("fold"), "statements": stage}
    o, p["runs"]["oprove"] = load(runs, spec["oprove"], "oprove")
    honest, forged = {}, {}
    for name, x in sorted((o.get("levels") or {}).items()):
        row = live_row(x.get("live") or {}, waits(runs, p["runs"]["oprove"], f"oprove/{name}"))
        rep = x.get("replay")
        row["replay"] = rep.get("verdict") if isinstance(rep, dict) else rep
        d = name.replace("alg-", "alg/").replace("forged-sum-", "forged-sum/").replace("forged-comb-", "forged-comb/") \
                .replace("forged-message-", "forged-message/")
        row["circuit_bytes"] = sz.get(f"./{d}/circuit.txt")
        row["inst_bytes"] = sz.get(f"./{d}/inst.bin")
        row["pub_bytes"] = sz.get(f"./{d}/pub.bin")
        (forged if name.startswith("forged-") else honest)[name] = row
    p["vstar"] = honest
    p["forged"] = forged
    lv = [r for n, r in honest.items() if n.startswith("L")]
    al = [r for n, r in honest.items() if n.startswith("alg")]
    allr = lv + al
    p["vstar_total"] = {g: {k: ssum(rs, k) for k in ("prove_s", "compute_s", "wait_e2e_s", "session_s", "serve_verify_s", "proof_bytes",
                                                     "circuit_bytes", "gpu_held_s")}
                        | {"statements": len(rs), "host_peak_gb": smax(rs, "host_peak_gb"), "gpu_peak_mib": smax(rs, "gpu_peak_mib"),
                           "prover_cores_busy_before_max": smax(rs, "prover_cores_busy_before")}
                        for g, rs in (("levels", lv), ("algebra", al), ("vstar", allr))}
    if spec.get("lean"):
        le, p["runs"]["lean"] = load(runs, spec["lean"], "lean")
        lean = {}
        for name, x in sorted((le.get("levels") or {}).items()):
            vd = x.get("verdict")
            if isinstance(vd, dict):
                lean[name] = {k: vd.get(k) for k in ("accepted", "why", "verify_s", "setup_s", "inputs_s")} | {"wall": x.get("wall"), "peak_gb": x.get("peak_gb")}
            elif name in honest or name in forged or name in ("inner", "zk"):
                lean[name] = {"accepted": None, "why": str(vd)[-300:]}
        p["lean"] = lean
        hv = [lean[n] for n in honest if n in lean]
        p["lean_total"] = {"verify_s": ssum(hv, "verify_s"), "setup_s": ssum(hv, "setup_s"), "statements": len(hv),
                           "all_accepted": all(r.get("accepted") is True for r in hv) and len(hv) == len(honest)}
    zk = inner.get("zk") or {}
    m0 = inner.get("proxy") or {}
    vs = p["vstar_total"]["vstar"]["prove_s"]
    p["terms"] = {"inner_m0_proxy_prove_s": m0.get("prove_s"), "inner_m0_loopback_prove_s": (inner.get("m0") or {}).get("prove_s"),
                  "vstar_zk_prove_s": vs, "vstar_levels_prove_s": p["vstar_total"]["levels"]["prove_s"],
                  "vstar_algebra_prove_s": p["vstar_total"]["algebra"]["prove_s"], "today_zk_prove_s": zk.get("prove_s"),
                  "today_zk_session_s": zk.get("session_s"), "today_zk_serve_verify_s": zk.get("serve_verify_s"),
                  "today_zk_proof_bytes": zk.get("proof_bytes"), "vstar_proof_bytes": p["vstar_total"]["vstar"]["proof_bytes"],
                  "inner_m0_proof_bytes": m0.get("proof_bytes"),
                  "inner_m0_proxy_coin_wait_s": m0.get("wait_e2e_s"), "inner_m0_proxy_compute_s": m0.get("compute_s"),
                  "vstar_zk_coin_wait_s": p["vstar_total"]["vstar"]["wait_e2e_s"], "today_zk_coin_wait_s": zk.get("wait_e2e_s")}
    t = p["terms"]
    if all(isinstance(t[k], (int, float)) for k in ("inner_m0_proxy_prove_s", "vstar_zk_prove_s", "today_zk_prove_s")):
        p["overhead"] = round((t["inner_m0_proxy_prove_s"] + t["vstar_zk_prove_s"]) / t["today_zk_prove_s"], 4)
        p["vstar_over_today_zk"] = round(t["vstar_zk_prove_s"] / t["today_zk_prove_s"], 4)
        p["vstar_over_inner_m0"] = round(t["vstar_zk_prove_s"] / t["inner_m0_proxy_prove_s"], 4)
    # the rec proxy (Python, on the job's verifier cores) answers the inner's coins on its critical path; on node 1's shared
    # cores 96-127 its latency is foreign load, not the prover's, so the overhead is also given with the inner's wait removed
    if all(isinstance(t[k], (int, float)) for k in ("inner_m0_proxy_compute_s", "vstar_zk_prove_s", "today_zk_prove_s")):
        p["overhead_inner_compute"] = round((t["inner_m0_proxy_compute_s"] + t["vstar_zk_prove_s"]) / t["today_zk_prove_s"], 4)
    p["peaks"] = {"vstar_host_gb": p["vstar_total"]["vstar"]["host_peak_gb"], "vstar_gpu_mib": p["vstar_total"]["vstar"]["gpu_peak_mib"],
                  "inner_m0_host_gb": m0.get("host_peak_gb"), "inner_m0_gpu_mib": m0.get("gpu_peak_mib"),
                  "today_zk_host_gb": zk.get("host_peak_gb"), "today_zk_gpu_mib": zk.get("gpu_peak_mib")}
    p["gpu_held_s"] = round(sum(r.get("gpu_held_s") or 0 for r in list(inner.values()) if isinstance(r, dict)) +
                            sum(r.get("gpu_held_s") or 0 for r in list(honest.values()) + list(forged.values())), 1)
    return p


def fmt(x, nd=3):
    if x is None:
        return "—"
    if isinstance(x, float):
        return f"{x:,.{nd}f}"
    if isinstance(x, int):
        return f"{x:,}"
    return str(x)


def table(points: list[dict]) -> str:
    h = ["K", "N", "m", "inner M0 (proxy)", "of it, coin wait", "V* --zk total", "levels", "algebra (parts)", "today's --zk",
         "overhead", "overhead, inner wait removed", "V*/today", "V* bytes", "today bytes", "V* host/GPU peak", "Lean V* verify",
         "Lean today --zk", "build", "inner", "proxy", "vstage", "oprove", "lean"]
    lines = ["| " + " | ".join(h) + " |", "|" + "---:|" * 17 + "---|" * 6]
    for p in points:
        t, vt = p["terms"], p["vstar_total"]
        lean_zk = (p.get("lean") or {}).get("zk", {}).get("verify_s")
        lines.append("| " + " | ".join([
            p.get("label") or fmt(p["K"]), fmt(p["N"]), fmt(p["inner_statement"].get("m")), fmt(t["inner_m0_proxy_prove_s"]) + " s",
            fmt(t["inner_m0_proxy_coin_wait_s"]) + " s",
            fmt(t["vstar_zk_prove_s"]) + " s", fmt(t["vstar_levels_prove_s"]) + " s",
            fmt(t["vstar_algebra_prove_s"]) + f" s ({vt['algebra']['statements']})", fmt(t["today_zk_prove_s"]) + " s",
            fmt(p.get("overhead"), 2) + "×", fmt(p.get("overhead_inner_compute"), 2) + "×",
            fmt(p.get("vstar_over_today_zk"), 2) + "×", fmt(t["vstar_proof_bytes"]),
            fmt(t["today_zk_proof_bytes"]),
            f"{fmt(p['peaks']['vstar_host_gb'], 2)} GB / {fmt(p['peaks']['vstar_gpu_mib'])} MiB",
            fmt((p.get("lean_total") or {}).get("verify_s"), 1) + " s", fmt(lean_zk, 1) + (" s" if lean_zk else ""),
            *["+".join(p["runs"].get(s, [])) or "—" for s in ("build", "inner", "proxy", "vstage", "oprove", "lean")]]) + " |")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=Path, default=Path.home() / ".research" / "runs")
    ap.add_argument("--point", action="append", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--table", type=Path)
    a = ap.parse_args()
    pts = [point(a.runs, dict(kv.split("=", 1) for kv in spec.split(","))) for spec in a.point]
    doc = {"schema": "rec-ksweep/curve/v1", "question": "the recursive witness ZK's prove cost against today's --zk on the same "
           "statement as K grows (Gemm_v2{K, N=4096} coordinate, m = 35)", "source": "cursor/rec-step2-95d4@b6139d9b6",
           "script": "backends/flock/pod/85-rec-reprice.sh", "node": "vy-nebius-1",
           "overhead": "(inner M0 against the rec proxy + V*'s total --zk prove) / today's --zk prove",
           "overhead_inner_compute": "the same with the inner's critical-path wait for the rec proxy's coins removed (median over "
           "the timed sessions of prove_total_s - wait_e2e_s): the Python proxy runs on the job's verifier cores, node 1's shared "
           "96-127, so its latency carries other jobs' load",
           "gpu_held_s_total": round(sum(p["gpu_held_s"] for p in pts if not p.get("label")), 1), "points": pts}
    a.out.write_text(json.dumps(doc, indent=1, sort_keys=False))
    md = table(pts)
    if a.table:
        a.table.write_text(md)
    print(md)


if __name__ == "__main__":
    main()
