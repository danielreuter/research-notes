#!/bin/bash
export PATH=/root/.cargo/bin:$PATH
PY=/workspace/venv312/bin/python
INT=$(ls -d /workspace/research/src/1986953*)
for zk in zk nonzk; do
  flag=""; [ $zk = zk ] && flag="--zk"
  out=/workspace/bitexact2/$zk/int-pipe3; rm -rf $out
  (cd $INT && PYTHONPATH=packages/verity/src:backends/numerical/python:. $PY /workspace/bitexact_fp4.py --tree $INT $flag --mode interactive --batch 4096 --subs 6 --seed 11 --out $out --hints device --pipeline 3 2>&1 | tail -3)
  (cd $out && sha256sum system.bin sub_*) > /workspace/bitexact2/$zk/int-pipe3.sha
  for other in lane int-seq int-pipe3; do
    if diff -q /workspace/bitexact2/$zk/main.sha /workspace/bitexact2/$zk/$other.sha >/dev/null; then echo "IDENTICAL $zk main vs $other: $(wc -l < /workspace/bitexact2/$zk/main.sha) files"; else echo "DIFFER $zk main vs $other: $(diff /workspace/bitexact2/$zk/main.sha /workspace/bitexact2/$zk/$other.sha | grep -c '^<') files"; fi
  done
done
