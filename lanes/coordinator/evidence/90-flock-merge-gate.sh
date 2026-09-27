#!/usr/bin/env bash
# coordinator: gate of the Flock merge chain (PR #36 tail + #30 + #34) on a CPU pod: builds and the lanes' selftests
set -uo pipefail
echo "tree: $(pwd) $(cat .research-source.json 2>/dev/null | head -c 200)"
bash backends/flock/pod/00-setup-cpu.sh > $RESEARCH_RUN_DIR/setup.log 2>&1; echo "setup rc=$?"
GPU=0 MODE=build bash backends/flock/pod/20-gpu-link.sh > $RESEARCH_RUN_DIR/gl-build.log 2>&1; echo "gpu-link CPU build rc=$?"
GPU=0 MODE=selftest VUS="8 64" bash backends/flock/pod/20-gpu-link.sh > $RESEARCH_RUN_DIR/gl-selftest.log 2>&1; echo "gpu-link selftest rc=$?"; grep -h "SELFTEST" $RESEARCH_RUN_DIR/gl-selftest.log | tail -4
for rel in bf16-hopper fp8-ada; do REL=$rel MODE=selftest SELF_VUS="8 64" bash backends/flock/pod/20-pure.sh > $RESEARCH_RUN_DIR/pure-$rel.log 2>&1; echo "pure $rel selftest rc=$?"; grep -h "SELFTEST" $RESEARCH_RUN_DIR/pure-$rel.log | tail -3; done
SKIP_BENCH=1 bash backends/flock/pod/10-link.sh > $RESEARCH_RUN_DIR/link.log 2>&1; echo "flock-link selftest rc=$?"; grep -h "SELFTEST" $RESEARCH_RUN_DIR/link.log | tail -4
echo GATE-DONE
