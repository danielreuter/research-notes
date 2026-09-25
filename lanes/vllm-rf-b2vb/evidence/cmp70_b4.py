"""Row #70 Commit: this lane's head summary.json vs f1's base Commit of record (commit70-base-head.tgz, sweep/...).  Per-pair
quantities are compared per pair (head PAIRS=1, the base 3).   usage: python3 cmp70.py HEAD_SUMMARY BASE_SUMMARY"""
import json
import re
import sys

h, b = (json.load(open(p)) for p in sys.argv[1:3])
rows = []


def unpath(s):
    return re.sub(r"/workspace/\S*?/(olmoe-)", r"<sweep>/\1", s) if isinstance(s, str) else s


def eq(name, x, y):
    rows.append((name, x == y, x, y))


eq("tp_run_root (every pair)", sorted(set(h["tp_run_roots"])), sorted(set(b["tp_run_roots"])))
eq("per_rank_roots (every pair)", {json.dumps(r, sort_keys=True) for r in h["per_rank_roots"]},
   {json.dumps(r, sort_keys=True) for r in b["per_rank_roots"]})
for rank in ("0", "1"):
    hc, bc = h["per_rank_coverage"][0][rank], b["per_rank_coverage"][0][rank]
    for k in ("leaves", "tensors", "bytes_bound"):
        eq(f"rank {rank} {k}", hc[k], bc[k])
    eq(f"rank {rank} classes", hc["classes"], bc["classes"])
    eq(f"rank {rank} openings verified/n", (hc["openings"]["verified"], hc["openings"]["n"]),
       (bc["openings"]["verified"], bc["openings"]["n"]))
eq("tokens_equal all", all(h["tokens_equal"]), all(b["tokens_equal"]))
eq("commit_pass (every pair)", set(h["commit_pass"]), set(b["commit_pass"]))
eq("pass", h["pass"], b["pass"])
eq("value_check", h["value_check"], b["value_check"])
for rank in ("0", "1"):
    hm, bm = h["match_oracle"][rank], b["match_oracle"][rank]
    eq(f"match_oracle rank {rank}", {k: hm[k] for k in ("verdict", "tensors", "equal", "mismatch_n", "missing_n")},
       {k: bm[k] for k in ("verdict", "tensors", "equal", "mismatch_n", "missing_n")})
for k in ("sampled_replay", "boundary_linkage", "cross_rank_collectives", "fold_match_binding", "query_population", "weights_pin"):
    eq(f"{k}.result", h[k]["result"], b[k]["result"])
hx, bx = h["cross_rank_collectives"], b["cross_rank_collectives"]
eq("cross_rank_collectives picks / pair", hx["picks"] / hx["pairs"], bx["picks"] / bx["pairs"])
eq("cross_rank_collectives equal == picks", hx["equal"] == hx["picks"], bx["equal"] == bx["picks"])
eq("fold_match_binding.why", unpath(h["fold_match_binding"].get("why")), unpath(b["fold_match_binding"].get("why")))
eq("weights_pin roots of record", {r: v["root_of_record"] for r, v in h["weights_pin"]["per_rank"].items()},
   {r: v["root_of_record"] for r, v in b["weights_pin"]["per_rank"].items()})
eq("query_population counts", {r: v.get("counts") for r, v in h["query_population"]["per_rank"].items()},
   {r: v.get("counts") for r, v in b["query_population"]["per_rank"].items()})
eq("required manifest digest", h["required_manifest"]["manifest_digest"], b["required_manifest"]["manifest_digest"])
eq("required_classes", h["required_classes"], b["required_classes"])
eq("committer / openings", (h["committer"], h["openings"]), (b["committer"], b["openings"]))

bad = [r for r in rows if not r[1]]
for name, ok, x, y in rows:
    print(("OK  " if ok else "DIFF"), name, "" if ok else f"head={json.dumps(x)[:300]} base={json.dumps(y)[:300]}")
print(f"{len(rows) - len(bad)}/{len(rows)} equal; pairs head {h['pairs']} base {b['pairs']}")
