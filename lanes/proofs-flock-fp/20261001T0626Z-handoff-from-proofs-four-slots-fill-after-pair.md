---
id: 20261001T0626Z-handoff-from-proofs-four-slots-fill-after-pair
campaign: overnight
lane: proofs-flock-fp
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# Four prover slots: two for you now, all four once verify-overlap's pair submits

Infra, 11:21 PM PDT: provers run on cores 128–191, which makes four 16-core slots, and may borrow every idle node-1 GPU (up to 8).
Commits still take GPUs back. CPU slots, not GPUs, are now the limit.

- **Until verify-overlap's pair has submitted:** BF16 and FP8/FP4 together hold at most 2 slots, staging jobs included.
  At 11:25 PM PDT you held exactly 2 (bf16-hill-k8192-s1-csc, fp-hill-stage-k16384), so refill only your own slot as it frees.
  Hold check (unchanged): `grep '"ev": "submit"' /workspace/jobs/dispatch/log.jsonl | grep 'proofs-verify-overlap/' | grep nvidia.com/gpu | tail -1`
  shows a submission after 06:26Z.
- **After it submits:** fill every free slot, with GPU points ahead of staging. Daniel's goal is every format at all four K,
  hill-climbed as far as it goes, with `cpu-slice-shared` and `draft-554-unreviewed` cleared. Every job still names
  its question.
- **Node 1's window:** queues hold at 5:10 AM PDT, nothing new starts after 5:15, and `/workspace` is offline 5:40–5:55. Submit
  nothing after 5:05 that could still be running at 5:35. If anything you plan runs longer, tell me by 5:15 so I can tell infra
  by 5:30.
- **Naming (Daniel, 11:11 PM PDT):** the pre-timing check is the **preflight check**, never the "gate", in notes and
  reports from now on. verify-overlap does the code rename together with its once-per-session preflight change, in one tree,
  because the stage-cache key hashes every `.py` file. Don't rename in your trees; merge that tree when it lands.
