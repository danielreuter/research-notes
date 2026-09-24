#!/bin/bash
# sp1-table (pod): executor-only comparison of host binaries on VUs 0..HI (cycles, gas, opcode mix), CPU executor.
#   HI=4096 EXTRA="--layout indexed" TAG=idx exec_cmp.sh HOST...   (writes exec-HOST[-TAG]-HI.json)
F=/workspace/src/fixtures/bench-instances/v1
M=059103cf9bd55ee83cbd4bb14ae6db2f60db2cb4ddf85cdc22b1cecee6e4eeea
HI=${HI:-4096}
for b in "$@"; do
  out=/workspace/sp1-table/exec-$b${TAG:+-$TAG}-$HI.json
  SP1_PROVER=cpu RUST_LOG=error /workspace/bin/$b bare-execute --instances $F --manifest-sha256 $M --lo 0 --hi $HI --vus-per-read 64 $EXTRA 2>/dev/null \
    | tail -1 > $out
  python3 - "$b" "$HI" "$out" <<'PY'
import json, sys
b, hi, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
d = json.load(open(out))
ex = d.get("execute") or d
tot = ex["total_cycles"]
print(f"{b} {d.get('layout', '')}: verdict={d.get('verdict', ex.get('outcome'))} matches={d.get('matches_expected')} total={tot:,} per_vu={tot/hi:,.0f} "
      f"gas={ex.get('gas'):,} input_bytes={d.get('input_bytes'):,} rows={d.get('rows')} exec_s={ex.get('execute_seconds')}")
ops = sorted(ex.get("opcodes", {}).items(), key=lambda kv: -kv[1])
print("  " + ", ".join(f"{k}:{v/hi:,.0f}" for k, v in ops[:24]))
PY
done
