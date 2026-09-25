#!/usr/bin/env bash
# verify-night-2 10:25Z batch, /workspace/src = main 3301c435, ligero-verify sha256 596529d2 (rebuilt in 22), coordinator 1017Z order:
# (1) 4090 fp8-ada+blake3 4096 live-verifier cell + x1 GPU-committer cell; (2) the 4096 / 16384 fp8-ada+blake3 cells again at 3301c435;
# (3) fp8-ada-x4+blake3 4096 + 8192 plateau; (4) the fp8-ada-x4 instance-equiv/v1 file (art:f70cf39f, kb/bench-instances.md) --check.
# blake3-80gb's four cells are not here: their run_files have no proofs/ or dumps/, which main's reverify refuses.
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

BL="Producer b-ligero-standard-hash (tree 806a2f73 = its lane + main 94b1c4d2 GPU committer + ligero-steps-pin R1/R2/R4); verified with main 3301c435's verifier + reverify. $FN"
BL0="Producer b-ligero-standard-hash (0905Z handoff, host committer); re-verified with main 3301c435's verifier + reverify (its earlier verdict used ligero-verify d89cffc7, main 00ffe398). $FN"
echo "=== [$(date -u +%H:%M:%S)] (1) 4090 fp8-ada+blake3 4096 live-verifier run (1008Z) + x1 GPU committer"
TAG=4090-b3-live VN2_N=4096 LABEL=1 PV_NOTE="$BL The producer's live verifier (own coins, run_files live/) ran on the prover's pod; this label is the file re-verification of rep 1." bash $I/20-cells.sh \
  art:6a36cde712108a60fe919043996cfdeda11e06a93e583544bd1438b09966742c -- art:e9932b72b71ed81a6d4a94ea62e36bc3f1db521258c9237744c5c31459ca71ee
TAG=4090-b3-x1 VN2_N=4096 LABEL=1 PV_NOTE="$BL" bash $I/20-cells.sh \
  art:08225c8c209777cde883d544ed19b59704b2e9d3e8c60000137b5f2cdbfa1c4a -- art:e7d59ab6a7bad2140c776f1d160efa302f46439ea1ceda9edff68d228a6df022
echo "=== [$(date -u +%H:%M:%S)] (2) 4090 fp8-ada+blake3 4096 / 16384 plateau at 3301c435"
TAG=4090-b3-4096-3301 VN2_N=4096 LABEL=1 PV_NOTE="$BL0" bash $I/20-cells.sh \
  art:3e64461f92030cafa89f8260f83d0260b6c5856fd74c1a49c094fc79ba065310 -- art:5d20ad00f5e7b251987cfc58998199e7c8ee8e35fd935d9a0c9dfb5ad1853a40
TAG=4090-b3-16384-3301 VN2_N=16384 LABEL=1 PV_NOTE="$BL0 n = 16384: $SYN." bash $I/20-cells.sh \
  art:0269046e49e47beda0cf6801812669f0628f8608236a1d5ce3d9234b6f065c77 -- art:d6328cf5ef00648038cb35a171f212ee39a9d5f341c1f049ce4a7eb1671f874e
echo "=== [$(date -u +%H:%M:%S)] (3) 4090 fp8-ada-x4+blake3 4096 / 8192 plateau"
TAG=4090-b3x4-4096 VN2_N=4096 LABEL=1 PV_NOTE="$BL" bash $I/20-cells.sh \
  art:0a95eb1e36bf2003501911d5d7983eb2c39a9356635994007ac60eab78ebc240 -- art:017a706919fd4f694ab7bfa25f63e3123a1fbd2ddd7b0bb0aff800cb447c2ae4
TAG=4090-b3x4-8192 VN2_N=8192 LABEL=1 PV_NOTE="$BL n = 8192: $SYN." bash $I/20-cells.sh \
  art:f35d43aa392b154f2af73bc41920ce1dc17c96b58d9ccd5a608aed9ebf7a453f -- art:6b6d4484c7a3911946431ec8a7d3ef609137274157003e47654313d25be77631

echo "=== [$(date -u +%H:%M:%S)] (4) fp8-ada-x4 instance-equiv/v1 art:f70cf39f"
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
