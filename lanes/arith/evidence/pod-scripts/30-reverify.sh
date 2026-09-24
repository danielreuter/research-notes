#!/usr/bin/env bash
# arith: reverify.py on stored results (labels --by arith: a producer check that the proofs verify; Table 2 needs a
# non-producer pass on top).  bash 30-reverify.sh ROUND ART...   (credential: /workspace/arith/.cred, minted on the laptop)
cd /workspace/src && source /workspace/env.sh
set -a; source /workspace/arith/.cred; set +a
O=/workspace/arith; mkdir -p $O/rv
ROUND=$1; shift
$PY -m backends.direct.ligero.reverify "$@" --by arith --verifier /workspace/cargo-target/release/ligero-verify \
  --jobs 6 --work $O/rv > $O/reverify-$ROUND.out 2>&1
echo "reverify $ROUND rc=$?" | tee -a $O/runs.txt
