#!/usr/bin/env bash
# wave-h100-2, on vy-wave-h100-verifier: pinned Rust batch re-verify (main 24f252b1 build, /workspace/bin/ligero-verify) of
# every live session dir, then a JSON-only tar of the store (no .proof/.stmt) for custody.
S=/workspace/live/sessions; O=/workspace/wave-h100-2; mkdir -p $O; : > $O/rebatch.txt
for d in $S/s*/; do
  [ -f $d/system.bin ] || continue
  hs=""; [ -f $d/system_h.bin ] && hs="--system-h system_h.bin"
  ( cd $d && /workspace/bin/ligero-verify batch --system system.bin $hs --dir . --jobs 7 --threads 1 --target-bits 128 \
      --json rust_rebatch.json > rust_rebatch.out 2> rust_rebatch.err )
  echo "$(basename $d) rust rc=$? $(/workspace/venv312/bin/python -c 'import json,sys;x=json.load(open(sys.argv[1]));print("accepted",x["accepted"],"/",x["n"],"own_coins",x.get("own_coins"),"batch",x["batch_accepted"],"bits %.2f"%x["batch_bits"],"pinned",x["system_pinned"],x["system"]["pinned_relation"])' $d/rust_rebatch.json 2>&1 | tail -1) verdict=$(tr -d '\n ' < $d/verdict.json 2>/dev/null | cut -c1-120)" | tee -a $O/rebatch.txt
done
cd /workspace/live && tar czf $O/live-store-json.tgz --exclude='*.proof' --exclude='*.stmt' --exclude='*.bin' sessions
ls -la $O
echo REBATCH_DONE
