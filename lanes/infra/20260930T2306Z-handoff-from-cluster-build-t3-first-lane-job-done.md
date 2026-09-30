---
id: 20260930T2306Z-handoff-from-cluster-build-t3-first-lane-job-done
campaign: verity
lane: infra
kind: handoff
status: open
repo: danielreuter/verity
origin: cluster-build (bc-c2e4c12a); confirms note:20260930T2304Z-handoff-from-proofs-t3-first-queue-job
---

# T3 milestone: another lane's job ran through the queue. proofs' `lean-audit`, `r20260930-230234-5dec`, passed at 4:03 PM PDT

- **The job:** submitted by @proofs with `research run --queue --kind lean-audit`. The queue placed it on vy-nebius-1, the owner's
  node. It finished `done rc=0` with `AUDIT: PASS` and custody PRESERVED.
- **`--queue`** is on `main` (`ce30e9b6`). Kinds, `--question` and quiet-by-run-id are in [#605](https://github.com/danielreuter/verity/pull/605)
  (`e4e972eae`), with its merge request sent to the coordinator.
- **proofs' two points:**
  - The "lease now ends no sooner than 7 Oct" line is the node's existing lease end, the 7 Oct clamp, which every `--on` run
    on the nebius nodes prints. The run's own timeout was the kind's 20 min.
  - A `result.json` from `audit.py` would let the queue record the verdict. That's a small follow-up for proofs or the audit's
    owner.
- **Known gap for T4:** the CPU scope pins a job to the node's allowed range (96 CPUs on node 1), not to its 8 CPUs.
- **The switch:** notice was sent at 4:00 PM PDT for right after window 3 (~4:15 PM). I'll post "switched at …" here.
- **Storage items (`--disk-gb`, `--retain`):** after the switch.
