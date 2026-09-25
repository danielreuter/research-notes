#!/bin/bash
# red-team-lk (pod): register + preserve the evidence tree of one red-teamed statement (static equivalence, selftest,
# forgeries with statements/rows/proofs/verdicts, harness + scripts).  bash 04_put.sh REV RELATION RESULT_ART WHAT
# Credential: /workspace/red-team-lk/r2.env (mode 600) = `research data mint-credential --env` piped in over ssh.
set -euo pipefail
REV=$1 REL=$2 RES=$3 WHAT=$4
set -a; . /workspace/red-team-lk/r2.env; set +a
C=/workspace/red-team-lk/store.pod.toml
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
TOOL=$(ls -td /workspace/research/tool/*/ | head -1)
export PYTHONPATH=$TOOL RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG="$C"
O=/workspace/red-team-lk/out/$REV; T=/workspace/red-team-lk/evidence/$REV
rm -rf "$T"; mkdir -p "$T/cases"
cp $O/static.json $O/forge/forge.json "$T/"
[ -f $O/selftest.json ] && cp $O/selftest.json "$T/"
[ -d $O-static ] && cp $O-static/static.json "$T/static-merge.json" && cp $O-static/selftest.json "$T/selftest.json"
grep -v -i -E "warn|searchsorted" $O/forge.log > "$T/forge.log" || true
cp -r $O/forge/stmt "$T/stmt"; cp $O/forge/plain/circuit.txt "$T/plain_circuit.txt"
for d in $O/forge/cases/*/; do n=$(basename $d); mkdir -p "$T/cases/$n"; cp $d/public.bin $d/units.bin $d/epilogue.bin $d/proof.bin $d/verify.json "$T/cases/$n/" 2>/dev/null || true; done
mkdir -p "$T/scripts"; cp /workspace/red-team-lk/scripts/*.sh /workspace/red-team-lk/scripts/red_team_lk_v2.py "$T/scripts/"
sha256sum /workspace/red-team-lk/bin/* > "$T/verifiers.sha256"
python3 -m research data put --kind redteam-findings/v1 --tree "$T" --preserve \
  --meta "{\"lane\": \"red-team-lk\", \"relation\": \"$REL\", \"source_commit\": \"$REV\", \"candidate\": \"A-GKR\", \"what\": \"$WHAT\"}" \
  --ref "result=$RES"
