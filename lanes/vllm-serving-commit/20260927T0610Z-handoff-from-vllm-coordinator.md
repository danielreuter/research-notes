---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-serving-commit · kind: handoff · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-27T06:10Z

# Overnight: you are the headline. Budget $40 of new spend, approved by Daniel. The guard is armed to 15:00Z.

Daniel approved the overnight plan (`$STORE/docs/overnight-plan.md`, goal 2; A2 of the headline).

**Targets, in order:**
1. **GPU byte-match on #101's RoPE heads:** serving's committed rows in M0's format (`frame-v3-sha512` rows, `hm96-sha512` leaves,
   SHA-512 roots, registration record) byte-equal to M0's staging of the same values.
2. **Overhead measured:** the commit cost of the new scheme against `vllm-v1` on the same run (time and bytes).
3. **Roots handed to the e2e lane** (`one-stage-e2e`) for run A2, with the registration record and the art ids. Write the handoff to
   `internal/lanes/one-stage-e2e/` and copy it to me.

**Rules:**
- **Opt-in:** `vllm-v1` stays the default and the record. With the scheme off, #101's manifest, roots, run root and verdict equal main's.
- **Money:**
  - The budget is **$40**. Send your estimate to me before the first pod: pod type, hours, dollars, and what each run proves.
  - I approve anything within $40 directly. Beyond $40, root has an $80 reserve that is released only for the headline, so ask me with
    an estimate.
  - Terminate each pod as soon as its outputs are `research data put` (custody preserves only `evidence/`).
- **Pods:** the vyv- guard is re-armed to 15:00Z with a cap of 840, and the day stops at $830. Once I've acked your estimate you can
  create pods (`vyv-rf-serving-commit-*`, `--register --project verity --guard 90`).
- **Checkpoints:** `research notes checkpoint` often (at least every 45 min while working), with pod ids and expected ends.
- **By 14:00Z:** a status handoff (done, spend, open), for the morning report.
