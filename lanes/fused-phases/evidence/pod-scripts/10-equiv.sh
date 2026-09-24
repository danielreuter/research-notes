#!/usr/bin/env bash
# fused-phases: (1) which instances ref each relation a fill run would use carries at B = 4096, vs tables.FROZEN_INSTANCES
# (dataset / tier / range / manifest_sha256); (2) instance-equiv/v1 for every derived relation of fp8-ada, bf16-hopper,
# fp8-hopper (v2, v3, v2x4, v3x4, x4): both sides by their own loaders -> canonical x, W, y digests.  CPU only.
source /workspace/fused-phases/scripts/lib.sh
cd /workspace/src
E=$FP/equiv; mkdir -p $E
RESEARCH_GIT_COMMIT=$TIP OMP_NUM_THREADS=1 $PY - <<'PY' 2>&1 | tee $E/refs.txt
from backends.direct.ligero import relchain
from backends.direct.ligero.relations import RELATIONS
from backends.direct.ligero.fp4 import chain as fp4chain
from verity_numerical.bench.instance_equiv import same_ref
from verity_numerical.bench.tables import FROZEN_INSTANCES
for name, r in sorted(RELATIONS.items()):
    want = FROZEN_INSTANCES.get(r.target.name)
    ref = relchain.instances_ref(r, 4096)
    print(f"{name:18s} {r.target.name:34s} {'FROZEN' if want and same_ref(ref, want) else 'other '} {ref['manifest_sha256'][:12]}")
want = FROZEN_INSTANCES["nvfp4-sm120-mma-draft/2026-09-22"]
print(f"{'fp4-nvf4 (chain)':18s} {'nvfp4-sm120-mma-draft/2026-09-22':34s} {'FROZEN' if same_ref(fp4chain._instances(4096), want) else 'other '}")
PY
RELS=""
for b in fp8-ada bf16-hopper fp8-hopper; do RELS="$RELS $b-v2 $b-v3 $b-v2x4 $b-v3x4 $b-x4"; done
args=(); for r in $RELS; do args+=(--relation $r); done
t0=$(date +%s)
RESEARCH_GIT_COMMIT=$TIP OMP_NUM_THREADS=1 $PY -m verity_numerical.bench.instance_equiv "${args[@]}" --out-dir $E --procs ${VY_CPU_THREADS:-8} 2>&1 | tee $E/log.txt
echo "EQUIV_DONE rc=${PIPESTATUS[0]} $(( $(date +%s) - t0 ))s" | tee -a $E/log.txt
