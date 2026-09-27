"""Markdown tables from the census JSONs and analysis.json."""
import glob
import json
import re
import sys
from collections import defaultdict

OUT = sys.argv[1]
A = json.load(open(f"{OUT}/analysis-main.json"))
for _m in ("z", "d"):
    try:
        A["shapes"].update(json.load(open(f"{OUT}/analysis-{_m}.json"))["shapes"])
    except FileNotFoundError:
        pass
C = {json.load(open(f))["row"]: json.load(open(f)) for f in sorted(glob.glob(f"{OUT}/*.json")) if "analysis" not in f}


def short(k):
    p = k.split("__")
    s = f"{p[0]} {p[2].upper()}" + (f" {p[3]}" if p[3] != "tp1" else "") + f" {p[4]} {p[5]}"
    if p[7] != "mixed":
        s += " arrivals"
    if "stoch" in p[8]:
        s += " sampled"
    return s


def lbl(scope, kind, head):
    fam = (scope or head or "?").split("{")[0]
    K = re.search(r"K=(\d+)", scope or "")
    Kx = f", K = {K.group(1)}" if K else ""
    t = {
        "GemmCoordinate_v1": f"GEMM coordinate (Ampere BF16){Kx}", "GemmCoordinate_v2": f"GEMM coordinate (Hopper BF16){Kx}",
        "ScaledMmFp8BlockCoordinate_v1": f"GEMM coordinate (FP8 block-scaled){Kx}", "MoeExpertCoordinateW_v1": f"MoE expert coordinate{Kx}",
        "RopeOut_v1": "RoPE output", "RopeOutAdd_v1": "RoPE output", "SiluMulBf16_v1": "SiLU·mul", "GeluTanhMulBf16_v1": "GELU(tanh)·mul",
        "ArgmaxStep_v1": "greedy argmax over the vocabulary", "GumbelSelectStep_v1": "Gumbel top-p sampler (whole vocabulary)",
    }.get(fam)
    if t:
        return t
    if fam.startswith("DotBf16"):
        return "attention score (Q·K)"
    if fam.startswith(("AttentionHead",)):
        return "attention output (P·V), all T" if kind == "output" else {"Fa2InvSum_v1": "attention row sum and 1/sum",
                "Fa3InvSum_v1": "attention row sum and 1/sum"}.get(head, f"attention {head.split('_')[0]} (per head)")
    if fam.startswith("AttnBlock"):
        return {"MufuEx2Ftz_v1": "attention probability (exp)", "F2fpBf16_v1": "attention probability (bf16 cast)",
                "MufuTanh_v1": "attention softcapped score", "F32Max_v1": "attention row max", "F32MulFtz_v1": "attention block rescale",
                "GuardNegInfZero_v1": "attention -inf guard"}.get(head, f"attention block {head}")
    if fam.startswith("RMSNorm"):
        return f"{fam.split('_')[0]} {'output' if kind == 'output' else 'row scalar'}"
    if fam.startswith("Gather"):
        return "embedding gather"
    return f"{fam.split('_v')[0]} ({kind}, {head.split('_v')[0] if head else '-'})"


def e2(x):
    return f"$2^{{{x}}}$"


def rng(xs):
    xs = sorted(set(xs))
    return e2(xs[0]) if len(xs) == 1 else f"{e2(xs[0])}–{e2(xs[-1])}"


def fmt(x):
    if x >= 1e12:
        return f"{x / 1e12:.2f} T"
    if x >= 1e9:
        return f"{x / 1e9:.2f} G"
    if x >= 1e6:
        return f"{x / 1e6:.1f} M"
    if x >= 1e3:
        return f"{x / 1e3:.1f} k"
    return f"{x:.0f}"


def lg(x):
    return int(x).bit_length() - 1


def families(row):
    fam = defaultdict(lambda: {"units": 0, "rows": 0, "R": [], "Z": [], "D": [], "maxD": 0, "lk": 0, "est": set()})
    for c in C[row]["classes"]:
        f = fam[lbl(c["scope"], c["kind"], c["head"])]
        f["units"] += c["count"]
        f["rows"] += c["count"] * c["rows"]
        f["R"].append(lg(c["R"]))
        f["Z"].append(lg(1 << max(0, (max(c["z"], 1) - 1).bit_length())))
        f["D"].append(lg(1 << max(0, (max(c["D"], 1) - 1).bit_length())))
        f["maxD"] = max(f["maxD"], c["D"])
        f["lk"] = max(f["lk"], c["lookups"])
        f["est"] |= set(c["estimated"])
    return fam


