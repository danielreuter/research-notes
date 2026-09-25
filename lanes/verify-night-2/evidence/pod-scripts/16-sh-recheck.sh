#!/usr/bin/env bash
# verify-night-2: red-team SH R1/R2 recheck (coordinator 20260925T0745Z). For each B-Ligero included-hash result given:
#   reverify --dry-run (my ligero-verify), 04 statement binding (y words), 06 core roots with the R1/R2 checks (leaf triple ==
#   untiled layout, per-rep disjoint coverage of [0, N), bindings / owner / count / roots recomputed from my tree's set);
#   then, only if all three pass and LABEL=1, a verification-verdict/v1 (11-label.py) whose detail says R1/R2 were checked,
#   labelled verified=accepted --by verify-night-2.
#   TAG=<name> LABEL=0|1 bash 16-sh-recheck.sh ART...
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
I=$RESEARCH_RUN_DIR/inputs; TAG=${TAG:-sh}; O=/workspace/verify-night-2/$TAG; mkdir -p $O
BI=/workspace/bench-instances/v1; FZ=/workspace/src/fixtures/bench-instances/v1
{
echo "=== [$(date -u +%H:%M:%S)] bench-instances/v1 (bf16-ampere's frozen x / W) -> $BI"
[ -f "$BI/vu-k1536.x.u16" ] || $PY -m verity_numerical.bench.instances build --out "$BI" --seeds "$FZ/seeds" --procs 16 2>&1 | tail -2
for f in $BI/*; do [ -e "$FZ/$(basename $f)" ] || ln -s "$f" "$FZ/$(basename $f)"; done
$PY - "$BI" "$FZ" <<'PYEOF'
import json, sys
from pathlib import Path
from verity_numerical.bench.instances import sha256_file
bi, fz = Path(sys.argv[1]), Path(sys.argv[2])
man = json.loads((fz / "manifest.json").read_text())
built = {n: f for t in man["tiers"].values() for n, f in t.get("files", {}).items() if not f.get("committed")}
bad = [n for n, f in built.items() if not (bi / n).is_file() or sha256_file(bi / n) != f["sha256"]]
print(f"built arrays: {len(built)}, sha256 mismatches vs committed manifest: {bad}")
PYEOF
echo "=== [$(date -u +%H:%M:%S)] reverify --dry-run $*"
$PY -m backends.direct.ligero.reverify "$@" --dry-run --verifier /workspace/bin/ligero-verify --jobs 16 --work $O/rv --json > $O/reverify.raw
echo "reverify rc=$?"
echo "=== [$(date -u +%H:%M:%S)] statement binding"
$PY $I/04-stmt-binding.py "$@" > $O/binding.json; echo "binding rc=$?"
echo "=== [$(date -u +%H:%M:%S)] core roots + R1/R2"
$PY $I/06-core-roots.py "$@" > $O/core-roots.json; echo "core-roots rc=$?"
echo "=== [$(date -u +%H:%M:%S)] per-result verdicts (LABEL=${LABEL:-0})"
$PY - $O "${LABEL:-0}" "$I/11-label.py" "$@" <<'PYEOF'
import json, os, subprocess, sys
from pathlib import Path
O, label, lab = Path(sys.argv[1]), sys.argv[2] == "1", sys.argv[3]
arts = sys.argv[4:]
s = (O / "reverify.raw").read_text()
i = min(j for j in (s.find("\n["), s.find("\n{"), 0 if s[:1] in "[{" else -1) if j >= 0)
rv = {r["result"]: r for r in json.loads(s[i:])}
bd = {r["result"]: r for r in json.loads((O / "binding.json").read_text())}
cr = {r["result"]: r for r in json.loads((O / "core-roots.json").read_text())}
summary = []
for a in arts:
    full = next((k for k in rv if k.startswith(a)), a)
    r, b, c = rv.get(full, {}), bd.get(full, {}), cr.get(full, {})
    reps = r.get("reps") or {}
    # red-team SH R4: every rep reverify batch-verified has exactly as many proofs as 06 counted proof-backed stmt entries
    epr = c.get("entries_per_rep") or {}
    r4 = bool(reps) and set(reps) == set(epr) and all(int(reps[k].get("n", -1)) == int(epr[k]) for k in reps)
    ok = r.get("status") == "PASS" and b.get("status") == "BOUND" and c.get("status") == "ROOTS-MATCH" and r4
    vsec = max((x.get("verify_seconds_sum", 0) for x in (r.get("reps") or {}).values()), default=0)
    acc = sum(x.get("accepted", 0) for x in reps.values()); n = sum(x.get("n", 0) for x in reps.values())
    bits = min((x.get("batch_bits", 0) for x in reps.values()), default=0)
    core = c.get("core") or {}
    line = (f"{full[:12]} {r.get('relation')}: reverify {r.get('status')} ({acc}/{n}, 2^-{bits:.2f}, custody {r.get('custody')}); "
            f"binding {b.get('status')} (y_bad {b.get('y_mismatched')}); R1/R2 {c.get('status')} "
            f"(roots a {core.get('a', {}).get('root', '')[:8]} b {core.get('b', {}).get('root', '')[:8]} y {core.get('y', {}).get('root', '')[:8]}; "
            f"{c.get('statements')} stmts, reps {c.get('reps')}, {c.get('vus_covered')} VUs; {c.get('problems') or ''}); "
            f"R4 proof-per-entry {'ok' if r4 else 'FAIL'} (batch n {({k: v.get('n') for k, v in reps.items()})} vs entries {epr})"
            + (f"; beyond frozen: {b['beyond_frozen']}" if b.get("beyond_frozen") else ""))
    print(("PASS " if ok else "FAIL ") + line, flush=True)
    summary.append({"result": full, "ok": ok, "line": line})
    if not (ok and label):
        continue
    ev = O / f"ev-{full[4:16]}.json"
    ev.write_text(json.dumps({"reverify": r, "binding": b, "core_roots_r1r2": c}, indent=1))
    N = int(os.environ.get("VN2_N", 4096))
    detail = (f"verify-night-2, red-team SH R1/R2/R4 checked: {line}. R1 = every statement's (vu_index, x_index, w_index) equals the "
              f"untiled layout (x = W = vu) over its dumped range and each rep's proof-backed sub-batches tile [0, {N}) disjointly "
              f"(R4: a stmt entry without a proof covers nothing; batch n == entries per rep); R2 = the three "
              f"trees' binding (hashauth.binding_digest), owner, count and root recomputed from my tree's instance set (framing and "
              f"trees: verity.commitments core; row digests: {(c.get('info') or {}).get('row_digest_ref')}) equal every statement's. "
              f"Proofs: ligero-verify d89cffc7 (main 00ffe398) on the dumped rep(s), "
              f"interactive transcripts replay the runner's coins (not transferable)." + (f" {os.environ['VN2_NOTE']}" if os.environ.get("VN2_NOTE") else ""))
    p = subprocess.run([sys.executable, lab, full, "--tree", r.get("run_files") or c.get("run_files"), "--verifier",
                        "ligero-verify d89cffc7 (main 00ffe398) + verify-night-2 R1/R2 core recompute (06-core-roots.py)",
                        "--detail", detail, "--seconds", str(vsec), str(ev)], capture_output=True, text=True)
    print("  label:", p.returncode, p.stdout.strip()[-300:], p.stderr.strip()[-300:], flush=True)
(O / "summary.json").write_text(json.dumps(summary, indent=1))
PYEOF
echo "=== [$(date -u +%H:%M:%S)] done"
} 2>&1 | tee $O/run.out
