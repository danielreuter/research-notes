import sys, json, pickle, glob, __main__
from collections import defaultdict
sys.argv = ['render.py', '/tmp/census/out']
exec(open('/tmp/census/render.py').read().split('if __name__ == "__main__":')[0])
for f in ("pick",):
    A["shapes"].update(json.load(open(f"/tmp/census/out/analysis-{f}.json")))
P = A["programs"]
nf = sum(p["n"] for p in P.values()); wf = sum(p["rows"] for p in P.values()); zf = sum(p["z"] for p in P.values()); df = sum(p["d"] for p in P.values())
BETA = 512


def tot(s):
    v = A["shapes"][s]
    R, Z, D = (1 << int(x) for x in s.split(","))
    n = sum(a["n"] for a in v.values())
    used = [sum(a["used"][i] for a in v.values()) for i in range(3)]
    return dict(R=R, Z=Z, D=D, n=n, used=used, ex=sum(a["extra_commitments"] for a in v.values()),
                sp=sum(a["split_units"] for a in v.values()), ov=sum(a["oversize_gates"] for a in v.values()))


def srow(s, t):
    r, z, d = s.split(",")
    wr = 1 - t["used"][0] / (t["n"] * t["R"])
    comb = 1 - (wf + BETA * df) / (t["n"] * (t["R"] + BETA * t["D"]))
    return (f"| ({e2(r)}, {e2(z)}, {e2(d)}) | {fmt(t['n'])} | {t['n'] / nf:.1f}× | {100 * wr:.1f}% | {100 * (1 - t['used'][1] / (t['n'] * t['Z'])):.1f}% | "
            f"{100 * (1 - t['used'][2] / (t['n'] * t['D'])):.1f}% | {100 * comb:.1f}% | {100 * t['sp'] / nf:.1f}% | {t['ex'] / nf:.2f} | {4 * t['ex'] / 1e12:.2f} TB |")


H = ("| $S = (R, Z, D)$ | $n$ | $n$ / fine units | row waste | $Z$ waste | $D$ waste | waste with binding | fine units split | extra commitments per fine unit | extra FP32 bytes |\n"
     "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
diag = sorted([s for s in A["shapes"] if int(s.split(",")[1]) - int(s.split(",")[0]) == 5 and int(s.split(",")[0]) - int(s.split(",")[2]) == 8],
              key=lambda s: int(s.split(",")[0]))
print("### FRONTIER\n\n" + H + "\n" + "\n".join(srow(s, tot(s)) for s in diag))
var = sorted([s for s in A["shapes"] if s not in diag and 15 <= int(s.split(",")[0]) <= 19], key=lambda s: tuple(int(x) for x in s.split(",")))
print("\n### VARIANTS\n\n" + H + "\n" + "\n".join(srow(s, tot(s)) for s in var))

REC, ALT = "16,21,8", "18,23,10"
lines = ["| program | fine units | $n$ | padded rows | row waste | fine units split | extra per fine unit | extra FP32 bytes | $n$ at the fallback | padded rows there | extra per fine unit there |",
         "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
for row, p in P.items():
    a, b = A["shapes"][REC][row], A["shapes"][ALT][row]
    lines.append(f"| {short(row)} | {fmt(p['n'])} | {fmt(a['n'])} | {a['n'] * (1 << 16) / p['rows']:.2f}× | {100 * a['waste_rows']:.1f}% | "
                 f"{100 * a['split_units'] / p['n']:.1f}% | {a['extra_commitments'] / p['n']:.2f} | {4 * a['extra_commitments'] / 1e9:.0f} GB | "
                 f"{fmt(b['n'])} | {b['n'] * (1 << 18) / p['rows']:.2f}× | {b['extra_commitments'] / p['n']:.2f} |")
print("\n### PERPROGRAM\n\n" + "\n".join(lines))

lines = ["| program | least padded rows at $R =$ | padded rows there | padded rows at $2^{16}$ |", "|---|---|---:|---:|"]
for row, p in P.items():
    best = min(diag, key=lambda s: A["shapes"][s][row]["n"] * (1 << int(s.split(",")[0])))
    pb = A["shapes"][best][row]["n"] * (1 << int(best.split(",")[0])) / p["rows"]
    lines.append(f"| {short(row)} | {e2(best.split(',')[0])} | {pb:.2f}× | {A['shapes'][REC][row]['n'] * (1 << 16) / p['rows']:.2f}× |")
print("\n### ROBUST\n\n" + "\n".join(lines))

# split families at REC
sys.path[:0] = ["/workspace/packages/verity/src", "/workspace/backends/numerical/python", "/workspace/backends/flock/python", "/workspace/integrations/vllm"]
from verity_flock import unit_shapes as US
__main__.UnitShape = US.UnitShape
S = (1 << 16, 1 << 21, 1 << 8)
fam = defaultdict(lambda: [0, 0, 0, set(), set()])
for pk in sorted(glob.glob("/tmp/census/out/*.pkl")):
    row = pk.split("/")[-1][:-4]
    for u, cnt, tp in pickle.load(open(pk, "rb")):
        if u.R <= S[0] and u.z <= S[1] and u.d <= S[2]:
            continue
        p = US.pack_best(u.seq, *S) if u.seq else {"pieces": 1, "extra": 0, "oversize": 1}
        f = fam[lbl(u.scope, u.kind, u.head)]
        f[0] += cnt; f[1] += cnt * p["pieces"]; f[2] += cnt * p["extra"]
        f[3].add(p["pieces"]); f[4].add(short(row).split()[0])
lines = ["| unit family | units split | pieces per unit | commitments added | share of all extra commitments |", "|---|---:|---|---:|---:|"]
T = sum(f[2] for f in fam.values())
for k, f in sorted(fam.items(), key=lambda kv: -kv[1][2])[:14]:
    ps = sorted(f[3])
    lines.append(f"| {k} | {fmt(f[0])} | {ps[0]}{'–' + str(ps[-1]) if len(ps) > 1 else ''} | {fmt(f[2])} | {100 * f[2] / T:.1f}% |")
print("\n### SPLITS\n\n" + "\n".join(lines))
print(f"\nfine {nf:.4e} rows {wf:.4e} z {zf:.4e} d {df:.4e}")
