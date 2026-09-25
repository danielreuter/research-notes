#!/usr/bin/env bash
# red-team-standard-hash-2: fp4-nvf4+poseidon2 R1 / R4 / H2 / ZK at main cd963fd4 + rtsh overlay (/workspace/src), sequential.
set -uo pipefail
S=/workspace/src; B=/workspace/bin/ligero-verify; PY=/workspace/venv312/bin/python
export PYTHONPATH=$S/packages/verity/src:$S/backends/numerical/python:$S/tools/research/src:$S OMP_NUM_THREADS=4 VY_CPU_THREADS=4
O=$PWD/out; mkdir -p $O; cd $S; sha256sum $B; cat .research-source.json | head -4
run() { local tag=$1; shift; $PY -m backends.direct.ligero.redteam.rtsh_fp4_e2e "$@" --bin $B --out $O/$tag > $O/$tag.log 2>&1; echo "$tag rc=$?"; tail -n 6 $O/$tag.log | cut -c1-700; }
run h2-24 steps --steps 24
run h2-48 steps --steps 48
run h2-12 steps --steps 12
run r1 remap --set-binding
run r4 orphan --vus 3
run zk zk
echo E2E-DONE
