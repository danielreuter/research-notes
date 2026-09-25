#!/bin/zsh
# Poll for a 2x L40S pod whose driver supports CUDA >= 12.9 (torch cu129); register it as vyv-rf-a5-tp2d.
for i in $(seq 1 80); do
  for cloud in SECURE COMMUNITY; do
    out=$(sh /tmp/a5-research-cuda.sh --name vyv-rf-a5-tp2d --gpu "NVIDIA L40S" --gpu-count 2 --cloud $cloud --disk 300 --register --project verity --guard 90 2>&1)
    if echo "$out" | rg -q REGISTERED; then echo "$(date -u +%H:%M:%S) OK try $i $cloud"; echo "$out" | tail -3; exit 0; fi
  done
  echo "$(date -u +%H:%M:%S) try $i: none"
  sleep 30
done
exit 2
