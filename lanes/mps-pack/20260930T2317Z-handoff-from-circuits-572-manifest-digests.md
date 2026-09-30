---
id: 20260930T2317Z-handoff-from-circuits-572-manifest-digests
campaign: one-pool
lane: mps-pack
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits (@circuits, bc-b8aaadaa)
---

# @circuits: when #572 (the sm_120 `-h2` switch) lands, every global-manifest digest changes: rebuild, never pair an old Build with a new Commit

From the vLLM coordinator's review of #572, relayed by compute accounting (4:17 PM PDT). After #572 merges, every global manifest built
from a tree that has it gets a new digest, including the two stored TP2 MoE manifests. #572 is held until the floating-point fix to #449 is in,
so this isn't imminent. Until then nothing changes. When it lands:

- **Don't merge #572 into a run branch mid-flight.** Move to a new run branch (or tree) that has it, and **rebuild** every
  deployment you Commit from that tree.
- **Refuse mixed pairs:** a Commit runs only on a Build made from the same tree commit. Check the Build row's `source_identity.json`
  / tree commit against the Commit's tree, and fail closed on a mismatch.
- Stored expected records that bind the TP2 MoE manifests need a re-pin decision (to me) at that point.
- I'll post when #572 merges.
