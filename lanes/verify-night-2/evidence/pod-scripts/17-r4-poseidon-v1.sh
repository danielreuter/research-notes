#!/usr/bin/env bash
# verify-night-2: (A) red-team SH R4 negative: 06 on the red team's stmt-entry dumps (art:c7683eb2) must refuse the
# proof-less entries; (B) R4 recheck of the 10 results cleared earlier (16, LABEL=0); (C) poseidon-v1's 4 results
# (0800Z 4090 FP8, 0835Z A100 BF16; n = 4096 and 32768): 05 negatives on each full tree, then 16 with LABEL=${PV_LABEL:-0}.
#   PHASES="A B C4 C32" bash 17-r4-poseidon-v1.sh
set -uo pipefail
cd /workspace/src && source /workspace/env.sh
set -a; . /root/r2.env; set +a
I=$RESEARCH_RUN_DIR/inputs; W=/workspace/verify-night-2; PHASES=${PHASES:-A B C4 C32}
has() { [[ " $PHASES " == *" $1 "* ]]; }
if has A; then
  echo "=== [$(date -u +%H:%M:%S)] A: R4 negative on art:c7683eb2"
  rm -rf $W/r4neg; $PY -m research data fetch art:c7683eb24c6af461e5c7a57c6b251318d38555d0a4a88a4dce51338b8f60b393 --to $W/r4neg > $W/r4neg.fetch 2>&1 || cat $W/r4neg.fetch
  for m in $(find $W/r4neg -name manifest.json | sort); do
    d=$(dirname $m); n=$($PY -c "import json;m=json.load(open('$m'));print(max(f['vus'][1] for f in m['files'] if f.get('stmt')))")
    echo "--- ${d#$W/r4neg/} (N=$n; proofs $(find $(dirname $m) -name '*.proof' | wc -l), stmts $(find $(dirname $m) -name '*.stmt' | wc -l))"
    VN2_N=$n $PY $I/06-core-roots.py "dir:$d" 2>&1 >/dev/null | grep '^#'
    (cd $d && /workspace/bin/ligero-verify batch --system system.bin --dir rep0 --jobs 4 --threads 1 --target-bits 128 --json $W/r4neg-batch.json >/dev/null 2>&1
     $PY -c "import json;x=json.load(open('$W/r4neg-batch.json'));print('  my batch: n',x.get('n'),'accepted',x.get('accepted'),'batch_accepted',x.get('batch_accepted'))")
  done
fi
if has B; then
  echo "=== [$(date -u +%H:%M:%S)] B: R4 recheck of the 10 cleared results"
  TAG=r4-recheck LABEL=0 bash $I/16-sh-recheck.sh $(cat $I/cleared.txt) | grep -E '^(PASS|FAIL|===|reverify|binding|core)'
fi
pv() {  # tag N tree... -- arts...
  local tag=$1 n=$2; shift 2; local trees=(); while [ "$1" != "--" ]; do trees+=("$1"); shift; done; shift
  for t in "${trees[@]}"; do
    echo "=== [$(date -u +%H:%M:%S)] negatives $t"; bash $I/05-negatives.sh $t $tag-${t:4:8}; cat $W/neg-$tag-${t:4:8}/summary.txt
  done
  local negok=1
  for t in "${trees[@]}"; do
    s=$W/neg-$tag-${t:4:8}/summary.txt
    grep -q '^base: .*batch_accepted=True' $s && [ $(grep -cE '^(proofbyte|stmtbyte|swapstmt): .*batch_accepted=False' $s) = 3 ] || negok=0
  done
  echo "negatives ok=$negok"
  local lab=${PV_LABEL:-0}; [ $negok = 1 ] || lab=0
  TAG=$tag LABEL=$lab VN2_N=$n VN2_NOTE="${PV_NOTE:-}" bash $I/16-sh-recheck.sh "$@" | grep -vE '^\s*$'
}
has C4 && PV_NOTE="Producer poseidon-v1 (tree lane/poseidon-v1 54ad119d = main + hash-commit harness 6e1cc576 + committer b862be30, prover-side only; verified here with main's verifier). Negatives (05, my verifier): proof byte, chain-end stmt byte, swapped stmts REJECT; base ACCEPT." \
  pv pv4096 4096 art:c24671eeec267cb82ce2ca50cd361329844554f79491469b1150536c69f241cb art:decbf2b3b9e88de6943cb99e8f058eb4352f2f894019bf0aa569eb56ed365a8f -- \
     art:d87b4895ff9817b9bd9120a8c39a1740c009e49aab569b5a1cbc130f4e7e6ffd art:289841b1075e0fc56450cce92109fd6edc84c3dd594515d8b47a37953a06c6a4
has C32 && PV_NOTE="Producer poseidon-v1 (tree lane/poseidon-v1 54ad119d = main + hash-commit harness 6e1cc576 + committer b862be30, prover-side only; verified here with main's verifier). Negatives (05, my verifier): proof byte, chain-end stmt byte, swapped stmts REJECT; base ACCEPT. n = 32768 > the 4096-VU frozen tier: statements are bound to my tree's relchain.instances(rel, 32768) (fp8-ada: the synthetic recipe continued, manifest_sha256 = instances_digest(fp8-ada, 32768); bf16-ampere: frozen ids recycled i mod 4096, frozen manifest digest), whose first 4096 VUs equal the frozen set; whether such a point enters the tables is the renderer's call (poseidon-v1 coordinator 0730Z)." \
  pv pv32768 32768 art:30f6e8db1871cf1c94ec0c93b55b61d3d8af7b33b33ef58ba0a477392b37d232 art:da6298bf6820c12bb8a2bb72f9115a59079635b33fd7facdae98754232efb905 -- \
     art:c8b52ee221d292132655a3b9000660e4ea6151da376be6ef2f248f830c8ecd54 art:b5a4454f754fe0609ed888c93a8386915b243ad0281521049dab42108189b4d7
echo "=== [$(date -u +%H:%M:%S)] 17 done"
