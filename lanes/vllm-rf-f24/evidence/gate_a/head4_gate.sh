#!/bin/bash
# Gate (a) at the final head (/workspace/head4, a2e2843e), keyless: every T0 check except manifest_digest on every row (the commits after
# be366f80 reach no module of the manifest rebuild), T1 on rows #4, #11, #23 (the keyless T1 rerun; #11 replay_partition needs the big
# pod), and the decisions listing.  Refuses to start if any key is found: a key file, an AWS_* variable, or a secret-shaped value
# (20+ characters after `=`, so this file's own pattern does not match) in /root, /tmp, /workspace/*.env, /workspace/*.sh, /workspace/rff24.
#   logs: /workspace/out/gates/a_head4.{log,xml,status,keycheck}
L=/workspace/out/gates
KEY_RE='AWS_(SECRET_ACCESS_KEY|SESSION_TOKEN)=["'"'"']?[A-Za-z0-9/+=._-]{20,}'
if [ -e /root/r2ro.env ] || [ -e /workspace/r2ro.env ] || env | grep -q '^AWS_' \
   || grep -rlsqE "$KEY_RE" /root /tmp /workspace/*.env /workspace/*.sh /workspace/rff24 2>/dev/null; then
  echo "$(date -u +%FT%TZ) key present: not started" > $L/a_head4.keycheck; exit 1
fi
echo "$(date -u +%FT%TZ) keyless check passed" > $L/a_head4.keycheck
nice -n 5 /workspace/rff24/gate_a.sh /workspace/head4 a_head4 -k "(T0 and not manifest_digest) or (T1 and (r4 or r11 or r23)) or decisions" \
  --deselect "tests/regression/test_regression.py::test_reproduces[T1-replay_partition-r11]"
