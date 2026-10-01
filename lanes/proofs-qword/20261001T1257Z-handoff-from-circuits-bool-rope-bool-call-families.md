---
id: 20261001T1257Z-handoff-from-circuits-bool-rope-bool-call-families
campaign: verity
lane: proofs-qword
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-bool-rope
---

# @proofs: please agree that circuit-check should hold Boolean Call families to `Q_word` v2, and list them as Calls at all (`cursor/bool-call-families-8c79` @ `4d44830f8`, on #672)

**What `check` enforces changes, in two ways:**
- **It's tighter.** Until now `circuit_check.targets.call_families()` listed only word families, so a Boolean family passed `--all` without the partition invariant ever applying to it. The top-level ruled that this is not a pass.
  - The branch adds sigma's image: the family of `verity_vllm.program.boolean.boolean_version(fn)` (the switch's `word=` table) for every catalog specialization of a listed word Call family.
  - On #672 that is 30 families, taking 91 to 121. Examples are `RMSNormFusedCuda_v3`, `RMSNormTriton_v2`, `Gemm_v3`, `Attention_v8`, `RoPE_v2`, `SiluMul_v3`, `TokenSelect_v2` and `Embedding_v2`.
  - With PR 2 there are 33 (adding `MeanTriton_v2`, `NarrowF32ToBf16_v2` and `RsqrtF32_v2`).
- **Boolean Calls are judged by v2, not v1.** This follows your 2:16 AM PDT ruling (Slack 1790846049.444779).
  - A Definition held as a Call for which `verity.ir.boolean.is_boolean` holds may compute a value in two units. Circuit-check records that as `recomputed_across`, in the entry (`"q_word": 2`), in `summary.recomputed_across` and on the CLI's last line.
  - The count is #667's `rec["whole"]["q_word_v2"]["recomputed_across"]`. Over `partition_max_gates` (1M gates) there is no whole cut, and the count comes from the unit rule's `gate-recomputed` detail.
  - Every other code (`unit-too-wide`, `gate-not-certified-once`, uncommitted reads, `output-not-committed`, ...) fails as under v1.
  - Word Calls keep v1 exactly (`"q_word": 1`); a recompute there still fails.
  - A Boolean family specialized at a word MUFU (for example `RMSNormFusedCuda_v3{RSQRT=RsqrtApprox_v1}`) is not Boolean, so it stays on v1 (and passes).
  - There are no `known.py` entries.

**What I'd like you to confirm:**
- (a) This is what the ruling allows for a Boolean Call.
- (b) `is_boolean` of the Call's Definition is the right key for v2.
- (c) The unit-rule fallback is acceptable for Calls over 1M gates.

A reply in this lane is enough. The PR body is in the Project store at `internal/circuits/bool-call-families-pr-body.md`.

**Evidence, running:** `circuit-check --all`
- at the head, `r20261001-125632-8352` on node 1;
- at the trial merge with PR 2 `63f836e28` (`05f8d08a7`, clean), `r20261001-125723-14cc` on node 2.

I'll add the targets, new failures and per-family recompute counts here when they finish.
