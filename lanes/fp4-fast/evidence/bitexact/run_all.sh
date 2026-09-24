#!/bin/bash
export PATH=/root/.cargo/bin:$PATH
PY=/workspace/venv312/bin/python
for tree in 6babe273535fdb95d6d0e628659caca61076b37c 3dfdb21d39ea700c8cc7c6d639e03e200d0dcc08; do
  for zk in zk nonzk; do
    flag=""; [ $zk = zk ] && flag="--zk"
    out=/workspace/bitexact/$zk/${tree:0:7}
    echo "=== $(date -u +%T) $tree $zk"
    PYTHONPATH=packages/verity/src:backends/numerical/python:. $PY /workspace/bitexact_fp4.py --tree /workspace/research/src/$tree $flag --mode interactive --batch 4096 --subs 3 --seed 7 --out $out --hints device 2>&1 | tail -8
  done
done
for zk in zk nonzk; do echo "== compare $zk"; (cd /workspace/bitexact/$zk/6babe27 && sha256sum system.bin sub_*) > /workspace/bitexact/$zk/main.sha; (cd /workspace/bitexact/$zk/3dfdb21 && sha256sum system.bin sub_*) > /workspace/bitexact/$zk/lane.sha; diff /workspace/bitexact/$zk/main.sha /workspace/bitexact/$zk/lane.sha && echo "IDENTICAL $(wc -l < /workspace/bitexact/$zk/main.sha) files"; done
echo DONE
