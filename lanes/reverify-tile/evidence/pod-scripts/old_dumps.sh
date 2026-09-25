#!/usr/bin/env bash
# reverify-tile: fetch the two shared-local cells (shared-live-2, before set.tile) with the read-only key the laptop piped
# into /root/r2ro.env, delete the key at once, then run reverify.commitment_problems (the tip's) on each dump: they must
# fail closed (a v6 dump without set.tile).  Also prints what their manifests' set blocks name.  Outputs /workspace/reverify-tile/old/.
set -uo pipefail
source /workspace/env.sh
cd /workspace/src
set -a; . /root/r2ro.env; set +a
export RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG=/workspace/src/tools/research/store.pod.toml
O=/workspace/reverify-tile/old; mkdir -p $O
while read -r name art; do
  rm -rf "$O/$name"
  $PY -m research.cli data fetch "$art" --to "$O/$name" > /dev/null 2>$O/$name.err && echo "ok $name $art" || { echo "FAIL $name $art"; tail -3 $O/$name.err; }
done <<'LIST'
fp8-ada-shared-local art:fa2be3987db0b45687f51caff76c84bc798c28ca6025cbc2117516e94b520289
bf16-hopper-shared-local art:b460261fb4b0c32429e3e865a6c364543396936ddda1c353ffccfb1ce2977ffe
LIST
rm -f /root/r2ro.env; unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
$PY - <<'PY' 2>&1 | tee $O/old_dumps.log
import json, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, "/workspace/src")
from backends.direct.ligero.relations import relation
from backends.direct.ligero.relchain import instances_digest, tile_digest
from backends.direct.ligero.reverify import commitment_problems
for m in sorted(Path("/workspace/reverify-tile/old").rglob("manifest.json")):
    d = m.parent
    man = json.loads(m.read_text())
    if not (d / "system.bin").is_file():
        continue
    reps = sorted(p.name for p in d.iterdir() if p.is_dir() and p.name.startswith("rep"))
    pinned = json.loads(subprocess.run([os.environ["LIGERO_VERIFY"], "system-digest", "--system", str(d / "system.bin")],
                                       capture_output=True, text=True).stdout)["pinned_relation"]
    s = man.get("set") or {}
    rel = relation(pinned.split("+")[0])
    names = {"unshared instances_digest": instances_digest(rel, s.get("total_vus", 0)), "tile_digest 64x64": tile_digest(rel, 64, 64)}
    print(json.dumps({"dump": str(d), "pinned": pinned, "reps": reps, "set": s,
                      "set.instances is": [k for k, v in names.items() if v == s.get("instances")],
                      "commitment_problems": commitment_problems(d, man, pinned, reps)}), flush=True)
PY
