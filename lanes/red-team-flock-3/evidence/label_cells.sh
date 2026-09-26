#!/usr/bin/env bash
# red-team-flock-3: label attention cells that passed check_cells.sh. First placement_check.py (records + RunPod API through PR #74's
# separation): prover and verifier on separate machines -> proof_class NON_ZK_PROOF; co-resident or not shown separate ->
# NON_ZK_PROOF_DIAGNOSTIC (red-team-flock's ruling, coordinator 2026-09-26 12:00Z). Both with a finding, by red-team-flock-3.
#   PR74=<main's bench/placement.py> label_cells.sh ART...
set -uo pipefail
E=$(cd "$(dirname "$0")" && pwd)
export PYTHONPATH=/workspace/tools/research/src:${PYTHONPATH:-}
export PR74=${PR74:-/tmp/rtf3/placement_main.py}
[ -f "$PR74" ] || { git -C /workspace fetch -q origin main && git -C /workspace show origin/main:backends/numerical/python/verity_numerical/bench/placement.py > "$PR74"; } || { echo "no PR #74 placement.py"; exit 1; }
for a in "$@"; do
  meta=$(research data show $a 2>/dev/null | awk '/^meta/{sub(/^meta +/,""); print}')
  read -r T commit pin ver <<< "$(python3 -c "
import json, sys; d = json.loads(sys.argv[1]); wf = d['workload_fingerprint']; be = wf['software']['backend']
print(be['unit'].split('/')[-1][1:], be['commit'][:8], be['lowering_sha256'][:8], d['derived_from']['verifier_run'])" "$meta")"
  case $commit in
    22dc6320) extra=" F1: at 22dc6320 the statement digest hashes the pre-0839742b TAG (v2 string; Sigma tag and domains v3): cosmetic, domain-separated by v3's extra fields; do not compare its digest with 0839742b cells." ;;
    ece9fdd2) extra=" ece9fdd2 = 0839742b plus harness-only rayon sizing from the cgroup quota (33-ir-cell.sh, 34-ir-selftest.sh); inside the grant." ;;
    0839742b) extra="" ;;
    *) echo "SKIP $a: commit $commit is not a reviewed commit"; continue ;;
  esac
  pl=$(python3 $E/placement_check.py $a | grep '^PLACEMENT' | cut -c11-)
  read -r cls ptext <<< "$(python3 -c "
import json, sys; r = json.loads(sys.argv[1]); p, v = r['prover'], r['verifier']
sep = r['verdict'] == 'SEPARATE' and r.get('pr74') == []
cls = 'NON_ZK_PROOF' if sep else 'NON_ZK_PROOF_DIAGNOSTIC'
ids = (f\"prover pod {p.get('pod_id')} (RunPod machine {p.get('machine_id')}, {p.get('public_ip')}, boot id {str(p.get('boot_id'))[:8]}, kernel {p.get('kernel')}, \"
       f\"{p.get('cpu')}, {p.get('gpu')} driver {p.get('driver')}) vs verifier pod {v.get('pod_id')} (machine {v.get('machine_id')}, {v.get('public_ip')}, \"
       f\"boot id {str(v.get('boot_id'))[:8]}, kernel {v.get('kernel')}, {v.get('cpu')}, {v.get('gpu')} driver {v.get('driver')}); prover dialled {r['network']}\")
t = (f' Placement (red-team-flock ruling 12:00Z; PR #74 separation() on the records + RunPod API): SEPARATE machines, {ids}.' if sep else
     f' Placement: NOT shown separate ({r[\"verdict\"]}; PR #74: {r.get(\"pr74\")}), {ids}: DIAGNOSTIC only; re-run through PR #74 placement check on main.')
print(cls, t)" "$pl")"
  f="red-team-flock-3: GRANTED WITH CONDITIONS, verity/flock-ir-frame/v3 attention (AttentionHead_v3{T=$T,D=64,BN=128}, pin $pin, $commit). This cell's verifier-staged statement ($ver) checked with cell_check.py: netlist = reviewed lowering, wiring = pinned leaf maps (0 diffs; zero leaves on empty runs, holes wired only to empty runs), digests and frame-v3 roots recomputed, e2e units+tail = IR = captured outputs. Review: unit netlist = IR on 2.0e7 adversarial vectors; Rust tail = IR on all 2^32 inputs of ex2/invsum/guard/f2fp and 6.3e6 binary/ternary cases; e2e 0 mismatches on 1,024 captured + 3,024 adversarial heads; 19 prover-side, 34 load, 4 restatement and 3 T/set-confusion negatives refused. The softmax tail (max, ex2, sums, rescale, rcp, cast) is verified natively on public S/P/O words, not proven (4-11% of scalar ops); the cell covers T=$T only. Conditions AC1 (verifier stages its own file and pin, T from its own set) to AC4: lanes/flock-ir-lowering/20260926T1115Z-handoff-from-red-team-flock-3.md.$extra$ptext"
  research data label $a proof_class $cls --by red-team-flock-3 --ref r20260926-103512-bb40 > /dev/null 2>&1 && \
  research data label $a finding "$f" --by red-team-flock-3 --ref r20260926-103512-bb40 > /dev/null 2>&1 && echo "LABELLED $a T=$T $commit $pin $cls" || echo "LABEL FAILED $a"
done
