---
id: 20260930T2343Z-handoff-from-old-circuits-and-proofs-tp-attach-rank-idle-splits
campaign: overnight-sep30
lane: vllm-staging-bug
kind: handoff
status: open
repo: danielreuter/verity
origin: old-circuits-and-proofs (bc-ecac3029)
---
# Follow-up to #611: the TP path

`taps.attach_rank` (the TP rank side) does not set `com.prescribe_idle_splits`, and `for_ranks` returns None when no tap is on. So TP2 Gumbel B>1 still leaves `runner.sampler/splits` unbound. Wire the same manifest check into the rank setup: rank_worker, where the committer is made, or attach_rank, with for_ranks running when `sampler_splits` is required. Add a test, then verify on one TP2 Gumbel B8 row once #609 (the GPU-less TP2 Build) lands. Reply with a -handoff- in lanes/old-circuits-and-proofs/.
