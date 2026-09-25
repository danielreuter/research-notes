#!/bin/bash
# On vyv-rf-b2v-tp2 once prefetch.sh has deleted the key: gate (a) T0,T1 at the head as two processes (the T1 replay_partition
# checks, and the rest; separate scratch), niced and first in line for the OOM killer so row #70's stages keep priority; then the
# merged XML against a23b's same-pod base XML, and the verdict byte comparison under the base tree and the head tree.
#   usage: tp2_gates.sh      logs: /workspace/out/gates/{a_head_rp,a_head_rest,a_head,verdict_bytes}.*
H=/workspace/head; B=/workspace/base; L=/workspace/out/gates; E=/workspace/b2v; PY=/workspace/venv312/bin/python
stamp() { echo "[tp2_gates] $(date -u +%FT%TZ) $*"; }
while ! grep -q '^key deleted' $L/prefetch.log 2>/dev/null; do sleep 15; done
stamp "prefetch: $(grep -c '^ok' $L/prefetch.log) ok, $(grep -c FAIL $L/prefetch.log) FAIL; key file present: $([ -e /root/r2ro.env ] && echo yes || echo no)"
[ -e /root/r2ro.env ] && { stamp "key file still present; refusing"; exit 4; }
env | grep -c '^AWS_' | sed 's/^/[tp2_gates] AWS_ variables in this environment: /'
run() { echo 1000 > /proc/self/oom_score_adj; exec nice -n 10 bash $E/gate_a.sh "$@"; }
stamp "gate (a) head: two processes"
( run $H a_head_rp -k "replay_partition" ) &
P1=$!
( run $H a_head_rest -k "not replay_partition" ) &
P2=$!
stamp "verdict bytes (base, then head)"
for t in base head; do
  T=/workspace/$t
  ( cd $T && CUDA_VISIBLE_DEVICES="" PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src PYTHONDONTWRITEBYTECODE=1 \
    nice -n 10 $PY $E/verdict_bytes.py $L/verdict_bytes/$t > $L/verdict_bytes.$t.txt 2>&1; echo "exit $?" >> $L/verdict_bytes.$t.txt )
done
diff -r $L/verdict_bytes/base $L/verdict_bytes/head > $L/verdict_bytes.diff 2>&1; echo "diff exit $?" >> $L/verdict_bytes.diff
stamp "verdict bytes: $(grep -c record-identical $L/verdict_bytes.head.txt) record-identical, $(grep -c RECORD-DIFFERS $L/verdict_bytes.head.txt) differ (head); $(tail -1 $L/verdict_bytes.diff)"
wait $P1; wait $P2
tail -2 $L/a_head_rp.log $L/a_head_rest.log
$PY - $L/a_head_rp.xml $L/a_head_rest.xml $L/a_head.xml <<'PY'
import sys, xml.etree.ElementTree as ET
root = ET.Element("testsuites")
for p in sys.argv[1:-1]:
    r = ET.parse(p).getroot()
    root.extend([r] if r.tag == "testsuite" else list(r))
ET.ElementTree(root).write(sys.argv[-1], encoding="utf-8", xml_declaration=True)
PY
$PY $E/jdiff.py $E/gate_a-t0t1-base-72884c8a-samepod.xml.gz $L/a_head.xml > $L/a_jdiff.txt 2>&1; echo "jdiff exit $?" >> $L/a_jdiff.txt
tail -30 $L/a_jdiff.txt
stamp done
