#!/usr/bin/env bash
# verify-po: independent verification of the A-GKR RTX 5090 NVFP4 result (agkr-nvf4 handoff 20260924T2200Z).
#   TREE=art:<run-files> TAG=<name> [FP8TREE=art:<an FP8/BF16 A-GKR tree>] [PREV=<commit>] bash 10-agkr-nvf4-verify.sh
# PREV (default 3c769c6d): the producer commit whose `gpu.nvf4.circuit export` regenerates the statement (git archive in
#   /workspace/agkr-$PREV); the verifier is always built from 3c769c6d (the handoff of 23:05Z: verifier diff to ab57df0a empty).
# Verifier: verity-gkr-verify from the PRODUCER'S NAMED SOURCE lane/agkr-nvf4 @ 3c769c6d (git archive in /workspace/agkr-3c769c6d;
#   main's verifier cannot parse the 3-word public statement), diff reviewed (verify-po report), built + tested HERE
#   (target dir /workspace/agkr-target-3c769c6d). Regression: the same binary on FP8TREE's (y16-only) statement must accept.
# Statement: 09-agkr-nvf4-statement.py (circuit files vs 3c769c6d's export; public.bin vs MY tree's frozen NVFP4 set).
# Negatives: mine (public s flip VU 5, t+1 VU 17, f+1 VU 4095, chain.txt without the public line, public line reordered),
#   then `mutate --sample 24` on rep0.
set -uo pipefail
source /workspace/env.sh
set -a; . /root/r2.env; set +a
export PATH=$HOME/.cargo/bin:$PATH CARGO_TARGET_DIR=/workspace/agkr-target-3c769c6d
V=$CARGO_TARGET_DIR/release/verity-gkr-verify
O=/workspace/verify-po/agkr-$TAG; mkdir -p $O
VSRC=/workspace/agkr-3c769c6d/src; PSRC=/workspace/agkr-${PREV:-3c769c6d}/src
{
echo "statement source: $PSRC ($(cat $PSRC/../REV)); verifier source: $VSRC"
diff -r $VSRC/backends/gkr/verifier $PSRC/backends/gkr/verifier && echo "verifier sources identical"
if [ ! -x $V ]; then
  echo "=== [$(date -u +%H:%M:%S)] build + test verity-gkr-verify from $VSRC ($(cat /workspace/agkr-3c769c6d/REV))"
  (cd $VSRC/backends/gkr/verifier && cargo build --release 2>&1 | tail -2 && cargo test --release 2>&1 | grep -E '^test result|FAILED|panicked')
fi
sha256sum $V
echo "=== [$(date -u +%H:%M:%S)] fetch $TREE"
[ -d $O/tree ] || $PY -m research data fetch $TREE --to $O/tree | tail -1
D=$(dirname $(find $O/tree -name public.bin | head -1))/..; D=$(cd $D && pwd); echo "tree: $D"
sha256sum $D/proofs/*.bin $D/statement/*
echo "=== [$(date -u +%H:%M:%S)] regenerate the statement files with the producer's named source"
(cd $PSRC/backends/gkr && PYTHONPATH=$PSRC/backends/gkr:$PSRC/packages/verity/src:$PSRC/backends/numerical/python:$PSRC \
   $PY -m gpu.nvf4.circuit export --out $O/regen > $O/regen.json 2>&1; echo "regen rc=$?"; tail -c 300 $O/regen.json)
echo "=== [$(date -u +%H:%M:%S)] statement check (public.bin vs MY tree's frozen NVFP4 set)"
(cd /workspace/src && $PY $RESEARCH_RUN_DIR/inputs/09-agkr-nvf4-statement.py $D/statement $O/regen > $O/statement-check.json 2>$O/statement-check.err; echo "check rc=$?")
grep -E '"(identical|ok|equals_frozen_stf|rows_mismatched|manifest_keys_differ|instances_digest_main|header)"' -A0 $O/statement-check.json; tail -3 $O/statement-check.err
echo "=== [$(date -u +%H:%M:%S)] verify"
for r in $D/proofs/rep*.bin; do
  b=$(basename $r .bin)
  $V verify --dir $D/statement --proof $r --vus 4096 --threads 15 --json $O/out_$b.json > $O/verify_$b.log 2>&1; rc=$?
  echo "$b rc=$rc $(head -c 400 $O/out_$b.json 2>/dev/null)"
done
if [ -n "${FP8TREE:-}" ]; then
  echo "=== [$(date -u +%H:%M:%S)] regression: this binary on $FP8TREE (y16 statement)"
  F=/workspace/verify-po/agkr-1b4fd4a1/tree; [ -d $F ] || $PY -m research data fetch $FP8TREE --to $F | tail -1
  $V verify --dir $F/statement --proof $F/proofs/rep0.bin --vus 4096 --threads 15 --json $O/regress_fp8.json > $O/regress_fp8.log 2>&1
  echo "fp8 regression rc=$? $(head -c 200 $O/regress_fp8.json)"
fi
echo "=== [$(date -u +%H:%M:%S)] negatives (mine)"
neg() {  # name, python snippet editing $N/public.bin or $N/chain.txt
  local n=$1; local N=$O/neg-$n; rm -rf $N; cp -r $D/statement $N
  $PY -c "$2" $N
  $V verify --dir $N --proof $D/proofs/rep0.bin --vus 4096 --threads 15 > $O/neg-$n.log 2>&1; local rc=$?
  echo "neg $n rc=$rc (non-zero expected): $(grep -o '"error": *"[^"]*"' $O/neg-$n.log | head -1 | cut -c1-160)$(grep -v '^{' $O/neg-$n.log | tail -1 | cut -c1-160)"
}
PUB='import struct,sys; p=sys.argv[1]+"/public.bin"; b=bytearray(open(p,"rb").read())
def ed(vu,col,f):
    o=16+4*(3*vu+col); w=struct.unpack_from("<I",b,o)[0]; struct.pack_into("<I",b,o,f(w)); print(vu,col,w,"->",f(w))
'
neg s_flip "$PUB
ed(5,0,lambda w: w^1); open(p,'wb').write(b)"
neg t_plus "$PUB
ed(17,1,lambda w: w+1); open(p,'wb').write(b)"
neg f_plus "$PUB
ed(4095,2,lambda w: w+1); open(p,'wb').write(b)"
neg no_public_line "import sys; p=sys.argv[1]+'/chain.txt'; t=open(p).read().splitlines(); open(p,'w').write(''.join(l+'\n' for l in t if not l.startswith('public')))"
neg public_reordered "import sys; p=sys.argv[1]+'/chain.txt'; t=open(p).read().splitlines(); open(p,'w').write(''.join((('public t s f') if l.startswith('public') else l)+'\n' for l in t))"
echo "=== [$(date -u +%H:%M:%S)] mutate --sample 24 on rep0"
$V mutate --dir $D/statement --proof $D/proofs/rep0.bin --vus 4096 --threads 15 --sample 24 > $O/mutate.log 2>&1; echo "mutate rc=$?"
tail -3 $O/mutate.log
echo "=== [$(date -u +%H:%M:%S)] done"
} 2>&1 | tee -a $O/verify.out
