#!/bin/bash
# Gate (a) checks at the final head (/workspace/head4, a2e2843e) that a_head4 left out, on the cheapest rows where they pass at
# be366f80: T1 replay_partition on #101, #57 and #60, and T0 manifest_digest on #60.  Same key sweep as head4_gate.sh.
#   logs: /workspace/out/gates/a_head4_t1.{log,xml,status,keycheck}
L=/workspace/out/gates
KEY_RE='AWS_(SECRET_ACCESS_KEY|SESSION_TOKEN)=["'"'"']?[A-Za-z0-9/+=._-]{20,}'
if [ -e /root/r2ro.env ] || [ -e /workspace/r2ro.env ] || env | grep -q '^AWS_' \
   || grep -rlsqE "$KEY_RE" /root /tmp /workspace/*.env /workspace/*.sh /workspace/rff24 2>/dev/null; then
  echo "$(date -u +%FT%TZ) key present: not started" > $L/a_head4_t1.keycheck; exit 1
fi
echo "$(date -u +%FT%TZ) keyless check passed" > $L/a_head4_t1.keycheck
/workspace/rff24/gate_a.sh /workspace/head4 a_head4_t1 -k "(T1 and replay_partition and (r101 or r57 or r60)) or (T0 and manifest_digest and r60)"
