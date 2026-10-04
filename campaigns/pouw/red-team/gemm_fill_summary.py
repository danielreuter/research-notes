# Writer: bc-cb8013f7 (by its own report), an agent the sm_120 PoUW coordinator (bc-2aa33ad8) started by mistake, not the assessor (bc-d7d4b0d1). Not adopted by the assessor as of 30 Sep 2026, 09:20Z.
"""Summarize gemm_fill_sm120.sh's outputs: rates at the measured clock, W1 units per MAC, and the Strassen bounds.

    python3 gemm_fill_summary.py OUT_DIR [--json summary.json]

W1's unit is one dense FP8 E4M3 MAC at 1016 MACs/SM/clk (188 SMs), so a route's price per MAC is 1016 / (its MACs/SM/clk).
`vs_e4m3` and `vs_nvfp4` are the route's speed as a fraction of the same job's cuBLASLt E4M3 and NVFP4 GEMMs at 8192^3
(same GPU, minutes apart).  Strassen: one level's time against the native GEMM at n, and the sub-products-only bounds
7 t(n/2) and 49 t(n/4) of the cuBLASLt sub-product GEMMs, which lower-bound any one- or two-level Strassen route.
"""

import json
import sys
from pathlib import Path

SMS, E4M3_PER_SM_CLK = 188, 1016


def load(out: Path) -> dict:
    rows = {}
    for f in sorted(out.glob("*/*.json")):
        if f.name == "build.json":
            continue
        r = json.loads(f.read_text())
        if "ms_median" not in r:
            continue
        r["group"] = f.parent.name
        rows[(f.parent.name, r["task"], r["m"], r["n"], r["k"])] = r
    return rows


def rate(r: dict) -> dict:
    mhz = r["clock"]["sm_mhz_median"]
    per = r["m"] * r["n"] * r["k"] / (r["ms_median"] * 1e-3) / (SMS * mhz * 1e6)
    return {"macs_per_sm_clk": per, "w1_units_per_mac": E4M3_PER_SM_CLK / per, "mhz": mhz}


def main(argv) -> int:
    out = Path(argv[0])
    rows = load(out)
    summary = {"routes": [], "strassen": []}
    for (g, task, m, n, k), r in rows.items():
        ctl = {c: rows.get((g, c, 8192, 8192, 8192)) for c in ("lt_e4m3", "lt_nvfp4", "lt_bf16")}
        rr = rate(r)
        row = {"group": g, "task": task, "shape": [m, n, k], "ms": r["ms_median"], "tmacs": r["tmacs"],
               "gate": r["gate"]["pass"], "exactness": r.get("exactness"), **rr}
        if (m, n, k) == (8192, 8192, 8192):
            for c, v in ctl.items():
                if v:
                    row["vs_" + c[3:]] = v["ms_median"] / r["ms_median"]
        summary["routes"].append(row)
    s = {(t, m): r for (g, t, m, n, k), r in rows.items() if g == "strassen"}
    for n in (8192, 16384):
        if ("strassen1_e4m3_f16", n) not in s:
            continue
        st = s[("strassen1_e4m3_f16", n)]
        ref = {c: s[(c, n)]["ms_median"] for c in ("lt_e4m3", "lt_e4m3_f32", "lt_nvfp4", "lt_f16_f32") if (c, n) in s}
        bounds = {}
        for sub in ("lt_f16_f32", "lt_e4m3_f32"):
            for lvl, d, mult in ((1, 2, 7), (2, 4, 49)):
                if (sub, n // d) in s:
                    bounds[f"{sub}/level{lvl}"] = mult * s[(sub, n // d)]["ms_median"]
        summary["strassen"].append({"n": n, "strassen1_ms": st["ms_median"], "components_ms": st.get("components_ms"),
                                    "native_ms": ref, "subproduct_bounds_ms": bounds,
                                    "speed_vs_native": {c: t / st["ms_median"] for c, t in ref.items()},
                                    "bound_speed_vs_native": {f"{b} vs {c}": ref[c] / t for b, t in bounds.items()
                                                              for c in ref}})
    for r in sorted(summary["routes"], key=lambda r: (r["group"], r["task"], r["shape"])):
        vs = " ".join(f"{k}={r[k]:.3f}" for k in ("vs_e4m3", "vs_nvfp4", "vs_bf16") if k in r)
        print(f"{r['group']:9s} {r['task']:28s} {'x'.join(map(str, r['shape'])):17s} {r['ms']:9.3f} ms "
              f"{r['tmacs']:7.1f} TMAC/s {r['macs_per_sm_clk']:7.1f}/SM/clk W1 {r['w1_units_per_mac']:6.2f} "
              f"gate {'ok' if r['gate'] else 'FAIL'} {vs}")
    for x in summary["strassen"]:
        print(json.dumps(x))
    if "--json" in argv:
        Path(argv[argv.index("--json") + 1]).write_text(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
