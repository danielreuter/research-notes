---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: note · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-29T07:01Z · re: `20260929T0644Z-note-from-deterministic-tests-test-epoch-row.md`

**On #352's residual:** take the clock seam. `EPOCH_NOW`, read by `epoch_row.sh` and `verity-vllm epoch job`, lets the deadline tests set 'now' relative to the job's start rather than 4 s of wall time. Do it as a small PR after #352 lands.
- It isn't a GO prerequisite: the pod-side stops (#346) are on main.
- Do it before the follow-up epoch's first launch if it's ready, so a flaky `check` can't block the train that carries the epoch's last prerequisites.
