#!/usr/bin/env bash
# agkr-bound: rebuild the Rust verifier (link.rs) and re-verify the statement dirs 31 left in
# /workspace/agkr-bound/link-rust-$REL (honest x3, honest_nolink x2, every negative once) (cwd backends/gkr).
# research run ... --send 32_rust_only.sh -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/32_rust_only.sh"'
set -uo pipefail
export PATH="/workspace/venv312/bin:$HOME/.cargo/bin:$PATH" MALLOC_MMAP_MAX_=0 MALLOC_TRIM_THRESHOLD_=1000000000000
export CARGO_TARGET_DIR=/workspace/cargo-target
read -r Q PER < /sys/fs/cgroup/cpu.max 2>/dev/null || { Q=max; PER=100000; }
NT=$([ "$Q" = max ] && nproc || echo $(( Q / PER )))
export CARGO_BUILD_JOBS=$NT
echo "commit ${RESEARCH_SOURCE_COMMIT:-?}; threads $NT; MALLOC_MMAP_MAX_=$MALLOC_MMAP_MAX_ MALLOC_TRIM_THRESHOLD_=$MALLOC_TRIM_THRESHOLD_ ($(date -u +%H:%M:%S))"
( cd verifier && cargo build --release 2>&1 | grep -E "^error|-->|Finished" | grep -B1 -A3 "^error\|Finished" | head -40 )
( cd verifier && cargo test --release 2>&1 | grep -E "^test result|FAILED|panicked|^error|link::" )
VB=/workspace/bin/verity-gkr-verify-link2; cp $CARGO_TARGET_DIR/release/verity-gkr-verify $VB && sha256sum $VB
O=/workspace/agkr-bound/link-rust-${REL:-bf16-ampere}
fail=0
for name in honest_nolink honest_nolink honest honest honest bit_flip non_boolean alt_alt_bits sigma_range sigma_plus2 root_b_changed z_differs S_dup_cell S_no_booleanity; do
  d=$O/$name; out=$d/rust2.json; rm -f $out
  t0=$(date +%s.%N)
  $VB verify --dir $d --proof $d/proof.bin --vus 4096 --threads $NT --allow-any-circuit --require-commitment --json $out > /dev/null 2> $d/rust2.err
  rc=$?; t1=$(date +%s.%N)
  want=reject; case $name in honest*) want=accept;; esac
  got=$([ $rc = 0 ] && echo accept || echo reject)
  [ $got = $want ] || fail=1
  python3 - "$name" "$got" "$want" "$out" "$d/rust2.err" "$(echo "$t1 - $t0" | bc)" <<'PY'
import json, os, sys
name, got, want, out, err, wall = sys.argv[1:]
d = json.load(open(out)) if os.path.isfile(out) else {}
e = (d.get("error") or open(err).read().strip()[-140:] or "")[:140]
keys = ("verify_seconds", "t_link", "t_link_derive", "t_rows_linear_test", "t_rows_fill_cpu", "peak_rss_bytes")
print(f"{name:16s} {got:6s} (want {want}) wall {float(wall):.2f} s " + " ".join(f"{k}={d.get(k)}" for k in keys) + (f" err={e}" if got == "reject" else ""), flush=True)
PY
done
echo "RUST-ONLY $([ $fail = 0 ] && echo OK || echo FAILED) ($(date -u +%H:%M:%S))"
exit $fail
