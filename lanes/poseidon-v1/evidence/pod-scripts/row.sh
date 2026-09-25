#!/usr/bin/env bash
# poseidon-v1: one Table 2 row on this pod.   bash row.sh ROW REL L P [NMAX]
#  1. /workspace/src-main = /workspace/src (lane tip, b862be30's committer) + rev-to-47485b81.patch (main's committer + the
#     --commit-reps harness), checked file by file against 47485b81-files.sha256
#  2. the plateau sweep on the tip (sweep.sh), commitment timed with the b862be30 committer
#  3. byte identity: main's committer at n = 4096 (REPS 2, CREPS 1): commit-evidence sha256 and rep-1 statement digest must
#     equal the tip's n = 4096 point
set -uo pipefail
SCRIPTS=/workspace/poseidon-v1/scripts; source $SCRIPTS/lib.sh
row=$1 rel=$2 l=$3 p=$4 nmax=${5:-131072}
M=/workspace/src-main
if [ ! -f $M/.poseidon-v1-main-ok ]; then
  rm -rf $M; cp -a /workspace/src $M
  ( cd $M && patch -p1 -s < $SCRIPTS/rev-to-47485b81.patch ) || { echo "patch failed" | tee -a $LOG; exit 2; }
  ( cd $M && sha256sum -c --quiet $SCRIPTS/47485b81-files.sha256 ) || { echo "src-main != 47485b81 on the patched files" | tee -a $LOG; exit 2; }
  echo '{"commit": "47485b8110f7", "note": "lane tip tree + rev-to-47485b81.patch (files checked against 47485b81-files.sha256)"}' > $M/.research-source.json
  touch $M/.poseidon-v1-main-ok
fi
bash $SCRIPTS/sweep.sh $row /workspace/src $rel $l $p $nmax
REPS=2 CREPS=1 run $row-maincommitter-n4096 $M $rel $l $p 4096
a=$($PY $SCRIPTS/line.py $O/$row-n4096 --json); b=$($PY $SCRIPTS/line.py $O/$row-maincommitter-n4096 --json)
$PY - "$a" "$b" <<'EOF' | tee -a $LOG | tee $PV/sweeps/$row.byteid
import json, sys
a, b = json.loads(sys.argv[1]), json.loads(sys.argv[2])
same = a["evidence_sha256"] == b["evidence_sha256"] and a["stmts"] == b["stmts"]
print(f"BYTEID {'IDENTICAL' if same else 'DIFFER'} tip ev={a['evidence_sha256']} stmts={a['stmts']} commit={a['commit']:.4f}s | "
      f"main-committer ev={b['evidence_sha256']} stmts={b['stmts']} commit={b['commit']:.4f}s")
EOF
echo ROW_DONE $row
