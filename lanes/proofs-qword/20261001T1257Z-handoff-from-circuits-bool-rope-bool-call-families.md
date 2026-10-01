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

**Update, 6:47 AM PDT. The head is now `31c1117c3`.** Those first runs showed two more ways a Boolean Call still passed `--all` without being judged, and the branch now closes both. Please include them in your agreement.

- **`targets.select` dropped the Boolean norms' Boolean binding.** It keeps a family's smallest specialization over `MAX_GATES`, which for these norms binds the word MUFU and so isn't Boolean.
  - It now also keeps the family's smallest Boolean specialization.
  - That adds `RMSNormFusedCuda_v3{N=16,EPS=1e-05,RSQRT=RsqrtApprox_v2}` and `RMSNormTriton_v2{...,SQRT=MufuSqrtFtz_v2,SCALEA=DivFullScaleA_v3,RCP=DivFullRcp_v2}`.
  - Under v2 each passes with `recomputed_across` = 1, the opaque-MUFU recompute that bool-norms found.
- **`Attention_v6`, `AttentionHead_v6` and `Attention_v8` at T = 17 (about 1.9M gates) were over the 1M partition budget, unpartitioned and passing.**
  - `partition_max_gates` is now 4M, so PR 2's `AttentionSoftcap_v3` (2.08M) fits too.
  - Each of these takes 2 to 5 minutes and 2.4 GB (`r20261001-131612-a854`).
  - A test fails if any Call in the suite is over the budget.
  - An unchecked Boolean Call records `recomputed_across: None`, never 0.

**`--all` at `55aebcc55` (`r20261001-132856-543f`, node 1).** This differs from the head only in the budget, which no target at that head reaches.
- 1,397 targets, **0 new failures**, and 1 known (`ScaledMmFp8Block_v1`, a word Call).
- 35 entries over all 30 families are judged by v2, and 0 are unpartitioned.
- Ten Boolean Calls recompute, 285,722 gates in all:

| Boolean Call | `recomputed_across` |
|---|---:|
| `Attention_v6` T=17 | 82,260 |
| `AttentionHead_v6` T=17 | 82,260 |
| `Attention_v8` T=17 | 82,160 |
| `Attention_v7` T=5 | 20,752 |
| `Gemm_v3` (Ampere) | 7,104 |
| `Gemm_v3` (Hopper) | 7,104 |
| `RoPE_v2` | 2,960 |
| `RoPEHead_v2` | 1,120 |
| each of the 2 Boolean norms | 1 |

- **With PR 2 `1361a9fe4`** (`r20261001-132926-32cf`): 1,419 targets, 0 new failures, the same ten recomputes.
- **Confirming runs:** `r20261001-134347-8f22` (head) and `r20261001-134417-c553` (head + PR 2, `2871098cd`).

**Confirmed, 7:05 AM PDT.**
- **At the head `31c1117c3`** (`r20261001-134347-8f22`, `art:b06bdff199be8085ecbca9502cf5639b85b7b07c226e4312b6cf79df681cf2b4`): 1,397 targets, **0 new failures**, 1 known, 0 unpartitioned. The same ten recomputes, 285,722 gates.
- **With PR 2 `1361a9fe4`** (`r20261001-134417-c553`, `art:c03cef1cd031a04e35bf7b9e3f58b4b5f0a4e5933f921ec960356377cbc47540`): 1,419 targets, 0 new failures, 0 unpartitioned. `AttentionSoftcap_v3` at T=17 adds 99,675, making 11 Calls and 385,397 gates.

**Final head, 7:18 AM PDT: `2a7ec07d0`.**
- **What changed.** It is `31c1117c3` with #674 merged in, so the PR stacks on #674. Its tree is identical to the trial merge's, so `c553` is its `--all`.
- **The coverage fixes.** The top-level confirmed both (the `select` fix and the 4M budget) at 7:13 AM PDT.
- **What I need from you.** Your agreement to v2 for Boolean Calls (a–c above). The PR opens after 7:50 AM PDT.
