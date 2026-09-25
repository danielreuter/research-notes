#!/usr/bin/env bash
# b-ligero-standard-hash (pod, over `research pods ssh`, backgrounded; coordinator 1105Z / 1114Z): the instance-equiv/v1 document
# of fp8-ada-x4 at B = 4096 (verity_numerical.bench.instance_equiv, fused-phases' tool, on the synced tree), its --check, then
# `research data put --kind instance-equiv/v1 --meta @doc --preserve` (the document IS the meta, + lane attribution).  Also the
# prefix evidence for the 8192 plateau: the first 4096 VUs of instances(fp8-ada-x4, 8192) against the frozen set's arrays.
#   nohup bash 42-equiv.sh > /workspace/b-lsh/equiv.log 2>&1 &
set -uo pipefail
W=/workspace/b-lsh; O=$W/equiv; mkdir -p $O
cd /workspace/src
source /workspace/env.sh
export PYTHONPATH="$(pwd)/packages/verity/src:$(pwd)/backends/numerical/python:$(pwd)/tools/research/src:$(pwd)"
NT=${VY_CPU_THREADS:-8}
$PY -m verity_numerical.bench.instance_equiv --relation fp8-ada-x4 --vus 4096 --procs $NT --out $O/instance-equiv-fp8-ada-x4-4096.json
echo "derive rc=$?"
$PY -m verity_numerical.bench.instance_equiv --check $O/instance-equiv-fp8-ada-x4-4096.json --vus 4096 --procs $NT
echo "check rc=$?"
$PY - $O $NT <<'PY'
import hashlib, json, sys
import numpy as np
from verity_numerical.bench import instance_equiv as E
out, nt = sys.argv[1], int(sys.argv[2])
relchain, RELATIONS, _ = E._runner()
x4 = RELATIONS["fp8-ada-x4"]
base, want = E.frozen_relation(x4.target.name, 4096)
f4 = E.arrays(relchain.instances(base, 4096, procs=nt), base.word_dtype)
a8 = E.arrays(relchain.instances(x4, 8192, procs=nt), x4.word_dtype)
sha = lambda a: hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()
doc = {"what": "prefix of the x4 8192 set vs the frozen 4096 set", "frozen_relation": base.name, "frozen": want,
       "candidate_8192": relchain.instances_ref(x4, 8192),
       "arrays": {k: {"frozen_sha256": sha(f4[k]), "candidate_prefix_sha256": sha(a8[k][:4096]), "candidate_rows": int(a8[k].shape[0])}
                  for k in ("x", "W", "y")}}
doc["prefix_equal"] = all(v["frozen_sha256"] == v["candidate_prefix_sha256"] for v in doc["arrays"].values())
open(out + "/prefix-fp8-ada-x4-8192.json", "w").write(json.dumps(doc, indent=2) + "\n")
print("prefix_equal", doc["prefix_equal"], "candidate_8192", doc["candidate_8192"])
PY
echo "prefix rc=$?"
python3 - $O/instance-equiv-fp8-ada-x4-4096.json > $O/meta.json <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
assert d["equal"] is True
d["lane"] = "b-ligero-standard-hash"
print(json.dumps(d))
PY
[ $? -eq 0 ] || { echo "not equal: nothing registered"; exit 1; }
set -a; . $W/r2.env; set +a
C=$W/store.pod.toml
TOOL=$(ls -td /workspace/research/tool/*/ | head -1)
PYTHONPATH=$TOOL RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG="$C" \
  python3 -m research data put --kind instance-equiv/v1 --meta @$O/meta.json --preserve 2>&1 | grep -vi secret | tail -3
echo "put rc=${PIPESTATUS[0]}"
