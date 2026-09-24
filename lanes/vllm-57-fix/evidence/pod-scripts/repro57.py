"""#57 offline reproduction over the stored Commit inputs (no GPU): population reconciliation (R17-3) and the oracle's member resolution.

Run on vyv-sw-57 from /workspace/verity/integrations/vllm with PYTHONPATH=.:../../packages/verity/src:../../tools/research/src.
  repro57.py pop      -- ProgramIndex (the manifest's address rule) + population() over every request Program -> query_population checks
  repro57.py oracle   -- MatchOracle over match/ + binding_map_p0.json: which members resolve (committed side = zeros: only reach is read)
"""
import json
import sys
import time
from collections import Counter

R = "/workspace/cp/sweep-v2s/gemma2-2b__bf16__l40s__tp1__b8__i1024__o128__mixed__greedy__bi-eager"
t0 = time.time()


def log(*a):
    print(f"[{time.time() - t0:7.1f}s]", *a, flush=True)


def requests_of_match():
    with open(f"{R}/match/instances.jsonl") as f:
        hdr = json.loads(f.readline())
    return hdr["requests"]


def load_programs():
    from verity_capture.commit import manifest_format as MF
    reqs = requests_of_match()
    fx = {"requests": [{"request_id": f"r{int(r['index'])}", "prompt_len": int(r["prompt_len"]), "max_tokens": int(r["max_tokens"])} for r in reqs]}
    return MF.programs_for(fx, R)


def pop():
    from verity_capture.commit import sampled_replay as SR
    man = json.load(open(f"{R}/manifest.json"))
    log("manifest", len(man["identities"]), "rule", SR.address_rule_of(man))
    loaded = load_programs()
    log("programs", {k: v.get("dir", "").rsplit("/", 1)[-1] for k, v in loaded.items()})
    arrive = {}
    for i in man["identities"]:
        if i.get("step") not in (None, "*") and i.get("engine_step") is not None and i.get("request_id") not in (None, "*"):
            arrive.setdefault(str(i["request_id"]), int(i["engine_step"]) - int(i["step"]))
    addresses, indices, vus_n = {}, {}, 0
    for rid, v in loaded.items():
        inst = v["instances"]
        pi = indices.get(id(inst))
        if pi is None:
            pi = SR.ProgramIndex(inst, padded_slots=SR.manifest_boundary_of(man) == "module-pad", promoted=SR.promoted_addresses_of(man),
                                 rule=SR.address_rule_of(man), program_dir=v.get("dir"))
            indices[id(inst)] = pi
        vus, ne, nef = SR.population(pi, rid, rank=0, arrive=arrive.get(rid, 0), addresses=addresses, last_step=pi.n_steps - 1)
        vus_n += len(vus)
        log(rid, "vus", len(vus), "not-evaluable", sum(ne.values()), "corr", (pi.correspondence or {}).get("reader"))
    qp = SR.query_population(man, addresses, set(), ranks=[0])
    qc = qp["query_checks"]
    log("query_checks ok", qc.get("ok"), "accounted", qc.get("accounted"))
    for k in ("vus_outside_query", "identities_without_rows", "identities_unreachable_by_alias", "rows_disagree"):
        c = qc.get(k) or {}
        log(" ", k, c.get("n"), json.dumps(c.get("first", [])[:3])[:600])
    log("unstated", qc.get("unstated_families"), "total", qp.get("query_total", {}).get("identities") if isinstance(qp.get("query_total"), dict) else qp.get("query_total"))


def oracle(with_program=False):
    from verity_capture.commit import oracle_compare as OC
    man = json.load(open(f"{R}/manifest.json"))
    bm = json.load(open(f"{R}/commit/binding_map_p0.json"))
    producers = OC.producers_of(man)
    if with_program:
        loaded = load_programs()
        derived = OC.producers_of_programs(loaded, aliases=man.get("op_path_aliases"))
        for key in (("model", "out"), ("model.norm", "0"), ("model.norm", "1"), ("model.layers.1.input_layernorm", "0"), ("model.layers.1.input_layernorm", "1")):
            log("  derived", key, json.dumps(derived.get(key))[:300], "| merged", json.dumps(OC.merge_producers(producers, derived).get(key))[:300])
        log("derived producers", len(derived), "selectors", sum(1 for d in derived.values() if d.get("operand")),
            "consumers", sum(1 for d in derived.values() if d.get("consumers")), "conflicts", sum(1 for d in derived.values() if d.get("conflict")))
        producers = OC.merge_producers(producers, derived)
        del loaded
    log("producers", len(producers))
    orc = OC.MatchOracle(f"{R}/match")
    log("oracle loaded, snapshot steps", len(orc.snapshot_steps))
    res = OC.oracle_compare(orc, bm, lambda s, n, lo, hi: b"\0" * (hi - lo), producers=producers,
                            aliases=man.get("op_path_aliases"), query_families=OC.query_families_of(man))
    log("compared", res["compared"], "not_compared_by_family", res.get("not_compared_by_family"))
    c = Counter()
    for k, v in res["not_compared"].items():
        if not k.startswith("no oracle family"):
            import re
            c[re.sub(r"layers\.\d+", "layers.N", k)[:200]] += v
    for k, v in c.most_common(12):
        log("  NOT", v, k)
    log("total not compared (excl. no-oracle families)", sum(c.values()))


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "pop"
    {"pop": pop, "oracle": lambda: oracle(False), "oracle-fixed": lambda: oracle(True)}[what]()
