#!/bin/bash
# vyv-rf-c1-big (cpu3m 64 vCPU / 512 GB): pod_bootstrap.sh --cpu from the head tree, pytest-xdist 3.8.0, xgrammar pinned to 0.2.7
# (a1's baseline environment), and the freeze diff against a1's baseline-freeze.txt.   logs: /workspace/c1/logs/ -> $RESEARCH_RUN_DIR/c1-logs/
set -u
L=/workspace/c1/logs; mkdir -p $L
IN=$RESEARCH_RUN_DIR/inputs
cp $IN/*.sh $IN/*.py $IN/baseline-freeze.txt /workspace/c1/ 2>/dev/null
finish() { mkdir -p $RESEARCH_RUN_DIR/c1-logs; cp -a $L/. $RESEARCH_RUN_DIR/c1-logs/; echo "BOOT-DONE $(date -u +%FT%TZ)"; }
trap finish EXIT
echo "bootstrap start $(date -u +%FT%TZ)"
( cd /workspace/head/integrations/vllm && bash verity_vllm/ops/pod_bootstrap.sh --cpu --out /workspace/c1/bootstrap ) > $L/bootstrap.log 2>&1
tail -3 $L/bootstrap.log
grep -q '^BOOTSTRAP-OK' $L/bootstrap.log || { echo "BOOT-FAIL"; exit 3; }
export PATH=$HOME/.local/bin:$PATH
uv pip install --python /workspace/venv312/bin/python pytest-xdist==3.8.0 xgrammar==0.2.7 > $L/uv_extra.log 2>&1; echo "uv extra rc=$?"
uv pip freeze --python /workspace/venv312/bin/python > $L/freeze.txt 2>/dev/null
diff /workspace/c1/baseline-freeze.txt $L/freeze.txt > $L/freeze.diff; echo "freeze diff lines: $(wc -l < $L/freeze.diff)"
cat $L/freeze.diff
/workspace/venv312/bin/python -c 'import sys, torch; print(sys.version.split()[0], torch.__version__, torch.cuda.is_available())'
uname -r; nproc; free -g | head -2
