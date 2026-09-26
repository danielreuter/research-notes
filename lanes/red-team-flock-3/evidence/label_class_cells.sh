#!/usr/bin/env bash
# red-team-flock-3: label key-count class cells that passed check_class_cells.sh. placement_check.py first (records + RunPod API
# through PR #74's separation): separate machines -> NON_ZK_PROOF, else NON_ZK_PROOF_DIAGNOSTIC; a finding either way.
#   label_class_cells.sh ART...
set -uo pipefail
E=$(cd "$(dirname "$0")" && pwd)
export PYTHONPATH=/workspace/tools/research/src:${PYTHONPATH:-} PR74=${PR74:-/tmp/rtf3/placement_main.py}
[ -f "$PR74" ] || { echo "no PR #74 placement.py at $PR74"; exit 1; }
for a in "$@"; do
  meta=$(research data show $a 2>/dev/null | awk '/^meta/{sub(/^meta +/,""); print}')
  read -r commit pin lo hi nT heads ver <<< "$(python3 -c "
import json, sys; d = json.loads(sys.argv[1]); wf = d['workload_fingerprint']; be = wf['software']['backend']; k = wf['key_class']; kc = wf['key_counts']
print(be['commit'][:8], k['pin'][:8], k['T'][0], k['T'][1], len(kc), sum(kc.values()), d['derived_from']['verifier_run'])" "$meta")"
  case $commit in 11f24da6|4eb3b991|31d275ad|53ffcaca) ;; *) echo "SKIP $a: commit $commit is not a reviewed class commit"; continue ;; esac   # 31d275ad, 53ffcaca: harness only after 11f24da6
  pl=$(python3 $E/placement_check.py $a | grep '^PLACEMENT' | cut -c11-)
  read -r cls ptext <<< "$(python3 -c "
import json, sys; r = json.loads(sys.argv[1]); p, v = r['prover'], r['verifier']
sep = r['verdict'] == 'SEPARATE' and r.get('pr74') == []
ids = (f\"prover pod {p.get('pod_id')} (RunPod machine {p.get('machine_id')}, {p.get('public_ip')}, boot id {str(p.get('boot_id'))[:8]}, {p.get('gpu')}) vs \"
       f\"verifier pod {v.get('pod_id')} (machine {v.get('machine_id')}, {v.get('public_ip')}, boot id {str(v.get('boot_id'))[:8]}, {v.get('gpu')}); differing: \"
       f\"{','.join(r['differing'])}; prover dialled {r['network']}\")
print('NON_ZK_PROOF' if sep else 'NON_ZK_PROOF_DIAGNOSTIC',
      (f' Placement (red-team-flock 12:00Z ruling; PR #74 separation() on the records + RunPod API): SEPARATE machines, {ids}.' if sep else
       f' Placement: NOT shown separate ({r[\"verdict\"]}; PR #74: {r.get(\"pr74\")}), {ids}: DIAGNOSTIC only; re-run through PR #74 placement check on main.'))" "$pl")"
  f="red-team-flock-3: GRANTED WITH CONDITIONS, verity/flock-ir-frame/v3 attention under a key-count class pin (flock-ir-class/v1 [$lo, $hi], pin $pin, $commit; 11f24da6 = 4eb3b991 + CP2 canonical manifest; 31d275ad and 53ffcaca change only the replay script and ir_bench's NVML wait). One v3 session per T under that T's reviewed netlist, T taken from the verifier's own staged file; the manifest is the verifier's own (CP1) and all its nets equal the reviewed generator's per-T netlists (CP5; verifier class.json byte-identical to mine). This cell ($ver): manifest_check PASS; every sub-batch's verifier-staged file through cell_check.py (netlist = reviewed lowering pinned by the file, leaf maps 0 diffs, digests/roots, e2e units+tail = IR = set outputs; the sub-batch's heads all at its T); key_counts ($nT T values, $heads heads) = the verified sub-batches' T (CP8: full-set point). Credit per listed T at heads/e2e_s from per_key_count: census-json PR #79 on main (CP7 met). Inputs synthetic (key_class_sets; CP6: the coordinator's call for the #101 headline). The softmax tail is verified natively on public words, not proven; review evidence art:8be608c6 (class negatives r20260926-132829-2165) + art:25c96f97; conditions: lanes/flock-ir-lowering/20260926T1340Z-handoff-from-red-team-flock-3.md.$ptext"
  research data label $a proof_class $cls --by red-team-flock-3 --ref r20260926-132829-2165 > /dev/null 2>&1 && \
  research data label $a finding "$f" --by red-team-flock-3 --ref r20260926-132829-2165 > /dev/null 2>&1 && echo "LABELLED $a class [$lo, $hi] $nT T $heads heads $commit $pin $cls" || echo "LABEL FAILED $a"
done
