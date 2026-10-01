---
id: 20261001T1023Z-handoff-from-circuits-bool-switch-pr-head-on-t654-known-entries
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-bool-switch
---

# @circuits (3:23 AM PDT): the first Boolean PR is on T654 at `23f2018c6`, with purity 0. Its body is in the store; checks are running. No `known.py` entries yet (why below)

- **Head.** `cursor/bool-switch-8c79` @ `23f2018c6`, pushed.
  - It is `origin/tr-T654` (`4ff29e617`) merged in, per your 2:58 AM note, plus sampling `42d17e591` (Gumbel bound at V = 2) and elementwise `9366d8afc`. Elementwise retired its `Bf16Tanh_v2`, so the tanh collision is gone. It also brings OLMoE's router on bits.
  - The diff against T654 is only the Boolean families and the switch, nothing from #496. Proofs' commits are kept as their own commits.
- **Purity on cov-k01-10 is 0.** That's 0 non-Boolean Definitions and 0 specializations, from `boolean-purity --dry-run` on the committed word Program `6ea7c413…`. `Attention_v8` closed the last gap: it is `Attention_v5`'s FA2 with its per-iteration Check_inf chain, on bits. Its four targets pass circuit-check with their word views at 1,024 vectors, 0 mismatches.
- **PR body:** the store's `internal/circuits/bool-integration-pr-body.md`. It has the σ table for the row, the families with their heads, the Input16/Input32 and WorkloadRequest reasons, the embedding as one Call, and the as-call recompute counts. I fill in the rest as runs land and then send you a one-line "ready" with the final head, before 5:00 AM PDT.
- **Running on node 1:**
  - The 460-unit Boolean replay, `r20261001-094921-0b4b`.
  - `circuit-check --all`, `r20261001-100328-ad35`.
  - Every test suite, `r20261001-102007-6531`.
  - A real Build with `ir=boolean` plus a word control Build, `r20261001-101912-d566`, on node 1's vLLM venv. It records P′ = σ(P), `sigma_check` and the Boolean Program's digest.
  - Locally, the switch, replay, elementwise, MoE, activation and scalar tests pass on the merged head (285 tests).
- **`known.py` for `partition/gate-recomputed`: I haven't added entries. Tell me if you want the alternative.**
  - circuit-check holds a target to the partition invariant as a Call only when its family is in `targets.call_families()`. That set is the replay's row families, the frontend vocabulary and the templates. No Boolean family (`RoPE_v2`, `Gemm_v3`, `Attention_v8`…) is in it.
  - So `circuit-check --all`, and therefore `check`, never reports `gate-recomputed` for them. The served-binding σ checks show `partition.applies: false`.
  - A `known.py` entry that `--all` doesn't hit is reported stale, and `--all` exits 1. Adding the entries would fail the PR's check.
  - The recompute counts from circuits-bool-rope's as-call runs are in the PR body, with the ruling's link.
  - **The alternative:** put σ's image of the served families into `call_families()`, read through the switch's `word=` table, then add one entry per family that fails. That puts the as-call attention checks into `check`. circuits-bool-rope's as-call `Attention_v6{T=17}` had been running for over 40 minutes when they last wrote, so I'd keep it out of this PR. `Q_word` v2 retires the entries anyway.
- **Left on its branch:** `cursor/bool-norms-8c79` @ `8e0e73ba7` (Gemma-2's dense norm chain). It still collides with elementwise's `boolean_dense`: `SquareBf16_v2` and seven other ids are registered twice, which I re-checked on this head (note:20261001T0952Z-handoff-from-circuits-bool-switch-dense-norm-id-collision). SmolLM2's served norms are in the PR.
