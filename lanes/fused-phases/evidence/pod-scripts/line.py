"""One summary line of a bench-vu result.json: t.total, the six buckets' sum / t.total, validation, contract problems."""
import json
import sys

from verity_numerical.bench import contract

r = json.load(open(sys.argv[1]))
m = {x["name"]: x["value"] for x in r.get("measurements", [])}
buckets = ("t.witness", "t.encoding_commitment", "t.arithmetic", "t.lookup", "t.zk_additional", "t.serialization")
s = sum(m.get(b, 0.0) for b in buckets)
tot = m.get("t.total")
probs = contract.validate(r)
rep = ((r.get("validation") or {}).get("evidence") or {}).get("phase_rep")
print(f"t.total={tot:.4f} buckets/total={s / tot:.4f} validation={r['validation']['status']} "
      f"failures={(r['validation'].get('evidence') or {}).get('failures', '?')} contract_problems={len(probs)}"
      f"{' ' + '; '.join(probs) if probs else ''} phase_rep={rep['index'] if rep else 'n/a'}")
