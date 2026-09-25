#!/usr/bin/env bash
# verify-night-2 10:10Z batch, /workspace/src = main 3301c435, ligero-verify sha256 596529d2 (rebuilt in 22):
# (1) blake3-80gb 0935Z A100 bf16-ampere+blake3 4096; (2) blake3-80gb 0844Z H100 bf16-hopper / fp8-hopper +blake3 4096, fp8-hopper
# 32768 plateau; (3) b-ligero-standard-hash 0958Z fp8-ada+blake3 4096, fp8-ada-x4+blake3 4096 + 8192 plateau, and the
# fp8-ada-x4 instance-equiv/v1 file (art:f70cf39f, kb/bench-instances.md) re-derived with --check against the x4 results' ref.
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
export MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000
I=$RESEARCH_RUN_DIR/inputs; W=/workspace/verify-night-2
LV=$(sha256sum /workspace/bin/ligero-verify | cut -c1-8)
export VN2_VDESC="ligero-verify sha256 $LV (main 3301c435)"
echo "verifier: $VN2_VDESC"
FN="file re-verification (runner's coins), not transferable."
SYN="synthetic instances (no frozen tier past 4096): statements bound to my tree's relchain.instances(rel, N), whose first 4096 VUs equal the frozen 4096 set"

echo "=== [$(date -u +%H:%M:%S)] (1) A100 bf16-ampere+blake3 4096"
B3A="Producer blake3-80gb (tree a80ebc31, A100 attempt r20260925-091820-3fd2); verified with main 3301c435's verifier + reverify. $FN"
TAG=a100-b3-4096 VN2_N=4096 LABEL=1 PV_NOTE="$B3A" bash $I/20-cells.sh \
  art:afd8c38473406a9258bea42d365ff8f4e5b9bb5f598ed99a4a1f16af96089d47 -- art:855cc59726e593d9b06fe1cf4cb6a647a63053f4aed3d7e307b4cc746e91c890

echo "=== [$(date -u +%H:%M:%S)] (2a) H100 +blake3 4096 x2"
B3H="Producer blake3-80gb (tree dc2cae87 / 11a1805e, H100; proved before the R1/R2 fix, proofs unchanged); verified with main 3301c435's verifier + reverify. $FN"
TAG=h100-b3-4096 VN2_N=4096 LABEL=1 PV_NOTE="$B3H" bash $I/20-cells.sh \
  art:5b08aeae3b7ca1a19a5836903f23752e8f0dc8e6543c5a1b5ac61d21736a48e2 art:f020c25b29ce4ed293ea18e8a0ac1c8796bdbd5b494f92aff859850c0e7338af -- \
  art:f32eec55395cdf2db8837f4f89f8d41a7fc8f6fcad9fdbd894114939f3467f71 art:3b78cbda8aa24b4d5ee7a328c655e5790def346c8f9106c31d9f833e15469cb4
echo "=== [$(date -u +%H:%M:%S)] (2b) H100 fp8-hopper+blake3 plateau 32768"
TAG=h100-b3-32768 VN2_N=32768 LABEL=1 PV_NOTE="$B3H n = 32768: $SYN." bash $I/20-cells.sh \
  art:c6462d1a57cd6292d529ebf362353cacd41a3519ca3dfb6aab8466517009124e -- art:4d1d6d6e5782eb4e6d4b84265aa8eca0e63f136eb89815eafd4f522ec251b2cf

echo "=== [$(date -u +%H:%M:%S)] (3a) 4090 fp8-ada+blake3 / fp8-ada-x4+blake3 4096"
BL="Producer b-ligero-standard-hash (tree 806a2f73 = its lane + main 94b1c4d2 GPU committer + ligero-steps-pin R1/R2/R4); verified with main 3301c435's verifier + reverify. $FN"
TAG=4090-b3-4096 VN2_N=4096 LABEL=1 PV_NOTE="$BL" bash $I/20-cells.sh \
  art:08225c8c209777cde883d544ed19b59704b2e9d3e8c60000137b5f2cdbfa1c4a art:0a95eb1e36bf2003501911d5d7983eb2c39a9356635994007ac60eab78ebc240 -- \
  art:e7d59ab6a7bad2140c776f1d160efa302f46439ea1ceda9edff68d228a6df022 art:017a706919fd4f694ab7bfa25f63e3123a1fbd2ddd7b0bb0aff800cb447c2ae4
echo "=== [$(date -u +%H:%M:%S)] (3a') 4090 fp8-ada+blake3 4096, live-verifier run (1008Z)"
TAG=4090-b3-live VN2_N=4096 LABEL=1 PV_NOTE="$BL The producer's live verifier (own coins, run_files live/) ran on the prover's pod; this is the file re-verification of rep 1." bash $I/20-cells.sh \
  art:6a36cde712108a60fe919043996cfdeda11e06a93e583544bd1438b09966742c -- art:e9932b72b71ed81a6d4a94ea62e36bc3f1db521258c9237744c5c31459ca71ee
echo "=== [$(date -u +%H:%M:%S)] (3b) 4090 fp8-ada-x4+blake3 plateau 8192"
TAG=4090-b3x4-8192 VN2_N=8192 LABEL=1 PV_NOTE="$BL n = 8192: $SYN." bash $I/20-cells.sh \
  art:f35d43aa392b154f2af73bc41920ce1dc17c96b58d9ccd5a608aed9ebf7a453f -- art:6b6d4484c7a3911946431ec8a7d3ef609137274157003e47654313d25be77631

echo "=== [$(date -u +%H:%M:%S)] (3c) fp8-ada-x4 instance-equiv/v1 art:f70cf39f"
E=$W/equiv; mkdir -p $E
F=$($PY -m research data fetch art:f70cf39fef166b540e60ccc48a55fed4babd55fdfef40179c4bfaf9dff744eef --to $E/f70cf39f 2>/dev/null | tail -1)
[ -d "$F" ] && F=$(find "$F" -name '*.json' | head -1)
echo "file: $F"
$PY - "$F" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
print("schema", d.get("schema"), "equal", d.get("equal"))
for k in ("candidate", "frozen", "target"):
    if isinstance(d.get(k), dict):
        r = d[k].get("ref", d[k])
        print(k, {x: r.get(x) for x in ("relation", "dataset", "tier", "range", "manifest_sha256") if x in r})
EOF
for R in art:017a706919fd4f694ab7bfa25f63e3123a1fbd2ddd7b0bb0aff800cb447c2ae4 art:6b6d4484c7a3911946431ec8a7d3ef609137274157003e47654313d25be77631; do
  $PY -m research data show $R --json | $PY -c "import json,sys; m=json.load(sys.stdin)['manifest']['meta']; i=(m.get('workload_fingerprint') or {}).get('instances'); print('$R'[:12], 'instances', i)"
done
timeout 1800 $PY -m verity_numerical.bench.instance_equiv --check "$F" 2>&1 | tail -8
echo "=== [$(date -u +%H:%M:%S)] 23 done"
