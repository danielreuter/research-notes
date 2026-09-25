#!/bin/bash
# big2 bootstrap: a1's recipe (`pod_bootstrap.sh --cpu` from the head tree), then xgrammar pinned to a1's 0.2.7, then the venv freeze
# diffed against a1's baseline-freeze.txt (beside this script).      usage: boot.sh      log: stdout (-> /workspace/rff3/bootstrap.log)
cd /workspace/head/integrations/vllm || exit 3
bash verity_vllm/ops/pod_bootstrap.sh --cpu --out /workspace/bootstrap || { echo "BOOT-FAIL bootstrap"; exit 4; }
export PATH=$HOME/.local/bin:$PATH
uv pip install --python /workspace/venv312/bin/python xgrammar==0.2.7 || { echo "BOOT-FAIL xgrammar"; exit 5; }
uv pip freeze --python /workspace/venv312/bin/python > /workspace/rff3/freeze.txt
diff /workspace/rff3/baseline-freeze.txt /workspace/rff3/freeze.txt > /workspace/rff3/freeze.diff
echo "freeze diff vs a1:"; cat /workspace/rff3/freeze.diff
echo "BOOT-DONE $(date -u +%FT%TZ)"
