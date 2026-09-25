#!/usr/bin/env bash
# verify-night-2: independent verification of sp1-committed's frame-v3 cell art:49695f7c (run files art:9e3c06bd; coordinator
# 20260925T0850Z), after 18-sp1c-build.sh.  The statement is written HERE from MY tree's fp8-ada set with the core only
# (verity.commitments: sha256/row/v1 row leaves, u32 y word leaves, v2h bindings, frame-v3 trees); the dump's statement is only
# compared with it.  Then my b54e42ed CPU host verifies proof-rep0 against MY statement (SP1 under the vk, the public digests'
# trees == my roots, the public id / format / K / B == mine).  Negatives: wrong root a / b / y, the dump's tampered proof, one
# proof byte flipped, my statement over [0, 4095) (another id / B), and the producer's `--batch` instance check (+ adopt).
#   LABEL=0|1 bash 19-sp1c-verify.sh
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
I=$RESEARCH_RUN_DIR/inputs; W=/workspace/verify-night-2; O=$W/sp1c; mkdir -p $O
H=/workspace/bin/veritor-zk-host-committed-b54e42ed-cpu
RES=art:49695f7caa4ddf4a8d80760524ead491f1bbb5048c10f69af809d77eac819a89
TREE=art:9e3c06bd9680153b2369a2734292d9428f24a68501e1bb6f506e5078f41e2b92
SET=art:4a6f7602d9962be856131e113d6fe2d2cb92a2701d1a6a7dc699f2e6a7d1a196
{
echo "=== [$(date -u +%H:%M:%S)] fetch $TREE"
[ -d $O/tree ] || $PY -m research data fetch $TREE --to $O/tree | tail -1
find $O/tree -type f | sed "s|$O/tree/||" | sort | head -40
( cd $O/tree && find . -type f -exec sha256sum {} + | sort -k2 ) > $O/tree.sha256
STMT=$(find $O/tree -name '*statement*.json' | head -1); PROOF=$(find $O/tree -name '*proof*rep0*' ! -name '*tamper*' | head -1)
TAMP=$(find $O/tree -name '*tamper*' | head -1)
echo "statement: $STMT"; echo "proof: $PROOF"; echo "tampered: $TAMP"
echo "=== [$(date -u +%H:%M:%S)] my statement (core, my tree's fp8-ada set)"
$PY - "$STMT" "$O" <<'PYEOF'
import hashlib, json, sys
from multiprocessing import Pool
from pathlib import Path
import numpy as np
from verity.commitments import CommitmentDomain, MerkleTree, RangeIndexedDomain, identity_digest
from verity.commitments import rowleaf
from backends.direct.ligero import relchain
from backends.direct.ligero.relations import RELATIONS

TAG = "verity/ligero-b/auth-binding/v2h"; K = 1536; OWNER = {"a": -1, "b": -2, "y": -1}
dump = json.loads(Path(sys.argv[1]).read_text()); O = Path(sys.argv[2])
rel = RELATIONS["fp8-ada"]
N = 4096
data = relchain.instances(rel, N, procs=16)
msha = relchain.instances_digest(rel, N)

def leaf(args):
    words, role = args
    return rowleaf.sha256_row_digest([int(w) for w in words], 8, role)

with Pool(16) as pool:
    dx = pool.map(leaf, [(np.asarray(v[0]).reshape(-1), rowleaf.ROLE_X) for v in data], chunksize=32)
    dw = pool.map(leaf, [(np.asarray(v[1]).reshape(-1), rowleaf.ROLE_W) for v in data], chunksize=32)
y = [int(rel.y_public(int(v[3]))) for v in data]

def stmt(lo, hi):
    inst = {"dataset": rel.instances_dataset, "tier": rel.instances_tier, "manifest_sha256": msha, "lo": lo, "hi": hi}
    ident = f"{inst['dataset']}|{inst['tier']}|{lo}|{hi}|{msha}"
    trees = []
    for n, vals, schema in (("a", dx[lo:hi], rowleaf.SCHEMA_SHA256_ROW), ("b", dw[lo:hi], rowleaf.SCHEMA_SHA256_ROW),
                            ("y", [w.to_bytes(4, "big") for w in y[lo:hi]], "u32")):
        b = bytes.fromhex(identity_digest(TAG, {**{k: inst[k] for k in ("dataset", "tier", "manifest_sha256")}, "lo": lo, "hi": hi,
                                                "K": K, "tree": n, "schema": schema}))
        t = MerkleTree(CommitmentDomain(b, OWNER[n], RangeIndexedDomain(0, len(vals))), dict(enumerate(vals)), lambda _p, s=schema: s)
        trees.append({"name": n, "schema": schema, "binding": b.hex(), "owner": OWNER[n], "count": hi - lo, "root": t.commitment.root.hex()})
    return {"schema": "sp1-committed-statement/v1", "format": "fp8-ada", "K": K, "B": hi - lo, "identity": ident,
            "id": hashlib.sha256(ident.encode()).hexdigest(), "instances": inst, "scheme": "frame-v3",
            "row_schema": rowleaf.SCHEMA_SHA256_ROW, "binding_tag": TAG, "trees": trees}

mine = stmt(0, N)
(O / "statement.mine.json").write_text(json.dumps(mine, indent=1))
(O / "statement.short.json").write_text(json.dumps(stmt(0, N - 1), indent=1))
keys = ("format", "K", "B", "identity", "id", "instances", "scheme", "row_schema", "binding_tag", "trees")
diff = [k for k in keys if dump.get(k) != mine.get(k)]
print("my roots:", {t["name"]: t["root"][:16] for t in mine["trees"]}, "identity:", mine["identity"])
print("dump roots:", {t["name"]: t["root"][:16] for t in dump.get("trees", [])})
print("dump statement == mine on", keys, ":", "YES" if not diff else f"NO, differs on {diff}")
PYEOF
echo "=== host"
sha256sum $H; SP1_PROVER=cpu RUST_LOG=error $H info 2>/dev/null | grep '^{' | tail -1 | tee $O/info.json
VK=$($PY -c "import json;d=json.load(open('$O/info.json'));print(d.get('vk_hash') or d.get('vk') or '')")
echo "vk: $VK"
v() {  # name args...
  local n=$1; shift
  local t0=$(date +%s.%N)
  SP1_PROVER=cpu RUST_LOG=error $H committed-verify --expect-vk "$VK" "$@" 2>$O/$n.err | grep '^{' | tail -1 > $O/$n.json
  local rc=${PIPESTATUS[0]}
  echo "$n: rc=$rc wall=$($PY -c "print(round($(date +%s.%N) - $t0, 2))")s $($PY -c "
import json
try:
    d = json.load(open('$O/$n.json')); print({k: d.get(k) for k in ('ok', 'sp1_ok', 'vk_pinned', 'verdict', 'tree_check', 'instance_roots', 'instance_check', 'verify_seconds')})
except Exception as e:
    print('no JSON', e, open('$O/$n.err').read()[-300:])")" | tee -a $O/verdicts.txt
}
rm -f $O/verdicts.txt
echo "=== [$(date -u +%H:%M:%S)] verify"
v honest --proof $PROOF --statement $O/statement.mine.json
v honest-dumpstmt --proof $PROOF --statement $STMT
for t in a b y; do v wrong-root-$t --proof $PROOF --statement $O/statement.mine.json --wrong-root $t; done
[ -n "$TAMP" ] && v tampered-proof --proof $TAMP --statement $O/statement.mine.json
cp $PROOF $O/proof.flip.bin; $PY - $O/proof.flip.bin <<'EOF'
import sys; p = sys.argv[1]; b = bytearray(open(p, 'rb').read()); i = len(b) * 3 // 4; b[i] ^= 0x01; open(p, 'wb').write(b); print("flipped byte", i, "of", len(b))
EOF
v proof-byte --proof $O/proof.flip.bin --statement $O/statement.mine.json
v other-range --proof $PROOF --statement $O/statement.short.json
echo "=== [$(date -u +%H:%M:%S)] producer's --batch instance check (set $SET)"
[ -f $O/set/fp8-ada.bin ] || { $PY -m research data fetch $SET --to $O/set | tail -1; }
B=$(find $O/set -name '*.bin' | head -1); echo "set file: $B"
[ -n "$B" ] && v batch --proof $PROOF --statement $O/statement.mine.json --batch $B
[ -n "$B" ] && [ -n "$TAMP" ] && v tampered-adopt-batch --proof $TAMP --statement $O/statement.mine.json --adopt-published-roots --batch $B
echo "=== [$(date -u +%H:%M:%S)] gate"
$PY - $O "${LABEL:-0}" $I/11-label.py $RES $TREE <<'PYEOF'
import json, subprocess, sys
from pathlib import Path
O, label, lab, res, tree = Path(sys.argv[1]), sys.argv[2] == "1", sys.argv[3], sys.argv[4], sys.argv[5]
def j(n):
    try:
        return json.loads((O / f"{n}.json").read_text())
    except Exception:
        return None
h = j("honest")
neg = {n: j(n) for n in ("wrong-root-a", "wrong-root-b", "wrong-root-y", "tampered-proof", "proof-byte", "other-range")}
ok = bool(h and h.get("ok") and h.get("sp1_ok") and h.get("vk_pinned") and h.get("tree_check") is None)
negok = {n: (d is None or not d.get("ok")) for n, d in neg.items()}
b = j("batch")
print("honest ok:", ok, "| negatives rejected:", negok, "| producer --batch instance_roots:", b and b.get("instance_roots"))
allok = ok and all(negok.values()) and (b is None or b.get("instance_roots") is True)
print("GATE", "PASS" if allok else "FAIL")
if not (allok and label):
    sys.exit(0 if allok else 1)
ev = O / "sp1c-evidence.json"
ev.write_text(json.dumps({"honest": h, "negatives": neg, "batch": b, "info": json.loads((O / "info.json").read_text())}, indent=1))
detail = (f"verify-night-2: sp1-committed frame-v3 cell (fp8-ada [0, 4096), 4090, 69 shards, 2^-92.9 per proof, algebraic flag; "
          f"below 2^-128 so a drill-down result, not a Table 2 cell). My CPU host built from b54e42ed (guest/common == run source "
          f"cafa9464), vk {h.get('vk_hash')}. The statement is MINE: roots/bindings/id recomputed with verity.commitments core "
          f"(sha256/row/v1 rows, u32 y, v2h bindings) from my tree's fp8-ada set; proof-rep0 verifies against it (SP1 + the public "
          f"digests' trees == my roots + id/format/K/B). Negatives rejected: {sorted(n for n, v in negok.items() if v)}. Producer's "
          f"--batch instance check on set art:4a6f7602: instance_roots {b and b.get('instance_roots')}. Only rep0's proof is in the "
          f"run files (R4: one proof, one statement; reps 1-4 not re-verified).")
p = subprocess.run([sys.executable, lab, res, "--tree", tree, "--verifier", "veritor-zk-host committed-verify (b54e42ed, CPU, my build) + "
                    "verify-night-2 core statement (19-sp1c-verify.sh)", "--detail", detail, "--seconds", str(h.get("verify_seconds")), str(ev),
                    str(O / "verdicts.txt"), str(O / "statement.mine.json")], capture_output=True, text=True)
print("label:", p.returncode, p.stdout.strip()[-400:], p.stderr.strip()[-400:])
PYEOF
echo "=== [$(date -u +%H:%M:%S)] done"
} 2>&1 | tee $O/verify.out
