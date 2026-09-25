#!/usr/bin/env bash
# red-team-lk follow-up (pod vy-red-team-lk2): static merged-LK check of the H100 FP8 cell art:ad76c106 (run-files art:55eb421d,
# source 3be6a35f / a97576b5: gpu/v2/export.py identical at both).  Our tree = `git archive 3be6a35f backends/gkr/gpu
# backends/gkr/packed backends/numerical/python packages/verity/src` + our harness.  Exports fp8-hopper (model
# hopper_e4m3_wgmma_k32, K 1536) with --no-merge and merged, compares byte-for-byte (sha256) with the previously verified
# statement (art:2e7baba7 / art:b0c27291 run-files art:438ada92 = art:25c57ccb) and the cell's (art:55eb421d), runs static-merge +
# selftest, then registers the evidence.  Outputs /workspace/red-team-lk/out/hopper.
set -uo pipefail
W=/workspace/red-team-lk; T=$W/tree-3be6a35f; O=$W/out/hopper
rm -rf $T $O; mkdir -p $T $O
tar -xzf $W/rtlk-3be6a35f.tgz -C $T
mkdir -p $T/backends/gkr/tools; cp $W/scripts/red_team_lk.py $T/backends/gkr/tools/red_team_lk.py
export PYTHONPATH="$T/backends/gkr:$T/packages/verity/src:$T/backends/numerical/python:$T"
PY=python3
cd $T/backends/gkr
echo "== export $(date -u +%H:%M:%S)"
$PY -m gpu.v2.export circuits --model hopper_e4m3_wgmma_k32 --no-merge --out $O/plain > $O/plain.json 2> $O/plain.err; echo "plain rc=$?"
$PY -m gpu.v2.export circuits --model hopper_e4m3_wgmma_k32 --out $O/merged > $O/merged.json 2> $O/merged.err; echo "merged rc=$?"
tail -3 $O/plain.err $O/merged.err
(cd $O && sha256sum plain/* merged/* > sha256.txt)
$PY - $O > $O/custody.json <<'EOF'
import hashlib, json, sys
from pathlib import Path
o = Path(sys.argv[1])
ref = {
    "old art:2e7baba7/art:b0c27291 (run-files art:438ada92 = art:25c57ccb)": ("plain", {
        "circuit.txt": "424e72560b1ea8c7f2bbc9adc336f55125be93ffadfb5e6bbab7c92ed0738fee",
        "epilogue.txt": "43aa11bb588b625accee2ac975865894d50082bd0e6d3db8df06252bdb160291",
        "chain.txt": "97142fd5818157f31e3e50b6b94a5a8a075b24ac1cb0d2b903bdc0becedd9ae2",
        "manifest.json": "1cf98bcaad84e4f31bfd7bae81b95093a9139da07b454d14f552eeef607eb4df"}),
    "cell art:ad76c106 (run-files art:55eb421d)": ("merged", {
        "circuit.txt": "07d15dc38045e2041be8c3bbcae58ddb47bd23eb487273a463def0badd0166b7",
        "epilogue.txt": "43aa11bb588b625accee2ac975865894d50082bd0e6d3db8df06252bdb160291",
        "chain.txt": "97142fd5818157f31e3e50b6b94a5a8a075b24ac1cb0d2b903bdc0becedd9ae2",
        "manifest.json": "7d363774bebe98906f4017580561f216f40c4cc0467baea3cee0135d876fb130"}),
}
res = {"ok": True, "checks": {}}
for name, (d, files) in ref.items():
    got = {f: hashlib.sha256((o / d / f).read_bytes()).hexdigest() if (o / d / f).is_file() else None for f in files}
    same = {f: got[f] == files[f] for f in files}
    res["checks"][f"{d} export == {name}"] = {"identical": same, "export_sha256": got}
    res["ok"] &= all(same.values())
print(json.dumps(res, indent=1))
EOF
echo "custody ok=$($PY -c "import json;print(json.load(open('$O/custody.json'))['ok'])")"
echo "== static-merge $(date -u +%H:%M:%S)"
$PY tools/red_team_lk.py static-merge --plain $O/plain --merged $O/merged > $O/static.json 2> $O/static.err; echo "static rc=$?"
tail -3 $O/static.err
$PY -c "
import json; d=json.load(open('$O/static.json'))
print({k: d[k] for k in ('ok','problems','queries_per_unit','lk_rows','lk_width','lk_first_column_unique','epilogue.txt_identical','chain.txt_identical','manifest_keys_differing')})
print({n: (t['tag'], t['rows'], t['width'], t['max_key']) for n, t in d['tables'].items()})"
echo "== selftest $(date -u +%H:%M:%S)"
$PY tools/red_team_lk.py selftest --plain $O/plain --merged $O/merged > $O/selftest.json 2> $O/selftest.err; echo "selftest rc=$?"
tail -3 $O/selftest.err
$PY -c "import json; d=json.load(open('$O/selftest.json')); print('selftest ok', d['ok'])"
cp $W/scripts/10_hopper.sh $W/scripts/red_team_lk.py $O/
sha256sum $W/rtlk-3be6a35f.tgz > $O/source-tarball.sha256
if [ -f $W/r2.env ]; then
  echo "== put $(date -u +%H:%M:%S)"
  set -a; . $W/r2.env; set +a
  C=$W/store.pod.toml
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
  OK=$($PY -c "import json;a=json.load(open('$O/custody.json'))['ok'];b=json.load(open('$O/static.json'))['ok'];c=json.load(open('$O/selftest.json'))['ok'];print('PASS' if a and b and c else 'FAIL')")
  cd /tmp && PYTHONPATH=$TOOL RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG="$C" $PY -m research data put --kind redteam-findings/v1 --tree "$O" --preserve \
    --meta "{\"lane\": \"red-team-lk\", \"relation\": \"fp8-hopper\", \"model\": \"hopper_e4m3_wgmma_k32\", \"source_commit\": \"3be6a35f\", \"candidate\": \"A-GKR\", \"verdict\": \"$OK\", \"what\": \"static merged-LK check of the H100 FP8 cell: rewrites-off export == old verified statement, rewrites-on export == cell statement, static-merge + selftest\"}" \
    --ref "result=art:ad76c106" --ref "run_files=art:55eb421d" --ref "prior=art:2e7baba7"
  rm -f $W/r2.env
fi
