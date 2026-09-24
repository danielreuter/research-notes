#!/bin/bash
# Create cpu3m verifier candidates in several DCs (instant), wait for port maps, probe TCP RTT from the H100b pod, keep the best, terminate the rest.
cd ~/projects/verity-main-wt/post-freeze || exit 1
LOG=/tmp/dh2/probe_cpu_dcs.log; : > $LOG
mk() { uv run -q python -m research.pods.runpod create "$@" 2>&1 | grep -vE 'PUBLIC_KEY'; }
NPOD=0
for dc in "$@"; do
  out=$(mk --name vy-lv2-$dc --cpu cpu3m --vcpu 8 --disk 50 --expose-port 7000 --data-center $dc)
  id=$(echo "$out" | grep -oE '"id": "[a-z0-9]+"' | head -1 | cut -d'"' -f4)
  echo "[$(date -u +%H:%M:%S)] $dc: ${id:-$(echo "$out" | grep -oE 'HTTP [0-9]+.*' | cut -c1-90)}" | tee -a $LOG
  [ -n "$id" ] && NPOD=$((NPOD+1))
done
echo "waiting for port maps..." | tee -a $LOG
for i in $(seq 1 18); do
  sleep 10
  lst=$(uv run -q research pods list 2>&1 | grep vy-lv2-)
  n=$(echo "$lst" | grep -c "'22'")
  [ "$n" -ge "$NPOD" ] && break
done
echo "$lst" | tee -a $LOG
# probe from the H100b
targets=$(echo "$lst" | sed -E "s/.*vy-lv2-([A-Z0-9-]+)-veritor.*ip=([0-9.]+) ports=\{'22': ([0-9]+).*/\1 \2 \3/")
echo "$targets" > /tmp/dh2/lv2_targets.txt
bash /tmp/dh2/sshb.sh 'python3 - <<EOF
import socket, time, sys
targets = """'"$targets"'""".strip().splitlines()
for line in targets:
    dc, h, p = line.split(); p = int(p); ts = []
    for _ in range(4):
        s = socket.socket(); s.settimeout(6); t0 = time.time()
        try: s.connect((h, p)); ts.append(round((time.time()-t0)*1000, 1))
        except Exception as e: ts.append(None)
        finally: s.close()
    good = [t for t in ts if t is not None]
    print(f"RTT {dc} {h}:{p} median={sorted(good)[len(good)//2] if good else None} all={ts}")
EOF' | tee -a $LOG
