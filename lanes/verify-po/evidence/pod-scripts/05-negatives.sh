#!/usr/bin/env bash
# verify-po: negatives for a B-Ligero run-files tree, with my ligero-verify. On the first dumped rep of the tree (called rep0
# below; the bench dumps rep1 with --dump-reps 1):
#   base      unmodified rep0                     -> expect batch ACCEPT
#   proofbyte one byte flipped mid-way in proof 0 -> expect REJECT
#   stmtbyte  one byte flipped in the last 64 bytes of statement 0 (the chain-end y words) -> expect REJECT
#   swapstmt  statements of sub-batches 0 and 1 swapped -> expect REJECT
#   bash 05-negatives.sh TREE_ART TAG     (/root/r2.env read credential) -> /workspace/verify-po/neg-TAG/{*.json,summary.txt}
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
T=${1:?tree art}; TAG=${2:?tag}; O=/workspace/verify-po/neg-$TAG; V=/workspace/bin/ligero-verify
rm -rf $O; mkdir -p $O
$PY -m research data fetch $T --to $O/tree > $O/fetch.out 2>&1 || { echo "fetch failed"; cat $O/fetch.out; exit 2; }
P=$(dirname $(find $O/tree -name manifest.json -path '*proofs*' | head -1))
SYS=$($PY -c "import json,sys; m=json.load(open('$P/manifest.json')); print((m.get('system_file') or {}).get('path','system.bin'))")
R0=$(ls -d $P/rep* | head -1); echo "base rep: $R0" > $O/rep0-files.txt; ls $R0 | head -4 >> $O/rep0-files.txt
mk() { rm -rf $P/$1; cp -r $R0 $P/$1; }
mk neg-base
mk neg-proofbyte; f=$(ls $P/neg-proofbyte/*.proof | head -1); $PY - "$f" <<'EOF'
import sys; p=sys.argv[1]; b=bytearray(open(p,'rb').read()); b[len(b)//2]^=0x01; open(p,'wb').write(b); print("flipped", p, len(b)//2)
EOF
mk neg-stmtbyte; f=$(ls $P/neg-stmtbyte/*.stmt | head -1); $PY - "$f" <<'EOF'
import sys; p=sys.argv[1]; b=bytearray(open(p,'rb').read()); i=len(b)-8; b[i]^=0x01; open(p,'wb').write(b); print("flipped", p, i)
EOF
mk neg-swapstmt; S=($(ls $P/neg-swapstmt/*.stmt | head -2)); mv ${S[0]} $P/neg-swapstmt/tmp.x; mv ${S[1]} ${S[0]}; mv $P/neg-swapstmt/tmp.x ${S[1]}; echo "swapped ${S[0]} ${S[1]}"
cd $P
for c in base proofbyte stmtbyte swapstmt; do
  $V batch --system $SYS --dir neg-$c --jobs 16 --threads 1 --target-bits 128 --json $O/$c.json > $O/$c.out 2>&1; rc=$?
  $PY - $O/$c.json $c $rc <<'EOF' | tee -a $O/summary.txt
import json, sys
p, c, rc = sys.argv[1:]
try:
    x = json.load(open(p))
    print(f"{c}: rc={rc} batch_accepted={x.get('batch_accepted')} n={x.get('n')} accepted={x.get('accepted')} rejected={x.get('rejected')} reason={str(x.get('batch_reason'))[:160]}")
except Exception as e:
    print(f"{c}: rc={rc} no JSON ({e})")
EOF
done
rm -rf $O/tree
