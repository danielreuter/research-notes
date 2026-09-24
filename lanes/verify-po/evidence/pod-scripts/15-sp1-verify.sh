#!/usr/bin/env bash
# verify-po: independent verification of the sp1-128 SP1 sec134 result (handoff 20260924T2220Z), after 14-sp1-build.sh.
#   TREE=art:<run-files> TAG=<name> bash 15-sp1-verify.sh
# The statement is written HERE from MY tree's frozen bf16-ampere set (committed vu-k1536 y words + the manifest's sha256), as
# verify-night 09-sp1-verify.sh; the dump's statement.bin is only compared with it.
# Accept a rep only if its JSON has ok, statement_match, verdict true and unsound false (the stock host exits 0 on rejection).
# Negatives: last y byte flipped (sec134 host), and the STOCK host (124 queries) on rep0 (must reject).
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
H=/workspace/bin/veritor-zk-host-relation-bare-sec134-cpu; HS=/workspace/bin/veritor-zk-host-relation-bare-stock-cpu
O=/workspace/verify-po/sp1-$TAG; mkdir -p $O
{
echo "=== [$(date -u +%H:%M:%S)] fetch $TREE"
[ -d $O/tree ] || $PY -m research data fetch $TREE --to $O/tree --path 'proofs/*' --path 'variant.json' --path 'sec128-checks.json' | tail -1
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
echo "=== hosts"
sha256sum $H $HS
for h in $H $HS; do SP1_PROVER=cpu RUST_LOG=error $h info 2>/dev/null | grep '^{' | tail -1; done
echo "=== verify (sec134 host)"
for f in $P/proof-rep*.bin; do
  echo "--- $(basename $f)"
  t0=$(date +%s.%N)
  SP1_PROVER=cpu RUST_LOG=error $H verify --proof $f --statement $O/statement.mine.bin 2>$O/$(basename $f).err | grep '^{' | tail -1
  echo "rc=${PIPESTATUS[0]} wall $($PY -c "print(round($(date +%s.%N) - $t0, 2))") s"
done
echo "--- negative: last y byte flipped, rep0, sec134 host"
SP1_PROVER=cpu RUST_LOG=error $H verify --proof $P/proof-rep0.bin --statement $O/statement.neg.bin 2>/dev/null | grep '^{' | tail -1
echo "--- negative: STOCK host (124 queries), rep0"
SP1_PROVER=cpu RUST_LOG=error $HS verify --proof $P/proof-rep0.bin --statement $O/statement.mine.bin 2>$O/stock.err | grep '^{' | tail -1
tail -2 $O/stock.err
echo "=== [$(date -u +%H:%M:%S)] done"
} 2>&1 | tee $O/verify.out
