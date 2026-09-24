set -uo pipefail
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:/usr/local/cuda/bin:$PATH"
SRC=/workspace/wt_merge; cd $SRC
PY=/workspace/venv312/bin/python
export PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC"
for rel in fp8-ada bf16-hopper; do
  echo "=== [$(date -u +%H:%M:%S)] $rel tile64x64 committed, merged tree + hook, ZK interactive, 4096 VUs, 3 reps"
  "$PY" -m backends.direct.ligero.run --relation $rel bench-vu --batch 16384 --total-vus 4096 --reps 3 --zk --mode interactive \
     --auth included-hash --tile 64x64 --pipeline 1 --target -128 --device cuda --instance-procs 16 \
     --instances-cache /workspace/instances-cache --out /workspace/merge3_tile_$rel.json > /workspace/merge3_tile_$rel.log 2>&1
  echo "exit $?"; tail -4 /workspace/merge3_tile_$rel.log | cut -c1-300
done
echo "=== [$(date -u +%H:%M:%S)] done"
