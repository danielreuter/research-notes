#!/usr/bin/env bash
# bligero-real-k: fixtures + gadget gates of the real-K systems (the x4 folds at K = 2048 / 8192 under blake3-xob and sha256).
# Per system: leaf.fixtures (compose, one proved sub-batch), the pod's ligero-verify system-digest must name the committed PINS
# row ("<rel>+<leaf>"), the pinned Rust verify of the fixture must accept; then gate-vu --auth included-hash (honest sub-batches
# with the reference hint check + the negatives battery).  SYSTEMS="rel+leaf:vus ..."; summary in $RESEARCH_RUN_DIR/gates.json.
#   research run --on vy-bligero-real-k-gate --project verity --source . --cwd source --custody-r2 --custody-ttl 12h \
#     --send 10-gates.sh --env SYSTEMS="..." -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/10-gates.sh"'
REPO=$(pwd); RD=${RESEARCH_RUN_DIR:?}
echo "=== $(date -u +%H:%M:%SZ) bootstrap"
SRC=$REPO RELS= bash backends/direct/ligero/pod_bootstrap.sh > $RD/bootstrap.log 2>&1; echo "bootstrap rc=$?"; tail -n 4 $RD/bootstrap.log
source /workspace/env.sh; cd "$REPO"
Q=$(cat /sys/fs/cgroup/cpu.max 2>/dev/null | cut -d' ' -f1); P=$(cat /sys/fs/cgroup/cpu.max 2>/dev/null | cut -d' ' -f2)
NT=$([ "${Q:-max}" = max ] && nproc || echo $(( Q / P ))); [ "$NT" -lt 1 ] && NT=1
export OMP_NUM_THREADS=$NT MKL_NUM_THREADS=$NT OPENBLAS_NUM_THREADS=$NT VY_CPU_THREADS=$NT
export MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000 LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
V=/workspace/bin/ligero-verify; sha256sum $V; nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
mkdir -p $RD/fixtures $RD/gates
for s in ${SYSTEMS:?}; do
  rl=${s%%:*}; vus=${s##*:}; rel=${rl%%+*}; leaf=${rl##*+}; F=$RD/fixtures/$rel-$leaf
  echo "=== $(date -u +%H:%M:%SZ) fixture $rl"
  $PY -u -m backends.direct.ligero.leaf.fixtures --relation $rel --leaf $leaf --device cuda --out $F > $F.log 2>&1; echo "fixture rc=$?"
  $V system-digest --system $F/system.bin > $F.digest.json 2>&1; echo "digest: $(cut -c1-260 $F.digest.json)"
  $V verify --system $F/system.bin --statement $F/sub_00.stmt --proof $F/sub_00.proof > $F.verify.json 2>&1
  echo "pinned verify: $(python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print(d['accepted'],d['system_pinned'],d['reason'][:80])" $F.verify.json 2>&1)"
  echo "=== $(date -u +%H:%M:%SZ) gate $rl --vus $vus --batch 4096"
  t0=$(date +%s)
  $PY -u -m backends.direct.ligero.run --relation $rl gate-vu --vus $vus --batch 4096 --zk --mode interactive --auth included-hash \
      --target -128 --device cuda --instance-procs 16 --out $RD/gates/$rel-$leaf.json > $RD/gates/$rel-$leaf.log 2>&1
  echo "gate rc=$? wall=$(( $(date +%s) - t0 ))s"; tail -n 2 $RD/gates/$rel-$leaf.log | cut -c1-240
done
$PY - "$RD" <<'PY'
import json, sys
from pathlib import Path
rd = Path(sys.argv[1]); out = []
for g in sorted((rd / "gates").glob("*.json")):
    d = json.loads(g.read_text()); name = g.stem
    fx = rd / "fixtures"; dg = fx / f"{name}.digest.json"; vf = fx / f"{name}.verify.json"
    dgj = json.loads(dg.read_text()) if dg.is_file() else {}
    vfj = json.loads(vf.read_text()) if vf.is_file() else {}
    out.append({"system": d.get("relation"), "leaf": d.get("leaf"), "honest_subbatches": len(d.get("positives", [])),
                "honest_accepted": sum(1 for p in d.get("positives", []) if p.get("ok")), "negatives": len(d.get("negatives", [])),
                "negatives_accepted": sum(1 for n in d.get("negatives", []) if n.get("accepted")), "failures": d.get("failures"),
                "rows": (d.get("hash_census") or {}).get("rows_total"), "sys_id": dgj.get("sys_id"), "table_digest": dgj.get("table_digest"),
                "pinned_relation": dgj.get("pinned_relation"), "fixture_rust": {k: vfj.get(k) for k in ("accepted", "system_pinned")}})
(rd / "gates.json").write_text(json.dumps(out, indent=1))
for o in out: print(json.dumps(o))
PY
