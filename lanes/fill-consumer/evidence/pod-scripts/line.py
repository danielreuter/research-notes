"""One summary line of a bench-vu result.json: t.total, t.total_live, buckets / t.total, validation, contract, contention."""
import json
import sys

from verity_numerical.bench import contract

r = json.load(open(sys.argv[1]))
m = {x["name"]: x.get("value") for x in r.get("measurements", []) if isinstance(x, dict) and "name" in x}
buckets = ("t.witness", "t.encoding_commitment", "t.arithmetic", "t.lookup", "t.zk_additional", "t.serialization")
s = sum(m.get(b) or 0.0 for b in buckets)
tot = m.get("t.total")
probs = contract.validate(r)
c = r.get("contention") or (r.get("workload_fingerprint") or {}).get("contention") or {}
live = m.get("t.total_live")
print(f"t.total={tot:.4f} live={live if live is None else round(live, 4)} rtt_ms={m.get('net.rtt_ms')} "
      f"buckets/total={s / tot:.4f} validation={r['validation']['status']} contract_problems={len(probs)}"
      f"{' ' + '; '.join(probs) if probs else ''} contended={c.get('contended', '?')} bytes={m.get('proof_bytes')}")
