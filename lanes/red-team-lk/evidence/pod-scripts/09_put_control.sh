#!/bin/bash
# red-team-lk (pod): register + preserve the tag-stripped control (06_control.sh), its audit (07_audit.sh) and the fp8 isolated
# search (08_iso.sh).  Credential and store config as in 04_put.sh.
set -euo pipefail
set -a; . /workspace/red-team-lk/r2.env; set +a
C=/workspace/red-team-lk/store.pod.toml
TOOL=$(ls -td /workspace/research/tool/*/ | head -1)
export PYTHONPATH=$TOOL RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG="$C"
O=/workspace/red-team-lk/out; T=/workspace/red-team-lk/evidence/control
rm -rf "$T"; mkdir -p "$T"
for REV in 3be6a35f 716ea008; do
  mkdir -p "$T/$REV"
  cp $O/$REV/forge-control/forge.json $O/$REV/audit.json "$T/$REV/"
  cp $O/$REV/forge-control/control_stmt/circuit.txt "$T/$REV/control_circuit.txt"
  grep -v -i -E "warn|searchsorted" $O/$REV/forge-control.log > "$T/$REV/forge-control.log" || true
  for d in $O/$REV/forge-control/cases/*tag.*/; do n=$(basename $d); mkdir -p "$T/$REV/cases/$n"; cp $d/units.bin $d/proof.bin $d/verify.json "$T/$REV/cases/$n/" 2>/dev/null || true; done
done
cp $O/3be6a35f/forge-iso/forge.json "$T/3be6a35f/forge-iso.json"; cp $O/3be6a35f/audit-iso.json "$T/3be6a35f/"
grep -v -i -E "warn|searchsorted" $O/3be6a35f/forge-iso.log > "$T/3be6a35f/forge-iso.log" || true
mkdir -p "$T/scripts"; cp /workspace/red-team-lk/scripts/*.sh /workspace/red-team-lk/scripts/red_team_lk.py "$T/scripts/"
sha256sum /workspace/red-team-lk/bin/* > "$T/verifiers.sha256"
du -sh "$T"
python3 -m research data put --kind redteam-findings/v1 --tree "$T" --preserve \
  --meta '{"lane": "red-team-lk", "candidate": "A-GKR", "what": "tag-stripped LK control + per-forgery LK-miss audit (fp8 3be6a35f, nvf4 716ea008); fp8 isolated range-tag search (none exists at the forged unit)"}' \
  --ref "result=art:49757870" --ref "result_fp8=art:45c5be4a"
