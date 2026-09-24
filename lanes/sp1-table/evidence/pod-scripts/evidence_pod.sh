#!/bin/bash
# sp1-table (pod): preserve the lane's exploratory evidence (not a result) before the pod is terminated: executor
# comparisons of every kernel variant (exec-*.json), check_vu disassemblies, build/test logs, prover-option probe logs
# (gzipped, no proofs), the fresh-build reproduction, the pod scripts, and the verified guest ELF (k7m, f11cf2cc...).
# The credential is `research data mint-credential --env` output on STDIN, never a file.
#   research data mint-credential --ttl 1h --env | psshi bash /workspace/sp1-table/evidence_pod.sh
set -euo pipefail
set -a; eval "$(cat)"; set +a
C=/workspace/sp1-table/store.pod.toml
export PYTHONPATH=/workspace/research/tool/fdc139c9183a52e8 RESEARCH_STORE=/workspace/research/store RESEARCH_STORE_CONFIG="$C"
S=/workspace/sp1-table
W=$S/evidence-tree; rm -rf "$W"; mkdir -p "$W"/{exec,disasm,logs,probe-env,probe,scripts}
cp $S/exec-*.json "$W/exec/"
cp $S/check_vu*.s "$W/disasm/"
cp $S/build-*.log $S/build-bare.out $S/build_k10.out $S/bootstrap.out $S/test-bare.out $S/test_k10.out $S/negatives.jsonl \
   $S/probe_env.out $S/probe_env2.out $S/probe_threshold.out $S/probe_threshold2.out $S/repro_verify.out "$W/logs/"
cp $S/*.sh $S/*.py "$W/scripts/"
for f in $S/probe-env/*.jsonl $S/probe-env/*.log; do gzip -c "$f" > "$W/probe-env/$(basename "$f").gz"; done
find $S/probe -maxdepth 1 -type f \( -name "*.jsonl" -o -name "*.log" -o -name "*.json" -o -name "*.out" \) \
  -exec sh -c 'gzip -c "$1" > "$2/$(basename "$1").gz"' _ {} "$W/probe" \;
cp $S/guest-k7m.elf "$W/guest-k7m.elf"
sha256sum "$W/guest-k7m.elf"
du -sh "$W"
python3 -m research data put --kind run-files/v1 --tree "$W" \
  --meta '{"lane": "sp1-table", "purpose": "exploratory evidence behind the sp1-table report (not a bench result): kernel variant executor comparisons k2..k10, disassemblies, prover-option probes, fresh-build ELF reproduction", "listed": ["exec", "disasm", "logs", "probe-env", "probe", "scripts", "guest-k7m.elf"]}' \
  --preserve --json | python3 -c 'import json,sys; d=json.load(sys.stdin); assert (d.get("preserve") or {}).get("preserved"), d; print(d["id"])'
rm -rf "$W"
