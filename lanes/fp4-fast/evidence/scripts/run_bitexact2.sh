#!/bin/bash
# lane fp4-fast bit-exactness round 2: main 6babe27 (sequential) vs lane a440565 (sequential) vs the integration tree
# 1986953 (main 02c3321 + lane pipeline, 6babe27 encoder) sequential and --pipeline 3; l=4096, 6 sub-batches, seed 11.
export PATH=/root/.cargo/bin:$PATH
PY=/workspace/venv312/bin/python
INT=$(ls -d /workspace/research/src/1986953*)
run () { # name tree flags...
  local name=$1 tree=$2; shift 2
  for zk in zk nonzk; do
    flag=""; [ $zk = zk ] && flag="--zk"
    out=/workspace/bitexact2/$zk/$name
    echo "=== $(date -u +%T) $name $zk"
    (cd $tree && PYTHONPATH=packages/verity/src:backends/numerical/python:. $PY /workspace/bitexact_fp4.py --tree $tree $flag --mode interactive --batch 4096 --subs 6 --seed 11 --out $out --hints device "$@" 2>&1 | tail -4)
    (cd $out && sha256sum system.bin sub_*) > /workspace/bitexact2/$zk/$name.sha
  done
}
mkdir -p /workspace/bitexact2/zk /workspace/bitexact2/nonzk
run main /workspace/research/src/6babe273535fdb95d6d0e628659caca61076b37c
run lane /workspace/research/src/a440565d5fcacfa0e7ac1822a026a8d85686b4e0
run int-seq $INT
run int-pipe3 $INT --pipeline 3
for zk in zk nonzk; do for other in lane int-seq int-pipe3; do
  if diff -q /workspace/bitexact2/$zk/main.sha /workspace/bitexact2/$zk/$other.sha >/dev/null; then echo "IDENTICAL $zk main vs $other: $(wc -l < /workspace/bitexact2/$zk/main.sha) files"; else echo "DIFFER $zk main vs $other"; diff /workspace/bitexact2/$zk/main.sha /workspace/bitexact2/$zk/$other.sha | head -6; fi
done; done
echo BITEXACT2_DONE
