#!/usr/bin/env bash
# lane fp4-port-2: fetch one pod run dir (/workspace/fp4-port-2/<run>) and put + preserve its cited files; appends
# "art:... <what>" lines to evidence/store_ids.txt.   $1 = run (r1..), $2 = commit, $3.. = items: stage[:kind]
#   bench_* stages: proof dump tree + result.json + pinned Rust verdict; others: the stage's log / json files
set -euo pipefail
RUN=$1; COMMIT=$2; shift 2
L=/tmp/fp4p2/$RUN; OUT=~/.research/notes/lanes/fp4-port-2/evidence/store_ids.txt
mkdir -p "$L"
SSH="ssh -i $HOME/.runpod/ssh/runpodctl-ssh-key -p 11113 -o StrictHostKeyChecking=no -o UserKnownHostsFile=$HOME/.runpod/ssh/veritor-campaign-known_hosts -o LogLevel=ERROR"
rsync -a -e "$SSH" --exclude 'auth-cache' root@209.170.80.132:/workspace/fp4-port-2/$RUN/ "$L/"
R=~/.research/bin/research
set -a; source ~/.config/verity/r2.env; set +a
put() {  # $1 kind, $2 --file|--tree, $3 path, $4 meta json, $5.. extra ; echoes the art id
  $R data put --kind "$1" "$2" "$3" --meta "$4" "${@:5}" --preserve --json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('id') or d.get('art') or d)"
}
meta() {  # $1 relation, $2 note, $3 extra json (optional)
  python3 -c "import json,sys; d={'lane':'fp4-port-2','source':'lane/fp4-port@'+sys.argv[1],'hardware':'RTX 4090 (vy-fp4-port kzsdvjpfjxlvif)','run':sys.argv[2],'relation':sys.argv[3],'note':sys.argv[4]}; d.update(json.loads(sys.argv[5] or '{}')); print(json.dumps(d))" \
    "$COMMIT" "$RUN" "$1" "$2" "${3:-}"
}
put_stdout=$(put run-files/v1 --file "$L/stdout.log" "$(meta fp4-nvf4+hash "suite stdout ($RUN)")")
echo "$put_stdout $RUN stdout.log" | tee -a "$OUT"
for S in "$@"; do
  case $S in
    bench_*)
      case $S in *hashed*) REL=fp4-nvf4+hash; X='{"authentication":"included-hash","hash":"poseidon2-babybear-w24"}';; *) REL=fp4-nvf4; X='{"authentication":"excluded","hash":"none"}';; esac
      X=$(python3 -c "import json,sys; d=json.loads(sys.argv[1]); d.update({'mode':'interactive','zk':True,'B':4096,'K':1536,'pipeline':4,'arm':sys.argv[2]}); print(json.dumps(d))" "$X" "$S")
      P=$(put proof/v1 --tree "$L/$S/proofs" "$(meta $REL "proof dump: 4096 VUs, l=16384, --zk --mode interactive, local coins, --pipeline 4, rep 1 (7 sub-batches) + system.bin" "$X")")
      echo "$P $RUN/$S proofs" | tee -a "$OUT"
      B=$(put bench-result/v1 --file "$L/$S/result.json" "$(meta $REL "bench result.json (--pipeline 4, 3 reps, local coins)" "$X")" --ref "proof=$P")
      echo "$B $RUN/$S result.json" | tee -a "$OUT"
      V=$(put verification-verdict/v1 --file "$L/$S/rust_batch_pinned.json" "$(meta $REL "pinned ligero-verify batch (no --allow-any-system) over the rep-1 dump")" --ref "proof=$P")
      echo "$V $RUN/$S rust_batch_pinned.json" | tee -a "$OUT";;
    *)
      I=$(put run-files/v1 --tree "$L/$S" "$(meta fp4-nvf4+hash "stage $S of $RUN")")
      echo "$I $RUN/$S" | tee -a "$OUT";;
  esac
done
