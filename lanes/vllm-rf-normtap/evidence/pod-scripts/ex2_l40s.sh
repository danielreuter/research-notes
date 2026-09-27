#!/usr/bin/env bash
# ex2_l40s.sh: MUFU.EX2 (`ex2.approx.ftz.f32`) on an L40S (sm_89) against the registered rule over all 2^32 inputs.  mufu_probe.cu `verify`
# (FRAC_MODE 4) of the shipped fix (explicit shift clamp) and of MAIN_SHA (the undefined shift), both against the PINNED tables (fa2_relation's
# xz deltas, rebuilt as MufuTables.load does); the L40S's own measured tables (`table`) against the pinned ones; `probe` of both builds on the
# tiny landmarks.  No bootstrap: the image's nvcc and python3 + numpy.  Evidence under $RESEARCH_RUN_DIR/evidence.
# usage: research run --on <l40s pod> --project verity --source <fix worktree> --cwd source --custody-r2 --env MAIN_SHA=<sha> --send ex2_l40s.sh
#          -- bash -c 'exec bash "$RESEARCH_RUN_DIR/inputs/ex2_l40s.sh"'
set -u
S=$PWD; OUT=$RESEARCH_RUN_DIR; EV=$OUT/evidence; mkdir -p "$EV"; ROOT=/workspace/research; W=/workspace/l40s; T=$W/fix
mkdir -p $W; rm -rf $T
git clone -q --no-checkout $ROOT/git/verity.git $T && git -C $T checkout -q --detach "$RESEARCH_SOURCE_SHA" || { echo "CLONE-FAIL $RESEARCH_SOURCE_SHA"; exit 3; }
d=$(diff -rq -x .git -x __pycache__ -x READY.json $S $T | grep -v "^Only in $S" | wc -l); echo "tree $T @ $(git -C $T rev-parse HEAD) vs shipped: $d differing entries"
[ "$d" = 0 ] || exit 4
K=integrations/vllm/verity_vllm/program/kernels
nvidia-smi --query-gpu=name,driver_version,compute_cap --format=csv,noheader | tee $EV/gpu.txt
nvcc --version | tail -2 | tee $EV/nvcc.txt
cp $T/$K/cuda/mufu_probe.cu $W/probe_fix.cu
git -C $T show "${MAIN_SHA:?}:$K/cuda/mufu_probe.cu" > $W/probe_main.cu
diff $W/probe_main.cu $W/probe_fix.cu > $EV/probe_main_vs_fix.diff; echo "probe main vs fix: $(grep -c '^[<>]' $EV/probe_main_vs_fix.diff) changed lines"
for v in fix main; do nvcc -O2 -arch=sm_89 -DFRAC_MODE=4 -o $W/probe_$v $W/probe_$v.cu > $EV/nvcc_$v.log 2>&1; echo "nvcc $v rc=$?"; done
python3 - $T/$K/tables/W11-40f0cebeb670-20260907T1800Z $W/table_pinned.bin <<'PY' | tee $EV/table_pinned.txt
import hashlib, lzma, sys
import numpy as np
d, out = sys.argv[1:3]
tabs = []
for name in ("ex2", "rcp"):
    raw = open(f"{d}/mufu_{name}_delta_int8.xz", "rb").read()
    delta = np.frombuffer(lzma.decompress(raw), dtype=np.int8)
    t = np.empty(1 << 23, dtype=np.int64)
    t[0] = 0x3F800000
    np.cumsum(delta.astype(np.int64), out=t[1:])
    t[1:] += 0x3F800000
    tabs.append(t.astype("<u4"))
    print(name, "xz", hashlib.sha256(raw).hexdigest(), "u32", hashlib.sha256(tabs[-1].tobytes()).hexdigest())
np.concatenate(tabs).tofile(out)
PY
for v in fix main; do
  $W/probe_$v verify $W/table_pinned.bin > $EV/verify_$v.json 2> $EV/verify_$v.err; echo "verify $v rc=$? $(head -c 160 $EV/verify_$v.json)"
done
$W/probe_fix table $W/table_l40s.bin > $EV/table_l40s.log 2>&1; echo "table rc=$?"
python3 - $W/table_pinned.bin $W/table_l40s.bin <<'PY' | tee $EV/table_compare.txt
import hashlib, sys
import numpy as np
a, b = (np.fromfile(p, dtype="<u4") for p in sys.argv[1:3])
for name, sl in (("ex2", slice(0, 1 << 23)), ("rcp", slice(1 << 23, 2 << 23))):
    print(name, "pinned", hashlib.sha256(a[sl].tobytes()).hexdigest(), "l40s", hashlib.sha256(b[sl].tobytes()).hexdigest(),
          "differing", int(np.count_nonzero(a[sl] != b[sl])))
PY
# 6.5e-22; +-2^-64 (e 63); +-2^-87 (e 40, the first class main's host rule got wrong); e 63 max mantissa; e 39; e 64; +-2^-24; +-2^-23; +-1
LM="$(python3 -c "import struct; print(struct.pack('>f', 6.5e-22).hex())") 1f800000 9f800000 14000000 94000000 1fffffff 9fffffff 13ffffff 20000000 33800000 b3800000 34000000 b4000000 3f800000 bf800000"
for v in fix main; do $W/probe_$v probe $W/table_pinned.bin $LM > $EV/probe_landmarks_$v.txt 2>&1; echo "probe $v rc=$?"; cat $EV/probe_landmarks_$v.txt; done
echo "EX2-L40S-DONE $(date -u +%FT%TZ)"
