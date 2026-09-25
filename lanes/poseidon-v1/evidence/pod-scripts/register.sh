#!/usr/bin/env bash
# poseidon-v1 (pod): register + preserve every point of a sweep: a run-files/v1 tree (result.json, log, run_id, meta.txt,
# commit-evidence.json, proofs.sha256, proofs/ with system.bin, rep1/, rust_digest.json, rust_batch.json; non-plateau points
# SLIM: no rep-1 .proof files, every dumped file's sha256 in proofs.sha256) and a bench-result/v1 whose meta is result.json plus
#   lane / tag / label / pod / committer,
#   protocol {warm, runs, commit_runs, contended, contention}   (bench-vu's untimed warm-up sub-batch + full pipelined pass),
#   sweep {id, axis, point, plateau, rule, points[...]}          (views._protocol reads meta.protocol / meta.sweep),
# ref run_files=<tree>, both --preserve.     bash register.sh SWEEP_ID POD_DESC COMMITTER
# Credential: $PV/r2.env (mode 600) = `research data mint-credential --env` piped in over ssh, deleted after use.
set -uo pipefail
PV=/workspace/poseidon-v1; source /workspace/env.sh
sid=$1 pod=$2 committer=$3
J=$PV/sweeps/$sid.jsonl
set -a; . $PV/r2.env; set +a
C=$PV/store.pod.toml
cat > "$C" <<'EOT'
[remote]
type = "s3"
bucket = "verity-dev"
endpoint = "https://1d4dfa0a7dc0639e19f5d0125f14a634.r2.cloudflarestorage.com"
region = "auto"
access_key_id_env = "AWS_ACCESS_KEY_ID"
secret_access_key_env = "AWS_SECRET_ACCESS_KEY"
session_token_env = "AWS_SESSION_TOKEN"
EOT
export RESEARCH_STORE=/workspace/research-store RESEARCH_STORE_CONFIG="$C"
plateau=$($PY -c "
import json,sys
pts=[json.loads(l) for l in open('$J') if l.strip()]
ok=[p for p in pts if not p.get('failed') and p.get('P')]
print(max(ok,key=lambda p:p['P'])['tag'])")
for tag in $($PY -c "import json;[print(json.loads(l)['tag']) for l in open('$J') if l.strip() and not json.loads(l).get('failed')]"); do
  d=$PV/runs/$tag
  [ -f $d/result.json ] || { echo "$tag: no result.json"; continue; }
  ( cd $d && find proofs -type f | sort | xargs sha256sum > proofs.sha256 )
  src=$d
  if [ "$tag" != "$plateau" ] && [ "$tag" != "$sid-n4096" ]; then
    s=$PV/slim/$tag; rm -rf $s; mkdir -p $s
    cp -a $d/result.json $d/log $d/run_id $d/meta.txt $d/commit-evidence.json $d/proofs.sha256 $d/proofs $s/
    rm -f $s/proofs/rep1/*.proof
    src=$s
  fi
  $PY - "$d/result.json" "$tag" "$pod" "$committer" "$J" "$plateau" > $PV/meta-$tag.json <<'PY'
import json, os, sys
res, tag, pod, committer, jpath, plateau = sys.argv[1:7]
r = json.load(open(res))
pts = [json.loads(l) for l in open(jpath) if l.strip()]
me = next(p for p in pts if p.get("tag") == tag)
cont = r.get("contention") or {}
kv = dict(t.split("=", 1) for t in open(res.rsplit("/", 1)[0] + "/meta.txt").readline().split() if "=" in t)
malloc = {k: kv.get(k, "unset") for k in ("MALLOC_MMAP_MAX_", "MALLOC_TRIM_THRESHOLD_")}
m = {x["name"]: x["value"] for x in r["measurements"]}
sid = tag.rsplit("-n", 1)[0]
r.update(lane="poseidon-v1", tag=tag, pod=pod, committer=committer,
         label=f"poseidon-v1 {tag} (B-Ligero + in-proof hash, Poseidon2 per row, no sharing; TABLES.md protocol sweep point)",
         protocol={"warm": True,
                   "warm_rule": "bench-vu: an untimed warm-up sub-batch, then one full untimed pipelined pass (every slot meets "
                                "every layout: graph captures, allocator growth) before the timed reps; the first of the 1 + N "
                                "commitment builds is cold (commit.cold_seconds) and never enters commit.seconds",
                   "runs": me.get("reps"), "commit_runs": m.get("commit.reps"),
                   "contended": cont.get("contended"), "contention": cont, "malloc_env": malloc,
                   "statistic": "t.total and the t.* buckets are the median rep's (phases.median_rep); commit.seconds is the "
                                "median of the N warm commitment builds; e2e.seconds = commit.seconds + t.total; P = B / e2e.seconds"},
         sweep={"id": sid, "axis": "total_vus (B), doubled from 1024 at fixed per-proof settings", "point": me["n"],
                "plateau": tag == plateau, "plateau_point": next(p["n"] for p in pts if p.get("tag") == plateau),
                "rule": "kb/TABLES.md Sweep: doubled until two successive doublings together raise the median P by < 2 % "
                        "(P(n) < 1.02 P(n/4)) or memory runs out; plateau = the point with the highest median P"
                        + os.environ.get("RULE_EXTRA", ""),
                "points": [{k: p.get(k) for k in ("n", "P", "e2e", "t_total", "commit", "contended", "failed", "why") if k in p}
                           for p in pts]})
print(json.dumps(r))
PY
  tree=$($PY -m research data put --kind run-files/v1 --tree $src --preserve \
    --meta "{\"lane\": \"poseidon-v1\", \"tag\": \"$tag\", \"label\": \"poseidon-v1 $tag\"}" | grep -o 'art:[0-9a-f]*' | tail -1)
  [ -n "$tree" ] || { echo "$tag tree put failed"; continue; }
  res=$($PY -m research data put --kind bench-result/v1 --meta @$PV/meta-$tag.json --ref run_files=$tree --preserve | grep -o 'art:[0-9a-f]*' | tail -1)
  echo "$(date -u +%H:%M:%SZ) $tag plateau=$([ "$tag" = "$plateau" ] && echo yes || echo no) tree=$tree result=${res:-FAILED}" | tee -a $PV/registered.txt
done
# the byte-identity run (main's committer, row.sh step 3): its run-files tree only, slim, as evidence (not a sweep point)
bt=$sid-maincommitter-n4096; d=$PV/runs/$bt
if [ -f $d/result.json ]; then
  ( cd $d && find proofs -type f | sort | xargs sha256sum > proofs.sha256 )
  s=$PV/slim/$bt; rm -rf $s; mkdir -p $s
  cp -a $d/result.json $d/log $d/run_id $d/meta.txt $d/commit-evidence.json $d/proofs.sha256 $d/proofs $s/
  cp -a $PV/sweeps/$sid.byteid $s/ 2>/dev/null; rm -f $s/proofs/rep1/*.proof
  tree=$($PY -m research data put --kind run-files/v1 --tree $s --preserve \
    --meta "{\"lane\": \"poseidon-v1\", \"tag\": \"$bt\", \"label\": \"poseidon-v1 $bt: main's committer (47485b81) at n=4096, byte-identity evidence vs the tip\"}" | grep -o 'art:[0-9a-f]*' | tail -1)
  echo "$(date -u +%H:%M:%SZ) $bt byteid-evidence tree=${tree:-FAILED}" | tee -a $PV/registered.txt
fi
echo REGISTER_DONE $sid
