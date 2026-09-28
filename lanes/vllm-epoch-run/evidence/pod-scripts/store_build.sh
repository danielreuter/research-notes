#!/bin/bash
# store_build.sh ROWDIR: the row's Build and its records as two fixture/v1 trees, `research data put --preserve`, with this run's own
# custody key (research run --custody-r2 stages it under requests/<run id>/custody/; the pod holds no other credential).
#   build    the row dir without match/, commit/ and vu-export/: Programs, workload Program, manifest, summaries, logs (files <= 8 GB)
#   records  match/ and commit/ files under 200 MB, and the row's verdict / stage / log files
# Staged as hardlinks under /workspace/epoch/stage/<run id>/; what is left out is listed in evidence/store_omitted.txt.
# Prints `STORED <build|records> art:<id> <PRESERVED|FAILED>` per tree; exit 0 only when both are PRESERVED.
set -u
D=${1:?row dir}; ROWID=$(basename "$D")
EV=$RESEARCH_RUN_DIR/evidence
C=/workspace/research/requests/${RESEARCH_RUN_ID:?}/custody
[ -f "$C/cred.json" ] || { echo "no custody key at $C"; exit 4; }
export RESEARCH_STORE_CONFIG=$C/store.toml
eval "$(python3 -c "import json,shlex;d=json.load(open('$C/cred.json'));print(' '.join(f'export {k}={shlex.quote(d[k])}' for k in ('AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY','AWS_SESSION_TOKEN') if d.get(k)))")"
S=/workspace/epoch/stage/$RESEARCH_RUN_ID; rm -rf "$S"; mkdir -p "$S/build" "$S/records"

cp -al "$D/." "$S/build/"
rm -rf "$S/build/match" "$S/build/commit" "$S/build/vu-export"
: > "$EV/store_omitted.txt"
find "$S/build" -type f -size +8G -printf "build %s %P\n" -delete >> "$EV/store_omitted.txt"
(cd "$D" && find match commit -type f -size -200M -print0 2>/dev/null | xargs -0 -r cp -al --parents -t "$S/records/")
(cd "$D" && find match commit -type f -size +200M -printf "records %s %p\n" 2>/dev/null >> "$EV/store_omitted.txt")
for f in verdict.json stages.txt row.log timeline.jsonl commit.log build_summary.json target_family.json admission.json; do
  [ -f "$D/$f" ] && cp -al "$D/$f" "$S/records/"
done

meta() {  # meta KIND ROLE -> the tree's meta (serving-view's record-build layout), from the Build's own summaries
  /workspace/venv312/bin/python - "$D" "$1" "$2" <<'EOF'
import glob, json, os, sys
d, kind, role = sys.argv[1:]
def doc(p):
    try:
        return json.load(open(p))
    except Exception:
        return {}
progs, wds = {}, {}
for bs in [f"{d}/build_summary.json", *sorted(glob.glob(f"{d}/build/rank*/build_summary.json"))]:
    s = doc(bs)
    r = "0" if os.path.dirname(bs) == d else os.path.basename(os.path.dirname(bs)).removeprefix("rank")
    for k, v in s.items():
        if isinstance(v, dict) and v.get("program_digest") and (k in ("request", "step") or k.startswith("build_request")):
            progs[f"rank{r}/{k}"] = v["program_digest"]
    wd = (s.get("workload") or {}).get("workload_digest")
    if wd:
        wds[f"rank{r}"] = wd
m, v = doc(f"{d}/manifest.json"), doc(f"{d}/verdict.json")
row = os.path.basename(d)
print(json.dumps({"name": f"epoch-{kind}/{row}", "role": role, "row": int(os.environ["ROWNUM"]), "row_id": row,
                  "epoch": "vllm-rebaseline-epoch-2026-09-28", "program_digests": progs, "workload_digests": wds,
                  "manifest_digest": m.get("manifest_digest"), "query_id": (m.get("query") or {}).get("query_id"),
                  "verdict": v.get("outcome"),
                  "build": {"gpu": os.environ.get("GPU_NAME"), "machine": os.environ.get("POD"), "run": os.environ["RESEARCH_RUN_ID"],
                            "source": os.environ["EPOCH_SHA"], "stage": kind}}))
EOF
}

rc=0
for kind in build records; do
  role=programs; [ "$kind" = records ] && role=records
  meta "$kind" "$role" > "$EV/meta-$kind.json"
  echo "=== $(date -u +%H:%M:%SZ) put $kind $(du -sh "$S/$kind" | cut -f1) $(find "$S/$kind" -type f | wc -l) files"
  ok=0
  for i in 1 2 3; do
    python3 -m research data put --kind fixture/v1 --tree "$S/$kind" --meta @"$EV/meta-$kind.json" --preserve --json \
      > "$EV/put-$kind.json" 2> "$EV/put-$kind.err" && { ok=1; break; }
    tail -n 3 "$EV/put-$kind.err"; sleep $((20 * i))
  done
  art=$(grep -o 'art:[0-9a-f]\{64\}' "$EV/put-$kind.json" | head -n 1)
  if [ "$ok" = 1 ] && [ -n "$art" ]; then echo "STORED $kind $art PRESERVED"; else echo "STORED $kind ${art:-none} FAILED"; rc=1; fi
done
rm -rf "$S"
exit $rc
