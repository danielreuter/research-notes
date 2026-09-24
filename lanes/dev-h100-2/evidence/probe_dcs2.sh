#!/bin/bash
# For each DC: try the H100 SXM (instant failure when no stock); on success try cpu3m there (then cheap GPUs); if no verifier host, terminate the H100.
# Uses the runpod module directly (no ssh wait). Stops at the first DC where BOTH exist -> /tmp/dh2/probe_result.txt "DC h100_id cpu_id".
cd ~/projects/verity-main-wt/post-freeze || exit 1
LOG=/tmp/dh2/probe_dcs2.log
mk() { uv run -q python -m research.pods.runpod create "$@" 2>&1 | grep -vE 'PUBLIC_KEY'; }
for dc in "$@"; do
  echo "[$(date -u +%H:%M:%S)] == $dc: H100" | tee -a $LOG
  out=$(mk --name vy-dev-h100-2b --gpu "NVIDIA H100 80GB HBM3" --disk 60 --data-center $dc)
  echo "$out" | grep -E 'HTTP|"id"|dataCenterId' | tee -a $LOG
  h=$(echo "$out" | grep -oE '"id": "[a-z0-9]+"' | head -1 | cut -d'"' -f4)
  [ -z "$h" ] && continue
  echo "[$(date -u +%H:%M:%S)] == $dc: H100 $h OK; trying cpu3m" | tee -a $LOG
  out=$(mk --name vy-live-verifier-2b --cpu cpu3m --vcpu 8 --disk 50 --expose-port 7000 --data-center $dc)
  echo "$out" | grep -E 'HTTP|"id"|dataCenterId' | tee -a $LOG
  c=$(echo "$out" | grep -oE '"id": "[a-z0-9]+"' | head -1 | cut -d'"' -f4)
  if [ -z "$c" ]; then
    for g in "NVIDIA GeForce RTX 4090" "NVIDIA RTX A4000" "NVIDIA L4" "NVIDIA RTX 4000 Ada Generation" "NVIDIA RTX A5000" "NVIDIA GeForce RTX 3090" "NVIDIA A40" "NVIDIA RTX A6000" "NVIDIA L40S"; do
      out=$(mk --name vy-live-verifier-2b --gpu "$g" --disk 50 --expose-port 7000 --data-center $dc)
      echo "$g: $(echo "$out" | grep -E 'HTTP|"id"' | head -1)" | tee -a $LOG
      c=$(echo "$out" | grep -oE '"id": "[a-z0-9]+"' | head -1 | cut -d'"' -f4)
      [ -n "$c" ] && break
    done
  fi
  if [ -n "$c" ]; then echo "$dc $h $c" > /tmp/dh2/probe_result.txt; echo "[$(date -u +%H:%M:%S)] FOUND $dc h100=$h verifier=$c" | tee -a $LOG; exit 0; fi
  echo "[$(date -u +%H:%M:%S)] == $dc: no verifier host; terminating H100 $h" | tee -a $LOG
  uv run -q python -m research.pods.runpod terminate $h 2>&1 | tail -1 | tee -a $LOG
done
echo "[$(date -u +%H:%M:%S)] NONE" | tee -a $LOG
echo "NONE" > /tmp/dh2/probe_result.txt
exit 1
