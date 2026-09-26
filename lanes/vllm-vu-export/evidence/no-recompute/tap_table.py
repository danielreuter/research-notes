import json

t = json.load(open("/tmp/vux/pgn/taps13.json"))


def kind(x):
    a = x["activation"]
    if a.startswith(("AttnBlock", "AttentionHead", "DotBf16")):
        return "guard"
    if a.startswith("RMSNorm"):
        return "norm"
    if a.startswith(("MoeRouter", "NvExpf")):
        return "router"
    if a.startswith("EmbeddingShard"):
        return "vocab"
    return "other"


rows = sorted(t.items(), key=lambda kv: kv[1]["row"] or 0)
print("| Row | Row key | Tokens | Guarded max (FA2/FA3 kernel) | Norm scales (norm kernels) | Router softmax (`topk_softmax`) | Vocabulary-range mask (TP embedding) | **New taps, B/token** | Committed today (FA stream), B/token |")
print("| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
other = []
tot = {}
for key, r in rows:
    by = {}
    today = 0.0
    for x in r["taps"]:
        if x["committed_today"]:
            today += x["bytes_per_token"] or 0
            continue
        k = kind(x)
        b = by.setdefault(k, [0, 0.0])
        b[0] += x["words"]
        b[1] += x["bytes_per_token"] or 0
        if k == "other":
            other.append((r["row"], x))
    cell = lambda k: (f"{by[k][1]:,.0f} B ({by[k][0] / 1e6:,.2f} M words)" if by[k][0] >= 1e5 else f"{by[k][1]:,.0f} B ({by[k][0]:,} words)") if k in by else "–"
    new = sum(v[1] for v in by.values())
    print(f"| {r['row']} | `{key}` | {r['tokens']:,} | {cell('guard')} | {cell('norm')} | {cell('router')} | {cell('vocab')} | **{new:,.0f}** | {today:,.0f} |")
print()
print("other:", other[:10])
