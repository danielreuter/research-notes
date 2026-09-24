#!/bin/bash
# round 3: integration tree 7c3b157 (main 9d35c4e + lane 07c3039 + 6babe27 encoder) vs main 6babe27's round-2 hashes (seed 11, 6 x 170 VUs, l=4096)
export PATH=/root/.cargo/bin:$PATH
PY=/workspace/venv312/bin/python
INT=$(ls -d /workspace/research/src/7c3b157* | head -1)
echo "tree $INT"
for zk in zk nonzk; do
  flag=""; [ $zk = zk ] && flag="--zk"
  for mode in seq pipe3; do
    pf=""; [ $mode = pipe3 ] && pf="--pipeline 3"
    out=/workspace/bitexact3/$zk/int2-$mode; rm -rf $out; mkdir -p $out
    (cd $INT && PYTHONPATH=packages/verity/src:backends/numerical/python:. $PY /workspace/bitexact_fp4.py --tree $INT $flag --mode interactive --batch 4096 --subs 6 --seed 11 --out $out --hints device $pf 2>&1 | tail -2)
    (cd $out && sha256sum system.bin sub_*) > /workspace/bitexact3/$zk/int2-$mode.sha
    if diff -q /workspace/bitexact2/$zk/main.sha /workspace/bitexact3/$zk/int2-$mode.sha >/dev/null; then echo "IDENTICAL $zk main6babe27 vs int2-$mode: $(wc -l < /workspace/bitexact2/$zk/main.sha) files"; else echo "DIFFER $zk main6babe27 vs int2-$mode: $(diff /workspace/bitexact2/$zk/main.sha /workspace/bitexact3/$zk/int2-$mode.sha | grep -c '^<') files"; fi
  done
done
echo BITEXACT3_DONE
