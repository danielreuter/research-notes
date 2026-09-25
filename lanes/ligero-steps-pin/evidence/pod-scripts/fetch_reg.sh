#!/usr/bin/env bash
# ligero-steps-pin: fetch the regression artifacts into /workspace/reg/<name> with the read-only key the laptop piped
# into /root/r2ro.env (kb/ops-tools.md recipe), then delete the key at once.
set -uo pipefail
source /workspace/env.sh
cd /workspace/src
set -a; . /root/r2ro.env; set +a
export RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=/workspace/src/tools/research/store.pod.toml
mkdir -p /workspace/reg
while read -r name art; do
  d=/workspace/reg/$name; rm -rf "$d"
  $PY -m research.cli data fetch "$art" --to "$d" > /dev/null 2>/workspace/reg/$name.err && echo "ok $name $art" || { echo "FAIL $name $art"; tail -3 /workspace/reg/$name.err; }
done <<'EOF'
fp8-ada-bare-t2 art:2c8d508966c8232d3cd5a88bd7f059c6f8a8f18876c5646e0ad870ec3045bb83
fp8-ada-hash-t2 art:527e99be903e2fea4ca6529a84d80e9d4812daa83cc510ab194070a3f671a993
fp8-ada-blake3 art:a2e7503c01869d80e415abe9e7e7059eeaa25499502fbaac5cc1f750680025f9
bf16-hopper-blake3 art:78121b220b6cc98a4036c30383dcef1268d34f9de56123e72994af10641cf1df
fp8-ada-x4-blake3 art:51b6e9e0a30cb817413f2917c3564cec10ac1466d647a8d3e2e0ece1c5c6cd07
fp8-ada-shared-local art:fa2be3987db0b45687f51caff76c84bc798c28ca6025cbc2117516e94b520289
bf16-hopper-shared-local art:b460261fb4b0c32429e3e865a6c364543396936ddda1c353ffccfb1ce2977ffe
fp8-ada-bare-local art:c1e415dec055461559341949af2018e8b45bb4dbedb19973265c9dadbf9fe3a1
bf16-hopper-bare-local art:62395cc93f0e60897b8e2eaad6b540faf469b2d424218ba1941f85798a2adfce
EOF
rm -f /root/r2ro.env; unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
du -sh /workspace/reg/*/ 2>/dev/null
