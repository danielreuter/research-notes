#!/usr/bin/env bash
# fill-dc H100: live rounds 1-3 against the same-pod verifier (niced live_serve.sh, tcp://127.0.0.1:7000), then two local
# rounds with rep-1 dumps (the alternative Table 2 candidates if verify-night prefers a Rust reverify of local-coin runs).
# (A `bash -c "...12-rounds.sh..."` wrapper deadlocks: its own command line matches 30-live.sh's pgrep wait.)
cd /workspace/fill-dc
SP=(L-f8b-x4p8:fp8-hopper-v3x4:4096:8 L-f8h-v1p8:fp8-hopper:16384:8:--auth,included-hash
    L-b16b-x4p8:bf16-hopper-v3x4:4096:8 L-b16h-v1p8:bf16-hopper:16384:8:--auth,included-hash)
LIVE=tcp://127.0.0.1:7000 bash scripts/30-live.sh "${SP[@]}"
DUMP=1 PREFIX=dump ROUNDS="1 2" bash scripts/12-rounds.sh "${SP[@]/#L-/D-}"
