---
id: 20261001T1548Z-handoff-from-proofs-owner-yes-prover-changes-1a-5-9
campaign: proofs-hillclimb
lane: proofs-bf16-hill
kind: handoff
status: open
repo: verity
origin: proofs (bc-8416bc72-c4cc-5551-93a8-b14a6e5f95d4)
---

# The research owner says yes to prover changes 1a, 5 and 9; build them for the 11:30 AM PDT set

to: proofs-bf16-hill. Act on this when your current item finishes or reaches a stopping point, before you start anything else.

**The yes.** The research owner (bc-ecac3029, author verified) said yes at 8:41 AM PDT (Slack `1790869300.844139`) to
three changes:
- 1a, the SWAR GF(2^8) products;
- 5, no `cudaMalloc`/`cudaFree` in steady-state sessions;
- 9, the session-boundary host code taken off the critical path.

**Its conditions:**
- Each change lands only with byte-identical proofs and verdicts on the K set it was measured at.
- Each change has one negative control that fails when the change is broken.
- M0, as code owner, can still veto how a change is done.

M0 was asked again at 8:40 AM PDT (Slack `1790869228.798669`), and the top-level is taking it to Daniel at about 8:50.
So build the changes on your own branch, not in M0's tree. Nothing lands until M0 or Daniel agrees.

**Targets.** Daniel's 11:30 AM PDT set has these as floors, on node 1, each the mean of two samples:

| Cells | Floor |
|---|---|
| BF16 K=2048 | ≤ 3.95e7 |
| BF16 K=4096 | ≤ 2.12e7 |
| BF16 K=8192 | ≤ 2.14e7 |
| BF16 K=16384 | ≤ 2.30e7 |
| Packed FP cells where packing doubles n | −6% against their packed best |
| Packed FP cells where packing quadruples n (K=16384) | −12% against their packed best |

- For the packed points, use flock-fp's `a30bc8e5b` tree with your changes on top, and its step-4 settings with
  `FLOCK_PACK_WORDS=1`.
- Order: 1a first (your prototype), then 9 (your CPU-sampled profile names it), then 5. Run BF16 points as each change
  proves byte-identical, then the packed cells.
- Record, for each change, its commit, the K points it was measured at, their statement digests and proof-byte hashes
  against the step they compare with, and the negative control's failure.

**Node 1.** Proofs' cap is 4 GPU jobs. You get up to 3 at once, and verify-overlap takes 1. Submit through `provers` and
request 64 GiB at K ≤ 4096 and 128 GiB at K ≥ 8192. Label each job with `question`.

**Reporting.** Only results or a blocker, in `lanes/proofs/`. Leave M0's tree, main and other lanes' branches untouched, and
open no PR.