def program_table(row, top_units=0.98, top_rows=0.995, cap=12):
    fam = families(row)
    n = sum(f["units"] for f in fam.values())
    w = sum(f["rows"] for f in fam.values())
    keep = set()
    acc = 0
    for k, f in sorted(fam.items(), key=lambda kv: -kv[1]["units"]):
        if acc / n < top_units:
            keep.add(k)
        acc += f["units"]
    acc = 0
    for k, f in sorted(fam.items(), key=lambda kv: -kv[1]["rows"]):
        if acc / w < top_rows:
            keep.add(k)
        acc += f["rows"]
    lines = ["| unit family | units | share of units | share of rows | $R$ | $Z$ | $D$ |", "|---|---:|---:|---:|---|---|---|"]
    rest = {"units": 0, "rows": 0, "R": [], "Z": [], "D": [], "k": 0}
    keep = set(sorted(keep, key=lambda k: -fam[k]["rows"])[:cap])
    for k, f in sorted(fam.items(), key=lambda kv: -kv[1]["rows"]):
        if k not in keep:
            rest["units"] += f["units"]
            rest["rows"] += f["rows"]
            rest["R"] += f["R"]
            rest["Z"] += f["Z"]
            rest["D"] += f["D"]
            rest["k"] += 1
            continue
        mark = "*" if f["est"] else ""
        lines.append(f"| {k}{mark} | {fmt(f['units'])} | {100 * f['units'] / n:.2f}% | {100 * f['rows'] / w:.2f}% | {rng(f['R'])} | {rng(f['Z'])} | {rng(f['D'])} |")
    if rest["k"]:
        lines.append(f"| {rest['k']} other families | {fmt(rest['units'])} | {100 * rest['units'] / n:.2f}% | {100 * rest['rows'] / w:.2f}% | "
                     f"{rng(rest['R'])} | {rng(rest['Z'])} | {rng(rest['D'])} |")
    return n, w, "\n".join(lines)


def hist_table():
    tot = {"R": defaultdict(float), "Rw": defaultdict(float), "Z": defaultdict(float), "D": defaultdict(float)}
    for row, p in A["programs"].items():
        for k in ("R", "Z", "D"):
            for b, v in p["hist"][k].items():
                tot[k][int(b)] += v
        for b, v in p["hist"]["Rw"].items():
            tot["Rw"][int(b)] += v
    nR, nW, nZ, nD = (sum(tot[k].values()) for k in ("R", "Rw", "Z", "D"))
    lo = min(min(tot["R"]), min(tot["D"]), min(tot["Z"]))
    hi = max(max(tot["R"]), max(tot["Z"]), max(tot["D"]))
    lines = ["| bucket | units with this $R$ | rows (work) in units with this $R$ | units with this $Z$ | units with this $D$ |", "|---|---:|---:|---:|---:|"]
    for b in range(lo, hi + 1):
        cells = [tot["R"].get(b, 0) / nR, tot["Rw"].get(b, 0) / nW, tot["Z"].get(b, 0) / nZ, tot["D"].get(b, 0) / nD]
        if not any(cells):
            continue
        lines.append(f"| {e2(b)} | " + " | ".join(f"{100 * c:.2f}%" if c >= 5e-5 else ("<0.01%" if c else "") for c in cells) + " |")
    return "\n".join(lines)


