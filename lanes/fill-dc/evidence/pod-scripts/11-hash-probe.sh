#!/usr/bin/env bash
# fill-dc: which relations compose with --auth included-hash (column 2)? The fused v3 / v3x4 relations do not
# (hashchain._private_operands: "operand pins ... differ from the expected decode triples"). Probe the non-fused derived
# relations (-x4, -v2, -v2x4) with --reps 1, then rounds 1-3 (--reps 5) over the ones that ran (v1 + hash is in the sweep).
#   BASE=fp8-hopper,bf16-hopper (H100) | bf16-ampere (A100);  P_<base>=pipeline depth for that base (default 4)
source /workspace/fill-dc/scripts/lib.sh
while pgrep -f "scripts/(10-h100|20-a100)-sweep.sh" >/dev/null; do sleep 5; done
S=()
for base in ${BASE//,/ }; do
  var=P_${base//-/_}; p=${!var:-4}
  for v in x4:4096 v2:16384 v2x4:4096; do
    rel=$base-${v%%:*}; l=${v##*:}; tag=hp-$rel-p$p
    REPS=1 run $tag $rel $l $p --auth included-hash && S+=("h-${rel#*-}-${base%%-*}p$p:$rel:$l:$p:--auth,included-hash")
  done
done
echo "$(date -u +%H:%M:%S) HASH_PROBE_DONE ${S[*]}" | tee -a $SUM
for r in ${ROUNDS:-1 2 3}; do PREFIX=hash round $r "${S[@]}"; done
echo "$(date -u +%H:%M:%S) HASH_SWEEP_DONE" | tee -a $SUM
