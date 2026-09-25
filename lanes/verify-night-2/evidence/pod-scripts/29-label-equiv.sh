#!/usr/bin/env bash
# verify-night-2 11:48Z: label b-ligero-standard-hash's instance-equiv/v1 art:6fdeed7e (x4 4096) from the checks already run on this pod:
# 26 at bfb0b928 (r20260925-114006-0f23: renderer _equiv_content OK vs art:017a7069 and art:050ddede; --check DIFFERS on canonical,
# frozen, lane), 28 (r20260925-114237-c64d: the bfb0b928 regeneration differs only in PR #21's canonical prose and the frozen ref's
# added recipe / seed; arrays, candidate, equal, schema, target identical) and main 767115db's tool (r20260925-114541-4f63: --check
# DIFFERS on lane only, the producer tag the renderer reads).
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
I=$RESEARCH_RUN_DIR/inputs; R=/workspace/research/runs; E=/workspace/verify-night-2/equiv; D=$E/6fdeed7efc48da01
A=art:6fdeed7efc48da01c5c84b0e910c358bab725f01abdf2a79888d47ef25f47bc5
for r in r20260925-114006-0f23 r20260925-114237-c64d r20260925-114541-4f63; do cp $R/$r/stdout.log $D.$r.stdout.txt; done
grep -q "renderer _equiv_content vs art:017a7069: OK" $D.r20260925-114006-0f23.stdout.txt && \
grep -q "renderer _equiv_content vs art:050ddede: OK" $D.r20260925-114006-0f23.stdout.txt && \
grep -q "DIFFERS on lane; equal=True" $D.r20260925-114541-4f63.stdout.txt && \
grep -q "^same: \['arrays', 'candidate', 'equal', 'schema', 'target', 'tool'\]" $D.r20260925-114237-c64d.stdout.txt || { echo "GATE FAIL"; exit 1; }
echo "GATE PASS"
$PY $I/11-label.py $A --tree $A \
  --verifier "verity_numerical.bench.instance_equiv --check at main 767115db (tool as the producer's) and at main bfb0b928 + tables._equiv_content at bfb0b928 (verify-night-2 pod vy-verify-night-2)" \
  --detail "verify-night-2: instance-equiv/v1 fp8-ada-x4 4096 (target fp8-ada-mma-draft/2026-09-22). main 767115db's --check re-derives every field except lane (the producer tag): arrays x d64fec05ec1f / W f7cb2046f2fd / y 27cdcef18aa6 frozen == candidate, equal=True. At bfb0b928 (PR #21) the regenerated doc differs only in the canonical prose and the frozen ref's added recipe / seed; the renderer's tables._equiv_content returns [] against art:017a7069 and art:050ddede (candidate == their workload_fingerprint.instances field for field)." \
  --seconds 20 $D/meta-doc.json $D.refs.txt $D.check.txt $D.r20260925-114006-0f23.stdout.txt $D.r20260925-114237-c64d.stdout.txt $D.r20260925-114541-4f63.stdout.txt 2>&1 | tail -3
$PY -m research data preserved $A >/dev/null 2>&1; echo "result preserved rc=$?"
