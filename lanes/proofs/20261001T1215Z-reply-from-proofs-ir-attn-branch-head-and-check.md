---
id: 20261001T1215Z-reply-from-proofs-ir-attn-branch-head-and-check
campaign: verity
lane: proofs
kind: reply
status: open
repo: danielreuter/verity
origin: proofs-ir (bc-6cd83494), re note:proofs-ir/20261001T0730Z-handoff-from-proofs-750-is-a-deadline-not-a-stop
---

**Attention and FP8 on bits: `cursor/proofs-ir-attn-95d4` at `3b6653dda25fe0db3dd8f70dc0cdd6a44caa1caa`; its check
`r20261001-113404-2729` passed at 12:13Z (5:13 AM PDT), inside the 6:15 AM PDT bar.**
I don't open PRs, so this note is the handoff either way.

## Branch and checks

- The branch is stacked on the frozen IR head `46c768b2c` (on main since T525) plus proofs-mufu's `1fd5cb6c3`. A PR from it
  carries proofs-mufu's commits up to `1fd5cb6c3`; proofs-mufu's branch has moved on (`6ae4828f5`, `3bf1b6d02`).
- **Check of the head:** `r20261001-113404-2729` on vy-nebius-1, gpu 0, `check.py --record`, launched 11:34Z (4:34 AM PDT,
  inside node 1's window): exit 0, SUCCESS, validated, all ten steps passed (pytest 2,005 s, circuit-check 421 s,
  `lean-agreement` passed). Its `circuit-check --all` report: `art:2a0ec03a77d6b71a0be575bd5a23909d53bacdf858db466eb51516ba7c9eed29`,
  `ok` over 1,240 targets, 0 new failures, the one known failure `ScaledMmFp8Block_v1`'s recomputed scale product (a word
  Definition, already in `known`).
- Earlier heads on the branch, each passed (exit 0, SUCCESS, validated):
  - `r20261001-101835-c07f` checked `e79b4aee1` (scalar and FP8);
  - `r20261001-110037-1cbf` checked `35d147507` (superseded by the renumbering below).
- Local circuit-check reports for the two new attention roots at the head, each 0 failures, with the word view compared on 1,024 vectors and 0 mismatches:
  - `Attention_v8{T=17,NH=1,KVH=1,D=16,BN=16,DOT=HopperBF16WgmmaDot16_v2,INV=Fa2InvSum_v2,MASKED_FROM=1}`:
    `art:e3db624296a25a425acc9b4b362fe1c042339b7b593f1691d212b1e88ad5b1a1`;
  - `Attention_v9{…,INV=Fa3InvSum_v2,MASKED_FROM=1}`: `art:ad4a5482641e1ae4e58228049c783187a0f8dc415136aec7e12fd51003f69d75`.

## What the branch adds since the frozen head

- **Attention on bits** (`integrations/vllm/.../registry/boolean_attention.py`):
  - v6 is `Attention_v3`'s chain, and v7 is `Attention_v2`'s, with `DOT` and `INV` statics plus `Fa3InvSum_v2`.
  - v8 is `Attention_v5`'s: FA2's per-iteration `Check_inf`, the served FA2 rows' attention. It is circuits-bool-switch's
    `e272fb466`, cherry-picked as is apart from the word-view form and re-pinned on this tree's `mufu`.
  - v9 is `Attention_v4`'s: FA3's per-iteration `Check_inf`, where an unguarded block also scales by the unguarded max.
  - The v8 and v9 blocks, heads and attentions are pinned, agree with their word views, and are each controlled by a test
    that `CHECK` is read. A v9 that guards `max * scale` fails it.
- **`Gemm_v3`** and the E4M3, E5M2, NVFP4 and MXFP4 steps and coordinates on bits (core, `verity.ml.boolean.gemm` and
  `fp4`).
- **`verity.ml.boolean.scalar`:** `F32Add/Mul/Fma/Div_v3`, `F32Fabs_v2`, `F32Fmaxf_v2`, `F32Fminf_v2`, `Bf16ToF32_v2` and
  `F32ToE4m3Sat_v2`. C-Flock's `tail_pieces` imports the moved builders, and its export is unchanged (fingerprinted).
- **`verity_vllm` `boolean_fp8`:** the v2 of every FP8 linear composite: per-row, per-group and block-scaled quantize, the
  E4M3 dot and the scaled matmuls. Five circuit-check roots.
- The frontend's unversioned names skip Boolean Definitions, and attention's word views use no lambda patches (the P9 lint).

## For the merge

- **`Attention_v8` id:** this branch and `cursor/bool-switch-8c79` now define the same v8. The cherry-pick has the same
  bodies; only the word-view lines differ (`_view` loop vs `.word = lambda`). Merging keeps the loop. My earlier answer to
  `note:proofs-ir/20261001T0933Z` (does v6 cover v5?) is late. No, it doesn't, and v8 is the v5 chain on bits.
- **`MufuEx2Ftz_v2` differs by tree:** this branch has proofs-mufu at `1fd5cb6c3`; the switch has a later `mufu` (1,073
  ANDs). The id is the same and neither is on main, so whichever lands second takes the later `mufu.py` and re-pins
  attention's counts and digests, as the switch did in `1d456b4c7`. No id changes.
- **`F32Add/Mul/Fma/Div_v3` twice** (`note:proofs-ir/20261001T1006Z`): the circuits are identical. The switch resolved it
  with `scalar` importing them from `elementwise` (`23f2018c6`), and I agree: whichever lands second imports.
- **Tracer costs** (`note:proofs-ir/20261001T1025Z`): I haven't started them. `cursor/bool-trace-emit-f91f` already edits
  `trace.py` (`_body` -> `emit`), so they go after it lands, on top of it.

No `needs-daniel:` lines.
