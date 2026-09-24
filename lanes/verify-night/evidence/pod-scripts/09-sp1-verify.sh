#!/usr/bin/env bash
# verify-night: independent verification of an SP1 relation-bare/v2 result (sp1-table handoff 20260924T0632Z).
#   RES=art:<bench-result> TREE=art:<run-files> TAG=<name> bash 09-sp1-verify.sh      (AWS_* read credential in the environment)
# Verifier: /workspace/sp1-target-relation-bare/release/veritor-zk-host built from lane/sp1-table @ b5e1ed5f (07-sp1-build.sh).
# The statement is written HERE from the frozen set in lane/verify-night @ 1b3c7be6 (/workspace/src/fixtures/bench-instances/v1:
# committed y words + the manifest's own sha256), not taken from the dump; the dump's statement.bin is only compared with it.
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
H=${HOST_BIN:-/workspace/sp1-target-relation-bare/release/veritor-zk-host}
O=/workspace/verify-night/sp1-$TAG; rm -rf $O; mkdir -p $O
{
echo "=== [$(date -u +%H:%M:%S)] fetch $TREE"
$PY -m research data fetch $TREE --to $O/tree --path 'proofs/*' | tail -1
P=$(dirname $(find $O/tree -name statement.bin | head -1)); echo "proofs dir: $P"; sha256sum $P/*
echo "=== statement (mine)"
$PY - "$O" <<'PYEOF'
import hashlib, json, struct, sys
from pathlib import Path
from verity_numerical.bench.tables import FROZEN_INSTANCES
o = Path(sys.argv[1]); fz = Path("/workspace/src/fixtures/bench-instances/v1")
man_sha = hashlib.sha256((fz / "manifest.json").read_bytes()).hexdigest()
want = FROZEN_INSTANCES["first-campaign-target/2026-09-21"]
assert man_sha == want["manifest_sha256"], (man_sha, want)
man = json.loads((fz / "manifest.json").read_text())
yrec = man["tiers"]["vu-k1536"]["files"]["vu-k1536.y.u16"]
y = (fz / "vu-k1536.y.u16").read_bytes()
assert hashlib.sha256(y).hexdigest() == yrec["sha256"] and len(y) == 2 * 4096, "y fixture vs manifest"
lo, hi = want["range"]
ident = f"{want['dataset']}|{want['tier']}|{lo}|{hi}|{man_sha}".encode()
st = b"verity/sp1/relation-bare/v2" + struct.pack("<I", 1) + hashlib.sha256(ident).digest() + struct.pack("<II", 1536, 4096) + y
(o / "statement.mine.bin").write_bytes(st)
neg = bytearray(st); neg[-1] ^= 1
(o / "statement.neg.bin").write_bytes(bytes(neg))
print("mine", len(st), hashlib.sha256(st).hexdigest(), "ident", ident.decode())
PYEOF
cmp $P/statement.bin $O/statement.mine.bin && echo "dump statement.bin == mine"
echo "=== verify (host sha256 $(sha256sum $H | cut -c1-16))"
for f in $P/proof-rep*.bin; do
  echo "--- $(basename $f)"
  SP1_PROVER=cpu RUST_LOG=error $H verify --proof $f --statement $O/statement.mine.bin 2>&1 | grep -E '^\{|^wall' | tail -2
done
echo "--- negative (last y byte flipped) on rep0"
SP1_PROVER=cpu RUST_LOG=error $H verify --proof $(ls $P/proof-rep*.bin | head -1) --statement $O/statement.neg.bin 2>/dev/null | grep '^{' | tail -1
echo "=== [$(date -u +%H:%M:%S)] done"
} > $O/verify.out 2>&1
