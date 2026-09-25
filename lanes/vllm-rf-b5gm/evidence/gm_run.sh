#!/bin/bash
# usage: gm_run.sh TREE TAG   the recorded GM-01 command of row #23 (v2 record), f24's evidence/gm_run.sh with two changes:
#   the module is verity_vllm.check.match.global_match (the base's path), and every run writes to the same directory
#   /workspace/out/gm/run (so x09.pipeline.decomp_out is equal across runs), moved to /workspace/out/gm/TAG afterwards.
set -uo pipefail
T=$1; TAG=$2; O=/workspace/out/gm/run; D=/workspace/out/gm/$TAG
[ -e "$O" ] && { echo "refusing: $O exists"; exit 4; }
[ -e "$D" ] && { echo "refusing: $D exists"; exit 4; }
mkdir -p "$O"
cd "$T/integrations/vllm" || exit 3
export PATH=/workspace/venv312/bin:$PATH PYTHONPATH=.:$T/packages/verity/src:$T/tools/research/src HF_HOME=/workspace/hf HF_HUB_OFFLINE=1 \
       VLLM_BATCH_INVARIANT=1 TOKENIZERS_PARALLELISM=false MATCH_IMPL=fast MATCH_PIPELINE=shared PYTHONDONTWRITEBYTECODE=1
unset MATCH_WORKERS PYTHONPYCACHEPREFIX
python3 - "$O" > "$O/cmd.txt" <<"PY"
import sys
o = sys.argv[1]
a = open("/workspace/gm23/matchrec/global_match.log").readline().lstrip("$ ").split()
a[a.index("-m") + 1] = "verity_vllm.check.match.global_match"
a[a.index("--out") + 1] = f"{o}/global_match.json"
a[a.index("--decomp-out") + 1] = f"{o}/match_decomp.json"
print(" ".join(a))
PY
env | grep -E "^(MATCH_|PYTHONPATH|VLLM_|HF_)" | sort > "$O/env.txt"
echo "tree $T tag $TAG start $(date -u +%FT%TZ) load $(cut -d' ' -f1-3 /proc/loadavg)" > "$O/start.txt"
python3 - "$O" <<"PY"
import resource, subprocess, sys, time
o = sys.argv[1]
cmd = open(f"{o}/cmd.txt").read().split()
t0 = time.time()
with open(f"{o}/global_match.log", "w") as out, open(f"{o}/stderr.log", "w") as err:
    rc = subprocess.call(cmd, stdout=out, stderr=err)
wall = time.time() - t0
ru = resource.getrusage(resource.RUSAGE_CHILDREN)
end = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
open(f"{o}/wall.txt", "w").write(f"rc={rc} wall_s={wall:.1f} cpu_user_s={ru.ru_utime:.1f} cpu_sys_s={ru.ru_stime:.1f} "
                                 f"max_rss_gib={ru.ru_maxrss / 2**20:.2f} end={end}\n")
PY
echo "end $(date -u +%FT%TZ) load $(cut -d' ' -f1-3 /proc/loadavg)" >> "$O/start.txt"
mv "$O" "$D"
cat "$D/wall.txt"
