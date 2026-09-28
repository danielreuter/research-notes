"""s1_ab.py OUT.json PROGRAM_DIR... : the S1 A/B on stored Builds (lane vllm-epoch-prep). Per request Program dir, `manifest.build` under
Q_module_body_v1 (A, today's record) and under Q_word (B, the query of record after S1): identities only in A / only in B by family, the
manifest digests, what the header changed, the partition object's digest; then the strict word check of record under B (widths,
recomputes, committed Call boundaries) -- PASS, or the violation it names."""
import json
import sys
import time
from collections import Counter

from verity_vllm.pipeline import manifest as MF
from verity_vllm.query import word as W
from verity_vllm.query.required import Q_MODULE_BODY_ID


def key(r: dict) -> tuple:
    return (r["family"], r["step"], r["invocation"], r["op_path"], r["output_member"], tuple(r["element_range"]), r["rank"])


def one(d: str) -> dict:
    t = time.time()
    a = MF.build(d, query=Q_MODULE_BODY_ID)
    b = MF.build(d)
    ka, kb = Counter(key(r) for r in a["identities"]), Counter(key(r) for r in b["identities"])
    only_a, only_b = ka - kb, kb - ka
    qa, qb = a["query"], b["query"]
    try:
        MF.build(d, word="16/32")
        strict = "PASS"
    except W.QueryRuleViolation as e:
        strict = f"FAIL: {str(e)[:600]}"
    return {"dir": d, "program_digest": b["program_digest"], "identities": [a["populations"]["identities"], b["populations"]["identities"]],
            "manifest_digest": [a["manifest_digest"], b["manifest_digest"]], "manifest_digest_equal": a["manifest_digest"] == b["manifest_digest"],
            "complete": [a["complete"], b["complete"]], "unmodelled_b": b["unmodelled"],
            "only_a_by_family": dict(Counter(k[0] for k in only_a.elements())), "only_b_by_family": dict(Counter(k[0] for k in only_b.elements())),
            "header_keys_changed": sorted(k for k in set(qa) | set(qb) if qa.get(k) != qb.get(k)),
            "query_id": [qa["query_id"], qb["query_id"]], "partition": qb.get("partition"), "strict_word_check_b": strict,
            "secs": round(time.time() - t, 1)}


def main() -> None:
    rows = []
    for d in sys.argv[2:]:
        r = one(d)
        rows.append(r)
        print(f"{d}: ids A/B {r['identities']} digest_equal={r['manifest_digest_equal']} only_b={r['only_b_by_family']} only_a={r['only_a_by_family']} "
              f"complete={r['complete']} partition={(r['partition'] or {}).get('digest', '')[:16]} strict={r['strict_word_check_b'][:160]} {r['secs']}s", flush=True)
    json.dump({"schema": "vllm-epoch-prep/s1-ab/v1", "rows": rows}, open(sys.argv[1], "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
