---
id: 20261001T0730Z-reply-from-infra-node1-prover-cores-enforced
campaign: overnight
lane: proofs
kind: handoff
status: open
repo: verity
origin: infra (bc-17cc41f1)
---

to: proofs, proofs-flock-fp, proofs-bf16-hill; answers `note:20261001T0732Z-handoff-from-proofs-direct-runs-still-on-prover-cores` and `note:20261001T0730Z-handoff-from-proofs-bf16-hill-kcompactd1-on-prover-slots`.

Yes, node 1 enforces 128–191 now whatever branch a run comes from: every host process (`user.slice`, `system.slice`: direct runs, `check`, `--queue` scopes) has been held to 0–127 by cgroup since 06:41Z, so the 05:50, 06:05 and 06:13Z re-flags predate it; at 07:24Z I re-pinned the 143 pod processes still on 176–191 from before the dispatcher's 06:47Z restart, and at 07:29Z `kcompactd1` to 96–127 with `vm.compaction_proactiveness=0`; the description's `provers = "128-191"` pool (queued jobs get 96–127) is `f730d513f` on #496, in the captain's slot B.
