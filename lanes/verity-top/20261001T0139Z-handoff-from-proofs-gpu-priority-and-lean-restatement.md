---
id: 20261001T0139Z-handoff-from-proofs-gpu-priority-and-lean-restatement
campaign: verity
lane: verity-top
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72)
---

# Daniel (6:35 PM PDT): GPUs are scarce, and circuits makes as many validated vLLM circuits as possible; two asks for you, one for lean

to: verity-top (bc-7f347b4b). Daniel told me directly to settle with you how to prioritize this and how proofs and circuits
coordinate. He also asked that the Lean restatement go past lean (bc-19c498a8), which sets the Lean standards. I can't
reach lean myself, so the third ask is for you to forward.

## What proofs does now, without waiting (all reversible, inside my lanes)

- **No GPU held idle.** My 6:31 PM PDT watch called GPUs not scarce; that was wrong. Grafana caught flock-fp's prover pod
  holding GPU 0 at 0% for 10 minutes while it staged a statement on the CPU. Statement staging moves into 0-GPU jobs,
  using proofs-rows' split (byte-identical statements, 3.4 GPU-min saved per stage-cache miss).
- **At most one GPU per proving lane** (bf16-hill, flock-fp, verify-overlap), so three on node 1 at the peak and usually
  fewer. No new GPU points beyond the 11:40 PM PDT goal list until you rule.
- **The verifier off the GPU stays our top priority** (verify-overlap). Today the GPU is held about 8.3 s per 1.02 s prove,
  and tonight's points show 2 to 46% GPU utilization. Overlap is the one change that frees most of proofs' GPU time.

## Ask 1: the GPU split between circuits and proofs

**My recommendation:** circuits' vLLM work (Builds, Commits, replays) goes first on both nodes. Proofs keeps a floor of
two GPUs on node 1 for the hillclimb, which is Daniel's other standing objective; it's held only while proving and
released as soon as a point is done. Infra enforces this as queue priority, not by agents' good manners. Shrinking the
floor to one, or to zero overnight, is your call.

## Ask 2: how proofs helps circuits make validated circuits

What proofs already has that circuits can use, in the order I'd offer it:
1. **The Boolean IR** (`docs/boolean-ir.md`, settled by Daniel at 6:23 PM PDT). vLLM's Programs can move to it now, since
   the special-function tables are already Boolean (one-hot ROMs). proofs-ir's first slice is the BF16
   `GemmCoordinate_v3`. **Question:** should its second slice be whichever circuit circuits most needs validated next?
   I'd say yes, chosen by circuits.
2. **Pinned sm_120 step Definitions**: E4M3, E5M2, MXFP4 and NVFP4, measured on the PRO 6000 with 0 mismatches and
   circuit-check green. They're on unmerged proofs branches; I'll open one consolidated PR for the old RC's next train, so
   circuits' FP8 and FP4 models can use them.
3. **circuit-check and Definition reviews**, if circuits' bottleneck is checking rather than GPUs. One worker, on
   circuits' orders.

**CPU contention runs the other way too** (`note:20261001T0137Z-handoff-from-proofs-flock-fp-vllm-jobs-on-prover-slices`).
On node 1, the vLLM pipeline jobs pin no cores, so they run on the provers' slices (96–159) while cores 0–95 and
160–191 sit idle. That's infra's dispatcher, and infra already has my request to widen the range.

**Channel:** I'd take circuits' requests in `lanes/proofs/` or on Slack, with @circuits giving its own lanes' orders and
me giving mine.

## Ask 3, for lean (bc-19c498a8): the C-Flock restatement against its standards

State: the writer (proofs-lean-restate, bc-3b607340) pushed `cursor/proofs-lean-restate-95d4` at `d6c8b0e37` (6:19 PM
PDT): `SHA512CRStrict` and `SHA512CRExpected`, L1 dropped, a `Certificate.lean`, and `δ_tree` in the end-to-end bounds.
Its pins aren't committed yet, and its `audit.py --update` runs next. red-team-flock-3 is the reviewer of record. Its first pass
was OBJECT with seven changes, and its acceptance test (my 6:31 PM PDT ruling) is that every `--update` entry traces to one
of the seven changes or to L1's removal, all in one PR.

Questions for lean, each with my default if it has no view:
1. Does this review follow `docs/lean-infrastructure.md` §12 now, with the footprint line, the retired list and the
   teeth checked by hand? Default: yes, added to the reviewer's checklist.
2. Is the footprint `cr/sha-512` (strict), `ecr/sha-512` (expected) and `uniform/io-getrandombytes` (A3), and nothing
   else? Round-coin uniformity is unnamed today. Default: name it, or state it as A3's scope.
3. Should lean be a second reviewer, or only set the criterion? Default: it sets the criterion, and red-team-flock-3 reviews.
4. Should the restatement wait for the pilot's registry? §12 says no: it finishes under today's rules and adopts the
   registry in rollout step 6. Default: no.

Nothing gets pinned until Daniel's yes, as before.
