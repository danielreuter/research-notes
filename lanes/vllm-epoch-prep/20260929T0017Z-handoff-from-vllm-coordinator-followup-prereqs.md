---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-prep · kind: handoff (CPU only, no pods) · from: vllm-coordinator (bc-ecac3029) · cc flock-ir-lowering (bc-9916bbb1) · created: 2026-09-29T00:17Z

# Follow-up epoch prerequisites 3 and 4: open them as PRs now

The plan is the "Follow-up epoch: draft plan" section of `lanes/coordinator/20260928T0420Z-plan-vllm-rebaseline-epoch.md`. Daniel sets the cap later, and **no GPU spend** is allowed in the meantime. The detail for both items is in my 20:48Z handoff (`20260928T2048Z-handoff-from-vllm-coordinator-75-two-producers-and-101-g4.md`).

**Prerequisite 3: the TP2 MoE two-producer manifest fix.**
- The MoE block's `AllReduce2` output becomes its own member (or the rank partials bind to the member the collective writes), so that `tp_peer_binding.n_unbound` is 0 on #75's (`art:8f0d249a`) and #70's (`art:82931d60`) stored Builds, on CPU.
- `build manifest` exits non-zero on `complete False` for a row of record.
- Add a test on a TP2 MoE stand-in.

**Prerequisite 4: #101's G4 fold count, off by 32.**
- Make G4 a bijection on try 5's stored Build and records (`art:0e6911da`, `art:55029fe0`), on CPU.
- Agree with the lowering lane which side owns the fix, the fold or `as_fold_selects`.

**For each:** send the PR head to me in `lanes/vllm-coordinator/`, and a merge request to the research coordinator. If either is blocked, write one line saying why.
