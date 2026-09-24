#!/usr/bin/env bash
# wave-h100-2: put + preserve one pulled cell dir. $1 = local cell dir (result.json [+ proofs/ + proofs/rust_batch.json]),
# $2 = relation, $3 = note, then label key=value pairs. Appends "art:... <what>" to evidence/store_ids.txt.
set -euo pipefail
D=$1; REL=$2; NOTE=$3; shift 3
OUT=~/.research/notes/lanes/wave-h100-2/evidence/store_ids.txt
R=~/.research/bin/research
set -a; source ~/.config/verity/r2.env; set +a
SRC="lane/wave-h100@24f252b1"
meta() { python3 -c "import json,sys; print(json.dumps({'by':'wave-h100-2','lane':'wave-h100-2','commit':'24f252b1','device':'H100 80GB HBM3 (RunPod GPU.ONE Dorval QC, vy-wave-h100b)','relation':sys.argv[1],'note':sys.argv[2]}))" "$REL" "$1"; }
put() { $R data put --kind "$1" "$2" "$3" --meta "$4" "${@:5}" --preserve --json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('id') or d.get('art') or d)"; }
refs=()
if [ -d "$D/proofs" ]; then
  P=$(put proof/v1 --tree "$D/proofs" "$(meta "proof dump rep 1 + system.bin: $NOTE")"); echo "$P $D proofs" | tee -a $OUT; refs+=(--ref "proof=$P")
  if [ -f "$D/proofs/rust_batch.json" ]; then
    V=$(put verification-verdict/v1 --file "$D/proofs/rust_batch.json" "$(meta "pinned ligero-verify batch (main 24f252b1) over the rep-1 dump: $NOTE")" --ref "proof=$P")
    echo "$V $D rust_batch.json" | tee -a $OUT
  fi
fi
B=$(put bench-result/v1 --file "$D/result.json" "$(meta "$NOTE")" "${refs[@]}"); echo "$B $D result.json" | tee -a $OUT
for kv in "$@"; do $R data label "$B" "${kv%%=*}" "${kv#*=}" --by wave-h100-2 >/dev/null; done
$R data label "$B" source "$SRC" --by wave-h100-2 >/dev/null
$R data label "$B" lane wave-h100-2 --by wave-h100-2 >/dev/null
echo "$B"
