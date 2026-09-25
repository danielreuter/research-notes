#!/usr/bin/env bash
# verify-night-3: G3 for the route (a) live-coin cell (PR #36 @ dec08973). Runs in the shipped source (--cwd source).
# 1. build flock-link + verity-gkr-verify from this tree (the producer's 20-verifier-setup.sh, shipped as an input);
# 2. fetch from the store (this run's minted key): the prover run record (cells, statements, digests), the verifier run record
#    (session records), the producer's gate_battery.py (gate run record);
# 3. re-run the gate battery (tools/cell_gate.py with --rust and --flock = the offline Flock replay) at 4096 and 1024.
set -uxo pipefail
SRC=$(pwd); I=$RESEARCH_RUN_DIR/inputs; O=$RESEARCH_RUN_DIR/out; mkdir -p $O
bash $I/20-verifier-setup.sh > $O/build.log 2>&1; tail -n 25 $O/build.log
cp $RESEARCH_RUN_DIR/out/binaries.sha256 $O/binaries.sha256 2>/dev/null; sha256sum /workspace/bin/* | tee $O/binaries-mine.sha256
RID=$(basename $RESEARCH_RUN_DIR); C=/workspace/research/requests/$RID/custody
export RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=$C/store.toml
eval "$(python3 - "$C/cred.json" <<'EOF'
import json, shlex, sys
d = json.load(open(sys.argv[1]))
for k in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"):
    print(f"export {k}={shlex.quote(d[k])}")
EOF
)"
R() { PYTHONPATH=$SRC/tools/research/src python3 -m research "$@"; }
D=/workspace/g3; mkdir -p $D
R data fetch art:d9666f5a230ca55ea1ed2a181a6357f0c3b79e8fbca7f6291aecb0456e98d998 --to $D/prover --path 'out/cell-*' --path 'out/statement*' --path 'out/binaries.sha256' | tail -1
R data fetch art:42841b22664e62484ea6aea459d6faac4a037d20fd273cb42604e49de2b8732a --to $D/verifier --path 'out/sessions-*' | tail -1
R data fetch art:a421f3115706aa4cd905a9cc632fd02652c57594fb4d2b6484c4f6f3c6cd9e90 --to $D/gate --path 'inputs/gate_battery.py' | tail -1
find $D -maxdepth 3 | head -60
cd $SRC/backends/gkr
TH=$(nproc)
for v in 4096 1024; do
  P=$D/prover/out; CD=$D/cells/c$v; mkdir -p $D/cells; rm -rf $CD; cp -r $P/cell-$v $CD
  [ -f $CD/statement/public.bin ] || cp $P/statement-$v/public.bin $CD/statement/ 2>/dev/null || cp $P/statements/public-$v.bin $CD/statement/public.bin 2>/dev/null
  ls $CD/statement
  CJ=$P/statements/cell-$v.json; PC=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['prime_commitment'])" $CJ)
  echo "vus $v prime_commitment $PC digests $(sha256sum $P/statements/leaf_digests-$v.bin)"
  python3 $D/gate/inputs/gate_battery.py --sessions $D/verifier/out/sessions-$v --cells $CD --statement $CD/statement \
      --digests $P/statements/leaf_digests-$v.bin --prime-commitment $PC --vus $v --rust /workspace/bin/verity-gkr-verify-live \
      --flock /workspace/bin/flock-link-live --threads $TH --producer route-a-live --out $O/gate-$v 2>&1 | tail -n 25 | cut -c1-400
  echo "battery-$v rc=${PIPESTATUS[0]}"
done
true
