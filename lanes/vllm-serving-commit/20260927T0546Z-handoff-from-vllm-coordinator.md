---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-serving-commit · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T05:46Z

# Welcome. How to report, and the money and pod rules.

You report to me (vllm-coordinator bc-ecac3029). Lane rules: `internal/lane-briefs/vllm-cloud-common.md` (no waiting inside a turn,
gate (b) in a git clone, the partition checker with 0 recomputes in reviews).

- **Scope, from root:** vLLM serving commits in M0's format (`frame-v3-sha512` rows, `hm96-sha512` leaves, SHA-512 roots, plus a
  registration record), so the one-stage audit links to what serving committed.
  - **Opt-in:** `vllm-v1` stays the default and the record, and the switch waits for the re-baseline.
  - The SHA-512 framings and `hm96-sha512/v1` are on main (PR #93). Their vectors are the spec.
- **Default path byte-identical:** with the scheme off, #101's manifest, commit roots, run root and verdict must equal main's.
  - On CPU, from the stored record Build `art:9cb3a4df…` (Program `ccc21347…`, manifest `90f81868…`).
  - On GPU: #101's run root `7adcef49…` with the scheme off.
- **Money:** the day is at $739 of $770 and stops at **$760**, so about $21 is left for everything.
  - Hand me an estimate before any pod: pod type, hours, dollars, and what each run proves. Root will get Daniel's approval if it needs
    more; this is top priority.
  - CPU work (the scheme, vectors, unit tests, the CPU A/B) needs no approval.
- **Guard:** the vyv- deadline lapses at 06:30Z with no pods running. Tell me in a checkpoint when a pod is about to start, and I'll
  re-arm the guard and clear any trip first. **Don't create a pod before I confirm**, or the guard will kill it.
- **Hand-offs:** merge-ready handoffs go to `internal/lanes/vllm-coordinator/`, with gate (b) and the default-path A/B.
