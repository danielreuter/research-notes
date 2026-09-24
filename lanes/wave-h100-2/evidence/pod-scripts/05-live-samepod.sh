#!/usr/bin/env bash
# wave-h100-2: FALLBACK live runs. The same-DC verifier pod (vy-wave-h100-verifier 69.30.85.40, CA-MTL-1) is unreachable from
# the prover (69.30.85.160): every public port refused in both directions (GPU.ONE DC does not hairpin public IPs; the laptop
# reaches both). So the live verifier runs on THIS pod (127.0.0.1, --jobs 6 --threads 1, same main 24f252b1 tree and
# ligero-verify build) -- shared-live-2 / integration's same-pod setup: CPU contention caveat, not the brief's same-DC number.
source /workspace/wave-h100-2/scripts/lib.sh
while ! grep -q REST_DONE $O/summary.txt 2>/dev/null; do sleep 3; done
L=$O/live-samepod; mkdir -p $L/sessions
setsid nohup $PY -m backends.direct.ligero.live serve --listen 127.0.0.1:7000 --out $L/sessions --ligero-verify $LIGERO_VERIFY \
  --jobs 6 --threads 1 --target-bits 128 > $L/serve.out 2>&1 < /dev/null &
echo $! > $L/serve.pid; sleep 6
VER=tcp://127.0.0.1:7000
read HF HB < $O/headline.txt
declare -A CFG=([fp8-v3x4-p8]="fp8-hopper-v3x4 4096 8" [fp8-v3x4-p4]="fp8-hopper-v3x4 4096 4" [fp8-v1-p4]="fp8-hopper 16384 4" [fp8-v3-p4]="fp8-hopper-v3 16384 4"
  [bf16-v3x4-p8]="bf16-hopper-v3x4 4096 8" [bf16-v3x4-p4]="bf16-hopper-v3x4 4096 4" [bf16-v1-p8]="bf16-hopper 16384 8" [bf16-v3-p8]="bf16-hopper-v3 16384 8")
lv sp-bare-fp8-$HF ${CFG[$HF]}
lv sp-bare-bf16-$HB ${CFG[$HB]}
lv sp-shared-fp8-p4 fp8-hopper 16384 4 --auth included-hash-shared --tile 64x64
lv sp-shared-bf16-p4 bf16-hopper 16384 4 --auth included-hash-shared --tile 64x64
sleep 5
for d in $L/sessions/s*/; do
  [ -f $d/system.bin ] || continue
  hs=""; [ -f $d/system_h.bin ] && hs="--system-h system_h.bin"
  ( cd $d && $LIGERO_VERIFY batch --system system.bin $hs --dir . --jobs 8 --threads 1 --target-bits 128 \
      --json rust_rebatch.json > rust_rebatch.out 2> rust_rebatch.err )
  echo "$(basename $d) rust rc=$? $($PY -c 'import json,sys;x=json.load(open(sys.argv[1]));print("accepted",x["accepted"],"/",x["n"],"own_coins",x.get("own_coins"),"batch",x["batch_accepted"],"bits %.2f"%x["batch_bits"],"pinned",x["system_pinned"],x["system"]["pinned_relation"])' $d/rust_rebatch.json 2>&1 | tail -1) verdict=$(tr -d '\n ' < $d/verdict.json 2>/dev/null | cut -c1-100)" | tee -a $L/rebatch.txt
done
kill $(cat $L/serve.pid) 2>/dev/null
cp $L/sessions/index.jsonl $L/ 2>/dev/null
( cd $L && tar czf $O/live-samepod-json.tgz --exclude='*.proof' --exclude='*.stmt' --exclude='*.bin' sessions )
$PY -m verity_numerical.bench.summary $O/bare $O/live $O/shared > $O/summary_table.txt 2>&1
$PY -m verity_numerical.bench.summary $O/bare $O/live $O/shared --json > $O/summary_table.json 2>&1
echo LIVE_SP_DONE | tee -a $O/summary.txt
