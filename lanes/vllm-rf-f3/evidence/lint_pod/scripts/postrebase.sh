#!/bin/bash
# post-rebase checks (coordinator 00:32Z): every tables_dir() resolves under program/numerics/tables/ and loads through its digest check,
# first with the old env overrides unset, then with them set to a bogus path (they must no longer be read); then the digest-pin test.
#   usage: postrebase.sh TREE TAG      log: stdout (launch_once.sh -> logs/TAG.out)
T=$1; TAG=$2
cd "$T" || exit 3
export PATH=/workspace/venv312/bin:$PATH
export PYTHONPATH=$T/integrations/vllm:$T/packages/verity/src:$T/tools/research/src
export HF_HOME=/workspace/hf PYTHONDONTWRITEBYTECODE=1
unset VERITY_REGRESSION VERITY_REGRESSION_TIERS VERITY_REGRESSION_CANDIDATE VERITY_REGRESSION_ROWS_ROOT VERITOR_REPO
unset VERITY_MUFU_TABLES VERITY_RMS_TABLES VERITY_MUFU_TANH_TABLES VERITY_ARCH
echo "start $(date -u +%FT%TZ) tree $T sha $(python -c 'import json,sys; print(json.load(open(sys.argv[1]))["commit"])' $T/.research-source.json 2>/dev/null)"
check() {
python - <<'PY'
import os
from verity_vllm.program.numerics import fa2_relation as F, rms_relation as R
from verity_vllm.program.registry import prims as P
want = os.sep + os.path.join("verity_vllm", "program", "numerics", "tables") + os.sep
for name, d in (("fa2", F.tables_dir()), ("rms triton", R.tables_dir("triton")), ("rms cuda", R.tables_dir("cuda"))):
    print(f"  {name}: {d} | under program/numerics/tables/: {want in d and os.path.isdir(d)}")
F.tables(); R.tables("triton"); R.tables("cuda")
print("  tables() load + TABLE_SHA256 check: ok")
print(f"  MUFU_TANH_TABLE_DIR: {P.MUFU_TANH_TABLE_DIR} | isdir: {os.path.isdir(P.MUFU_TANH_TABLE_DIR)}")
PY
}
echo "== env overrides unset"; check
echo "== env overrides set to /nonexistent, VERITY_ARCH=sm_90"
VERITY_MUFU_TABLES=/nonexistent VERITY_RMS_TABLES=/nonexistent VERITY_MUFU_TANH_TABLES=/nonexistent VERITY_ARCH=sm_90 check
python -m pytest -q -ra -p no:cacheprovider integrations/vllm/tests/program/test_mufu_tables_pinned.py
echo "exit $? $(date -u +%FT%TZ)"
