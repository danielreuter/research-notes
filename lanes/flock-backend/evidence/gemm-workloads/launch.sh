#!/usr/bin/env bash
# flock-backend: C-Flock GEMM cells for the served workloads (one script per GPU type, same flow).
#
#   bash launch.sh l40s [grant]     sm80 BF16 cells on an L40S prover   (#39 K1536, #57/#67 K2048, #60 K4096)
#   bash launch.sh h100 [grant]     sm90 wgmma BF16 cells on an H100    (#73 K4096)
#   "grant" adds the cells whose Chunk(n) is outside red-team-flock's grant (n in {2,4,8,16}; CPU selftests pass):
#   l40s: #57 K9216 Chunk(18), #60 K14336 Chunk(28); h100: #73/#74 K2560 Chunk(5), #73 K9728 Chunk(19).
#
# Run from the repo root on cursor/flock-backend-4983 (clean tree; research on PATH, lane env sourced). It creates the prover
# and a same-datacenter verifier pod (at most one pod per name: pod1.sh compares the pod list before and after a create), then
# per cell: `bench.cell plan` with the real addresses (the input set is sent with both runs), verifier run, prover run, wait,
# `bench.cell register` (verity_flock.register --lane flock-backend, then put with the input set ref). Pods are left for `research pods terminate` once the runs are fetched.
set -uo pipefail
GPU=$1 MODE=${2:-ready}; HERE=$(cd "$(dirname "$0")" && pwd)
case $GPU in
  l40s) DCS="US-MO-1 US-KS-2 EU-RO-1 US-NE-1"; PGPU="NVIDIA L40S"; SM=89; SID=sm80-mma-bf16
        CELLS="k1536:art:dbaacc6f61b0f9f7285e56c09994b273904243d1983058bb37e69c1338420b54:2048:512 1024 2048
k2048:art:69cb815c31b06425e7117ee6e4b43403c8cfb8d28f747f9bde79a18f63a0646e:2048:512 1024 2048
k4096:art:bfed17304406e29217b10fbd944bce13ef8e4f023542b7e005a3bbfe4eccfa4f:1024:512 1024 2048"
        GRANT="k9216:art:c6237f08127239fd9e545e8cc5c6193c9c6a2aa621013dc377ac96b7912d04cb:512:256 512 1024 2048
k14336:art:762f59238f7675e6d6b9a7d953fcea98d201cef83ed78856ac9401c74238738e:512:256 512 1024 2048" ;;
  h100) DCS="US-MO-1 US-KS-2 US-NE-1"; PGPU="NVIDIA H100 80GB HBM3"; SM=90; SID=sm90-wgmma-bf16
        CELLS="k4096:art:cdc7b5ebad6a1da4ce35e811c0ee21d81ab4bbc956a24f399e206496b088509e:2048:512 1024 2048"
        GRANT="k2560:art:01326d5b13004ba3e06cf9177f390848fc9042c4e7386d9a3399e70132dd0098:2048:512 1024 2048
k9728:art:8ab7c2da71562146f36112930fd1b71684da7ad791bf61c5c519ca13a12bf59a:1024:256 512 1024 2048" ;;
  *) echo "usage: launch.sh l40s|h100 [grant]"; exit 2 ;;
esac
[ "$MODE" = grant ] && CELLS="$CELLS
$GRANT"
VGPUS=("NVIDIA RTX 2000 Ada Generation" "NVIDIA RTX A4000" "NVIDIA L4" "NVIDIA RTX A5000" "NVIDIA A40" "NVIDIA L40S")
P=vy-flock-backend-$GPU V=vy-flock-backend-ver$GPU DC=""
for dc in $DCS; do
  out=$(bash "$HERE/pod1.sh" $P $dc "$PGPU" 100 | tail -1); echo "prover $dc: $out"
  case $out in POD*) DC=$dc; break;; esac
done
[ -z "$DC" ] && { echo "no $PGPU stock"; exit 1; }
for g in "${VGPUS[@]}"; do out=$(bash "$HERE/pod1.sh" $V $DC "$g" 40 | tail -1); echo "verifier $g: $out"; case $out in POD*) break;; esac; done
case $out in POD*) ;; *) echo "no same-DC verifier in $DC: terminate $P or retry"; exit 1;; esac
sleep 60
addr() { research pods list 2>/dev/null | awk -v n="$1-" 'index($2, n) == 1' | grep -oE "ip=[0-9.]+|'$2': [0-9]+" | sed -E "s/ip=//; s/'$2': //" | paste -sd:; }
VADDR=$(addr $V 7400) VSSH=$(addr $V 22)
echo "verifier $VADDR (sshd $VSSH)"
state() { research fetch $1 2>&1 | tail -1 | sed -E 's/.*Z: ([a-z]+) .*/\1/'; }
while IFS=: read -r tag _ art per pts; do
  [ -z "$tag" ] && continue
  art="art:$art"
  python -m verity_numerical.bench.cell plan --backend C-interactive --statement "gemm-coordinate/$tag/$SID+frame-v3/blake3-keyed" \
    --input-set $art --prover $P --verifier $V --verifier-addr $VADDR --rtt-target $VSSH --campaign flock-backend --lane flock-backend \
    --points "$pts" --per-proof $per --backend-arg SM=$SM --out .bench-cell/$GPU-$tag.json | tail -1 || continue
  runs=$(python -m verity_numerical.bench.cell launch --cell .bench-cell/$GPU-$tag.json 2>&1 | grep -oE 'r[0-9]{8}-[0-9]{6}-[0-9a-f]{4}' | paste -sd' ')
  set -- $runs; vid=${1:-} pid=${2:-}
  echo "$(date -u +%H:%MZ) $GPU $tag verifier=$vid prover=$pid"
  [ -z "$pid" ] && continue
  while s=$(state $pid); [ "$s" = running ] || [ "$s" = submitted ]; do sleep 60; done
  for i in $(seq 10); do s=$(state $vid); [ "$s" = running ] || [ "$s" = submitted ] || break; sleep 30; done
  research pods ssh $V -- 'pkill -f "[v]erity_flock.bench"; pkill -f "[f]lock-pure-gpu"' >/dev/null 2>&1
  research fetch $pid --all >/dev/null 2>&1; research fetch $vid --all >/dev/null 2>&1
  python -m verity_numerical.bench.cell register --cell .bench-cell/$GPU-$tag.json --prover-run $pid --verifier-run $vid | tail -3
done <<< "$CELLS"
echo "done: terminate $P and $V once the runs are fetched (research pods terminate <id>)"