def shape_rows(keys, per_program=False):
    lines = ["| $S = (R, Z, D)$ | $n$ (all 13) | row waste | $Z$ waste | $D$ waste | units split | extra commitments | per fine unit |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    nfine = sum(p["n"] for p in A["programs"].values())
    for s in keys:
        v = A["shapes"][s]
        n = sum(a["n"] for a in v.values())
        used = [sum(a["used"][i] for a in v.values()) for i in range(3)]
        R, Z, D = (1 << int(x) for x in s.split(","))
        ex = sum(a["extra_commitments"] for a in v.values())
        sp = sum(a["split_units"] for a in v.values())
        ov = sum(a["oversize_gates"] for a in v.values())
        r, z, d = s.split(",")
        lines.append(f"| ({e2(r)}, {e2(z)}, {e2(d)}) | {fmt(n)} | {100 * (1 - used[0] / (n * R)):.1f}% | {100 * (1 - used[1] / (n * Z)):.1f}% | "
                     f"{100 * (1 - used[2] / (n * D)):.1f}% | {fmt(sp)} | {fmt(ex)} | {ex / nfine:.2f} |" + (f" oversize {fmt(ov)}" if ov else ""))
    return "\n".join(lines)


def per_program(keys):
    head = "| program | fine units | useful rows | " + " | ".join(f"$n$ at $R = {e2(k.split(',')[0])}$" for k in keys) + " | " + \
        " | ".join(f"padded work at {e2(k.split(',')[0])}" for k in keys) + " | " + " | ".join(f"extra per fine unit at {e2(k.split(',')[0])}" for k in keys) + " |"
    lines = [head, "|" + "---|" * (3 + 3 * len(keys))]
    for row, p in A["programs"].items():
        cells = [short(row), fmt(p["n"]), f"{p['rows']:.2e}"]
        cells += [fmt(A["shapes"][k][row]["n"]) for k in keys]
        cells += [f"{A['shapes'][k][row]['n'] * (1 << int(k.split(',')[0])) / p['rows']:.2f}×" for k in keys]
        cells += [f"{A['shapes'][k][row]['extra_commitments'] / p['n']:.2f}" for k in keys]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def robustness(diag):
    lines = ["| program | best $R$ (least padded work) | padded work there | extra per fine unit there | padded work at the pick | vs its best |", "|---|---|---:|---:|---:|---:|"]
    return lines


def mixes(limit=3):
    nf = sum(p["n"] for p in A["programs"].values())
    wf = sum(p["rows"] for p in A["programs"].values())
    by = defaultdict(list)
    for m, v in A["mixes"].items():
        pr = sum(v[k]["padded_rows"] for k in v)
        ex = sum(v[k]["extra_commitments"] for k in v)
        ns = defaultdict(float)
        for k in v:
            for s_, x in v[k]["n"].items():
                ns[s_] += x
        by[(len(m.split("|")), m.split("|")[-1])].append((pr / wf, m, ex / nf, dict(ns)))
    lines = ["| shapes ($R$ of each; $Z = 32R$, $D = R/256$) | padded work | row waste | extra per fine unit | $n$ per shape |", "|---|---:|---:|---:|---|"]
    for (cnt, big) in sorted(by, key=lambda t: (int(t[1]), t[0])):
        pr, m, ex, ns = sorted(by[(cnt, big)])[0]
        lines.append(f"| {', '.join(e2(x) for x in m.split('|'))} | {pr:.2f}× | {100 * (1 - 1 / pr):.1f}% | {ex:.2f} | "
                     + ", ".join(fmt(ns[k]) for k in sorted(ns, key=lambda k: int(k.split(',')[0]))) + " |")
    return "\n".join(lines)


def outliers(top=14):
    seen = {}
    for row, c in C.items():
        for x in c["classes"]:
            k = (lbl(x["scope"], x["kind"], x["head"]), x["rows"], x["z"], x["D"])
            e = seen.setdefault(k, [x, set(), 0])
            e[1].add(short(row).split()[0])
            e[2] += x["count"]
    rows_ = sorted(seen.values(), key=lambda e: -e[0]["rows"])
    lines = ["| unit | rows | $R$ | $Z$ | $D$ | units (all programs) | programs |", "|---|---:|---|---:|---:|---:|---|"]
    fams = set()
    for x, progs, cnt in rows_:
        f = lbl(x["scope"], x["kind"], x["head"])
        if f in fams:
            continue
        fams.add(f)
        lines.append(f"| {f}{' (' + x['scope'].split('{')[1].rstrip('}') + ')' if x['scope'] and '{' in x['scope'] and 'GEMM' not in f else ''} | {x['rows']:,} | {e2(lg(x['R']))} | {x['z']:.3g} | {x['D']:,} | {fmt(cnt)} | {', '.join(sorted(progs))} |")
        if len(lines) >= top + 2:
            break
    return "\n".join(lines)


if __name__ == "__main__":
    for row in C:
        n, w, t = program_table(row)
        print(f"\n### {short(row)}\n\n{fmt(n)} units, {w:.3g} rows.\n\n{t}")
    print("\n" + hist_table())
    print("\n" + shape_rows(sorted(A["shapes"], key=lambda s: tuple(int(x) for x in s.split(",")))))
