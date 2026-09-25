#!/usr/bin/env bash
# x4-sha256-fill (from b-ligero-sha256): pod bootstrap on the synced tree (research pods sync -> /workspace/src), then a host-memory check that
# pod_bootstrap's health check does not make: the first 4090 (nncdmk8s54vnud, 2026-09-25) passed health but copied 220 MB in
# 0.7 s (numpy) / 10 s (out of pinned memory) -- 3.5 s of every proof's opened-column copy and 17 s of every Python verify.
# research run --on vy-b-ligero-sha256 --project verity --cwd /workspace/src --send 00-bootstrap.sh \
#     --env RELS=fp8-hopper-x4 -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/00-bootstrap.sh"'
set -uo pipefail
RELS=${RELS:-fp8-ada-x4} BENCH_INSTANCES=${BENCH_INSTANCES:-0} bash /workspace/src/backends/direct/ligero/pod_bootstrap.sh 2>&1 | tail -40
source /workspace/env.sh
$PY - <<'EOF'
import time, numpy as np, torch
a = np.ones(55_000_000, dtype=np.uint32)
b = a.copy()
t = time.perf_counter(); b = a.copy(); c = time.perf_counter() - t
p = torch.empty(55_000_000, dtype=torch.int32).pin_memory(); p.fill_(1)
q = p.numpy().view(np.uint32).copy()
t = time.perf_counter(); q = p.numpy().view(np.uint32).copy(); pc = time.perf_counter() - t
print(f"host memory: 220 MB numpy copy {c:.3f} s, pinned copy {pc:.3f} s -> {'OK' if max(c, pc) < 0.25 else 'DEGRADED'}")
EOF
