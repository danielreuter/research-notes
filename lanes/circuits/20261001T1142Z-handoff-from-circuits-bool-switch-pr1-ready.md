---
id: 20261001T1142Z-handoff-from-circuits-bool-switch-pr1-ready
campaign: verity
lane: circuits
kind: handoff
status: open
repo: danielreuter/verity
origin: circuits-bool-switch
---

# @circuits (4:45 AM PDT): PR 1 is ready. `cursor/bool-switch-8c79` @ `734ed97bd` (on tr-T654), purity 0, replay 460/460; P9 fixed, the norms `_on_word` fix taken, no frontend ambiguity on this head. Body: store `internal/circuits/bool-integration-pr-body.md`

**The four runs**
- **Replay `r20261001-094921-0b4b`** (at `e272fb466`): 460 of 460 picks equal to the committed outputs on bits, and 0 mismatches.
  - The re-run at `04af3429f` (`4571`) was stopped by an outside SIGTERM at 153/460 (load average 529, empty stderr).
  - It runs again at the head as `r20261001-114003-c1ae`.
- **`--all` `r20261001-100328-ad35`**, plus its re-run at `04af3429f`, `r20261001-105519-3199`: 1,381 targets, 0 new failures, 1 known on `main`, and 0 unpinned.
- **Suites `r20261001-102007-6531`** failed at launch and ran no tests: `--extra torch-cpu` was resolved for `verity-check`. How the suites came out:
  - `verity-circuit-check` 26/26 at `eb8cb9169` (`ec0e`).
  - At `04af3429f` (`d1a3`): `verity-numerical` 1,052 passed. `verity-flock` 350 passed with 45 failures, every one `lake build` failing in the job's fresh source tree; `check` builds the Lean verifier warm. The rest of `d1a3` is still running.
  - The targeted tests at the head, now with vllm's lints, frontend and profile tests, are `r20261001-114024-d3bb`, still running. They replace `3d71`, which I stopped.
- **The `ir=boolean` Build `r20261001-101912-d566`** (at `23f2018c6`): purity 0, digest `85655c09…`, `sigma_check` ok. It stands for the head, because no Definition changed after it.

**Your 1122Z items**
1. **Fixed: P9 on `boolean_attention.py:222–230`** (`3d7377d13` and `c0d3eac72`).
   - The nine v6, v7 and v8 Definitions are built by `_on_bits(..., body, word)`, which constructs each `CompositeDefinition` and names its word view there.
   - The bodies are unversioned (`_fa2_*`, `_dot_*`, `_checked_*`). Without that, P11's `def-name` failed once `@composite`'s exemption was gone.
   - No allowlist entry. Digests unchanged: `test_boolean_attention`'s pins pass as they are.
2. **Norms:** I took `b376087ec` as is (`734ed97bd`, `_on_word` plus its test), and `test_boolean_norms`'s pins are unchanged.
   - `8a1a80f5e`'s `trace.emit` and the `boolean_norms.py` half of `2acad3c94` were already on this branch, and that file passes P9 as it is.
   - No `boolean_dense_norm.py`.
3. **Frontend:** the ambiguity is absent, so I didn't need to ask proofs.
   - Locally at the head, all vllm lints, 54 torch frontend and profile tests, and `test_frontend_rulings`, `test_derive` and `test_applicability` (62 tests) pass, and the vllm suite collects with no errors.
   - The ambiguity came from `boolean_dense_norm`'s import of `verity.ml.boolean.gemm` (proofs' `55fa55417`), which is not in PR 1.

**What the changes since the runs touch:** the attention v6, v7 and v8 chains (the replay's `Attention_v8` row and the attention targets of `--all`) and the norms' MUFU static check. Both were re-run locally; their digests are unchanged.

**What isn't done:** a full `check --record` on the head doesn't fit before 5:00, so the train's `check` covers it. The diff touches `backends/flock/` (proofs-ir-attn's `fp4`), so that check needs `lean-agreement`.

**Update, 4:47 AM PDT:** `main` reached `2f98a400`, so I merged `main` @ `d88650921` in with no conflict. The final head is **`443538fed`**; the diff against `main` is still the same 62 files, and `main`'s new commits touch none of them (`tc_probe_fp4`, `pearl_c4`, a new sm120 tc model). Core's Boolean and tc-model tests pass on the merge, except the ones that need fixtures this VM hasn't fetched. `c1ae` and `d3bb` run at `734ed97bd`, which differs from the head only by `main`'s commits.

**Update, 4:55 AM PDT:**
- `d3bb`'s **verity-vllm passed** at `734ed97bd`, with the lints, frontend and profile tests included. Core's half is still running.
- The head replays `4571` and `c1ae` were not killed from outside. Both used 24 workers in a 96 GB cgroup, filled it (25 OOM events, 1 OOM kill), and were then SIGTERM'd, at 153 and 130 of the 460 picks.
- The replay runs again at **`443538fed`** with 16 workers and 144 GB as `r20261001-115415-9980` (`0b4b`'s 12 workers took 57 minutes). I'll put its result in the body.

**Not in PR 1:** softcap (`cursor/bool-softcap-attn-e311` @ `0a2e6f7e2`; it has no circuit-check binding) and norms' dense chain (`cursor/bool-norms-8c79`, which goes into PR 2).
