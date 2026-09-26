#!/usr/bin/env bash
# red-team-flock-3: check and label total GEMM re-run cells (verity/flock-pure-block-total, bf16-ampere-total, pin fef256df).
# gemm_cell_check.py (TG6, PB1-PB4, my CPU replay of every recorded session, instance files regenerated from the registered set)
# and placement_check.py (PR #74 separation() on the records + RunPod API). Both pass -> NON_ZK_PROOF; replay/statement fails ->
# no proof_class label (reported); placement not shown separate -> NON_ZK_PROOF_DIAGNOSTIC.
#   label_gemm_cells.sh [--dry] ART...
set -uo pipefail
E=$(cd "$(dirname "$0")" && pwd); DRY=0; [ "${1:-}" = --dry ] && { DRY=1; shift; }
export PYTHONPATH=/workspace/tools/research/src:${PYTHONPATH:-} PR74=${PR74:-/tmp/rtf3/placement_main.py}
REF=lanes/red-team-flock-3/20260926T0958Z-report-red-team-flock-3.md
for a in "$@"; do
  chk=$(python3 $E/gemm_cell_check.py $a --regen 2>&1 | grep '^GEMMCELL' | cut -f2-)
  pl=$(python3 $E/placement_check.py $a 2>&1 | grep '^PLACEMENT' | cut -c11-)
  [ -n "$chk" ] && [ -n "$pl" ] || { echo "SKIP $a: checker output missing"; continue; }
  read -r cls text <<< "$(python3 - "$chk" "$pl" <<'PY'
import json, sys
c, r = json.loads(sys.argv[1]), json.loads(sys.argv[2])
p, v = r["prover"], r["verifier"]
sep = r["verdict"] == "SEPARATE" and r.get("pr74") == []
bad = [k for k, ok in c["checks"].items() if not ok]
ids = (f"prover pod {p.get('pod_id')} (RunPod machine {p.get('machine_id')}, {p.get('public_ip')}, boot id {str(p.get('boot_id'))[:8]}, {p.get('gpu')}) vs "
       f"verifier pod {v.get('pod_id')} (machine {v.get('machine_id')}, {v.get('public_ip')}, boot id {str(v.get('boot_id'))[:8]}, {v.get('gpu') or p.get('cpu') and v.get('cpu')}); "
       f"differing: {','.join(r['differing'])}; prover dialled {r['network']}")
if bad:
    print("NONE", f"FAILED {bad}")
    sys.exit()
cls = "NON_ZK_PROOF" if sep else "NON_ZK_PROOF_DIAGNOSTIC"
place = (f" Placement (PR #74 separation() on the records + RunPod API): SEPARATE machines, {ids}." if sep else
         f" Placement: NOT shown separate ({r['verdict']}; PR #74: {r.get('pr74')}), {ids}: DIAGNOSTIC only.")
f = (f"red-team-flock-3: GRANTED WITH CONDITIONS, verity/flock-pure-block-total (bf16-ampere-total, netlist pin fef256df, domain total; "
     f"PR #87 2^14-row unit slots granted; unit = IR tc_dot_total + F2fpBf16 on 10,485,760 adversarial vectors, r20260926-201903-d07c; "
     f"GPU gate r20260926-202308-c367). This cell (K {c['K']}, B {c['B']}, verifier run {c['verifier_run']}, commit {c['commit']}, binary {c['binary']}): "
     f"TG6 relation/pin/domain={c['domain']}, the statement digest my build recomputes equals the one bound in every session ({', '.join(c['statement_digests'])}); "
     f"PB1 commit and binary named; PB2 union {c['proofs']} proof(s), 2^{c['achieved_log2']}; PB3 my CPU replay (own build of {c['commit']}) accepted "
     f"{c['sessions_accepted']}/{c['sessions_replayed']} recorded sessions, other-session and swapped-rep proofs rejected; PB4 require_link, exchange link, "
     f"one Sigma per sub-batch; the verifier's staged instance files regenerated from the registered input set under tc_dot_total + F2fpBf16: "
     f"byte-identical; contended false.{place}")
print(cls, f)
PY
)"
  echo "== $a $cls"; echo "   $text" | cut -c1-400
  [ "$cls" = NONE ] && continue
  [ $DRY = 1 ] && continue
  research data label $a proof_class $cls --by red-team-flock-3 --ref $REF
  research data label $a verified accepted --by red-team-flock-3 --ref $REF
  research data label $a verifier "flock-pure-gpu replay (CPU, red-team-flock-3 build of the cell's commit), every recorded session" --by red-team-flock-3 --ref $REF
  research data label $a finding "$text" --by red-team-flock-3 --ref $REF
done
