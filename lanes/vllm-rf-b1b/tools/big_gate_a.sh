#!/bin/bash
# vyv-rf-b1-big: prefetch every row's fixtures with the read-only key the laptop piped into /root/r2ro.env (prefetch.sh deletes it), then
# gate (a) T0+T1 at head as four processes over disjoint tests, each in its own copy of the tree: everything but replay_partition, and
# replay_partition in three row groups; then the same three replay_partition groups at base on this pod (replay wall time before/after).
#   logs: /workspace/b1/logs/ -> $RESEARCH_RUN_DIR/b1-logs/
set -u
L=/workspace/b1/logs; mkdir -p $L
finish() { rm -f /root/r2ro.env; mkdir -p $RESEARCH_RUN_DIR/b1-logs; cp -a $L/. $RESEARCH_RUN_DIR/b1-logs/; echo "GATE-A-DONE $(date -u +%FT%TZ)"; }
trap finish EXIT
grep -q '^BOOTSTRAP-OK' $L/bootstrap.log || { echo "bootstrap not OK"; exit 3; }
if ! grep -q 'fail=0 key_deleted=yes' $L/prefetch.log 2>/dev/null; then
  [ -s /root/r2ro.env ] || { echo "no key in /root/r2ro.env"; exit 4; }
  bash /workspace/b1/tools/prefetch.sh /workspace/head
  tail -1 $L/prefetch.log
  grep -q 'fail=0 key_deleted=yes' $L/prefetch.log || { echo "prefetch incomplete"; exit 5; }
fi
rp() { local e=""; for r in "$@"; do e="$e${e:+ or }replay_partition-$r]"; done; echo "$e"; }
G1=$(rp r74 r67 r60 r70); G2=$(rp r73 r68 r11 r75); G3=$(rp r39 r57 r101 r4 r23)
( while sleep 30; do echo "$(date -u +%FT%TZ) $(cat /sys/fs/cgroup/memory.current 2>/dev/null) $(ps -eo rss= | sort -n | tail -4 | tr '\n' ' ')"; done ) > $L/gate_a.rss 2>&1 &
MON=$!
for t in A R1 R2 R3; do rm -rf /workspace/ga-head-$t; cp -a /workspace/head /workspace/ga-head-$t; done
bash /workspace/b1/tools/gate_a.sh /workspace/ga-head-A gate_a-head-A -k "not replay_partition" > $L/gate_a-head-A.driver 2>&1 &
PA=$!
bash /workspace/b1/tools/gate_a.sh /workspace/ga-head-R1 gate_a-head-R1 -k "$G1" > $L/gate_a-head-R1.driver 2>&1 &
P1=$!
bash /workspace/b1/tools/gate_a.sh /workspace/ga-head-R2 gate_a-head-R2 -k "$G2" > $L/gate_a-head-R2.driver 2>&1 &
P2=$!
bash /workspace/b1/tools/gate_a.sh /workspace/ga-head-R3 gate_a-head-R3 -k "$G3" > $L/gate_a-head-R3.driver 2>&1 &
P3=$!
wait $P1 $P2 $P3
echo "head replay_partition done $(date -u +%FT%TZ)"; cat $L/gate_a-head-R?.driver
if [ -d /workspace/base/integrations/vllm ]; then
  for t in R1 R2 R3; do rm -rf /workspace/ga-base-$t; cp -a /workspace/base /workspace/ga-base-$t; done
  bash /workspace/b1/tools/gate_a.sh /workspace/ga-base-R1 gate_a-base-R1 -k "$G1" > $L/gate_a-base-R1.driver 2>&1 &
  B1=$!
  bash /workspace/b1/tools/gate_a.sh /workspace/ga-base-R2 gate_a-base-R2 -k "$G2" > $L/gate_a-base-R2.driver 2>&1 &
  B2=$!
  bash /workspace/b1/tools/gate_a.sh /workspace/ga-base-R3 gate_a-base-R3 -k "$G3" > $L/gate_a-base-R3.driver 2>&1 &
  B3=$!
  wait $B1 $B2 $B3
  echo "base replay_partition done $(date -u +%FT%TZ)"; cat $L/gate_a-base-R?.driver
fi
wait $PA
cat $L/gate_a-head-A.driver
kill $MON 2>/dev/null
/workspace/venv312/bin/python - <<'PY'
import xml.etree.ElementTree as ET
L = "/workspace/b1/logs"
for arm, parts in (("head", "A R1 R2 R3"), ("base", "R1 R2 R3")):
    suite = ET.Element("testsuite", name="pytest")
    n = 0
    for p in parts.split():
        try:
            r = ET.parse(f"{L}/gate_a-{arm}-{p}.xml").getroot()
        except Exception as e:
            print(arm, p, "no xml:", e); continue
        for tc in r.iter("testcase"):
            if arm == "head" and p == "A" and "replay_partition" in tc.get("name", ""):
                continue
            suite.append(tc); n += 1
    root = ET.Element("testsuites"); root.append(suite)
    ET.ElementTree(root).write(f"{L}/gate_a-t0t1-{arm}-merged.xml")
    print(arm, "merged", n, "testcases")
    for tc in suite.iter("testcase"):
        if "replay_partition" in tc.get("name", ""):
            st = "skip" if tc.find("skipped") is not None else ("FAIL" if tc.find("failure") is not None or tc.find("error") is not None else "pass")
            print(arm, st, tc.get("time"), tc.get("name"))
PY
