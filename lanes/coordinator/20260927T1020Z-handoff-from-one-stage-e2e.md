---
cursor:
  subagentId: "bc-c520c11b-172b-5758-a4c3-07b2e7956014"
---

lane: coordinator · kind: handoff · from: one-stage-e2e · created: 2026-09-27T10:20Z · status: open · repo: danielreuter/verity ·
origin: your 09:35Z ask (freeze #116 for an independent review)

# PR #116 is frozen at `66ab031b` for review: A0–A3 and the canonical-partition binding; A4 moved to #143

## The head

- **Review head:** `cursor/one-stage-e2e-6014` @ **`66ab031b`**
  ([#116](https://github.com/danielreuter/verity/pull/116), still a draft; you mark it ready once the review grants).
- **Main is merged in** (`c309a1f6`, trains A and B, at `a96333a9`).
  - There was one conflict, in `pyproject.toml`; both member lists are kept.
  - `uv lock --check` is clean.
- **A4 moved to [#143](https://github.com/danielreuter/verity/pull/143),** on `cursor/one-stage-a4-6014`, whose base is this
  branch. Retarget it to main after #116 merges. It differs from #116 only in `benchmarks/one_stage/a4.py`,
  `a4_layout.json` and `pod.sh`.
- **There was no force-push.**
  - The four A4 commits (`887131e4`, `13706d9e`, `13241ce9`, `057d2285`) stay in this branch's history.
  - `dba33a61` reverts them, and the tree at that point equals `e569e84a`'s.
  - So the diff `main...66ab031b` has no A4 code, and a squash merge drops the history noise.
- **Commits after the split:**
  - `a82758c0`: marks `wrong_units_bound`'s direct Subset(k) bisection TEMPORARY, pending
    [#135](https://github.com/danielreuter/verity/pull/135). #135 is still open, so the workaround stays.
  - `fdbf0437`: A0 and A3 accept the template's `program_digests` entry keyed by descriptor id or display id. M0 `e226a920`
    re-keys it to descriptor id. The value is still checked against the verifier's own `program_digest`.
  - `66ab031b`: `tools/research/tests/test_pythonpath.py` pins the workspace's import roots, and this PR adds
    `protocols/one_stage` to them. Without this fix the merge gate would fail.

## What to review: the driver's checks (red-team-flock-3)

1. **Registration:** `registration.check` (`protocols/one_stage/verity_one_stage/registration.py:78-142`) runs R1–R6 against
   the verifier's own program, query, law, scheme, ports, leaf layer, anchors and log. `receipt` is at `:72`; `matches_public`
   (the public file against the record) is at `:145`.
2. **Draw:** `draw.check_draw` (`draw.py:35`) checks keys, law, population, integer units, ascending order, range and count.
   `check_proved` (`:66`) requires the proved instances to be exactly the draw, in order.
3. **Served-domain recompute:** `registration.served_domain` (`:51`) and its use in `benchmarks/one_stage/a2.py:96-127`.
   - The verifier builds the program and the canonical partition itself, and composes the bound circuit itself.
   - It recomputes every port's domain from the program, the partition digest, port, schema, leaves and run.
   - It then runs `R.check`, using its own SHA-512 of the public file as the leaf layer, before any draw.
4. **Negatives:**
   - `a0.py:302-362` covers A0 and A1: 12, 15 and 16 cases.
   - `a2.py:151-167` covers A2: 4 cases.
   - `a3.py:190-211` covers A3: 5 cases.
   - Most of them re-call a check with one input altered. Three kinds run end to end:
     - `wrong-output-word`: a tampered set goes through a full session, and both M0's verifier and Lean refuse it;
     - the Lean draw tests U1 and U3;
     - M0's selftest `prover-ignores-the-draw`.
5. **Acceptance:** `audit.audit_record` (`audit.py:98`).

## Points I'd like the review to rule on (disclosed, not changed under the freeze)

- **A profile can come out while the audit is incomplete.**
  - `accepted` needs every verdict that ran to accept. A verdict that didn't run (null) makes the audit `complete: false` but
    still allows a profile.
  - Only A0, from before Lean `verify` existed, was accepted with `complete: false`. Every A1–A3 run is complete.
- **The run label in the served domain is the record's.** The served domain binds the record's own `window.run`
  (`a2.py:119`). A different run label is refused (negative "domains-of-another-run"), but the verifier doesn't issue it.
- **R4 is skipped when the record's `leaf_layer` is null.** Every A0–A3 record sets it.
- **A2's N is the registration's.** It comes from the served index, not from the verifier's copy of #101's program, and the
  audit record says so.
- **`partition._descriptor_id` uses a private function.** It falls back to core's private `codec._spec_id` until
  [#131](https://github.com/danielreuter/verity/pull/131), still open, exports `descriptor_id`.
- **Stand-in versus served:** A0, A1 and A3 are on the stand-in commitment; A2 is served. Every registration's
  `window.kind` says which.

## Runs, all PRESERVED, and the commits they ran at

| run | commit | result |
|---|---|---|
| A1 `r20260927-061630-0645` | `9d74cde4` | stand-in; accepted, complete; ≤ 46 of 1,024 at 2⁻²⁰; 15/15 negatives refused |
| A1 bound `r20260927-075018-180a` | `6ccb9b7b` | stand-in, canonical partition bound; accepted, complete; 16/16 |
| A2 `r20260927-074743-5461` | `6ccb9b7b` | served; accepted, complete; ≤ 9,675 of 183,680; 4/4 |
| A2 bound `r20260927-080759-2c1e` | `bc86139d` | served, canonical partition `17478e85…`, units derived by Lean; accepted, complete; 4/4 |
| A3 `r20260927-064317-9536` | `64c0a320` | stand-in, 4 templates, N = 344; accepted, complete; ≤ 28; 5/5 |
| A3b `r20260927-081249-3764` | `66bd90a3` | stand-in, 6 templates with GEMM, N = 856; accepted, complete; ≤ 38; 5/5 |

**No run was made at the review head.** The one semantic change since the runs is `e569e84a`, which names templates by
descriptor id, as core's partition builder (#131) and the Lean verifier do.
- **A0–A2:** their partition digests are unchanged, because RoPE's statics are all integers.
- **A3 and A3b:** their digests differ at the head, because RMSNorm's float `EPS` and GEMM's `DOT` have descriptor ids that
  aren't their display ids.
- **Rerunning A3 at the head** needs M0 ≥ `e226a920` (descriptor-id `program_digests`) and Lean #142
  (`--statement verity/flock-circuit@967b8d06`).
- **A4's P4 audit** (`r20260927-101433-97d7`, now running on #143) exercises exactly that path, with this head's
  `protocols/one_stage`.

## Tests

- **Full suite, CPU:** 3,663 passed, 31 skipped, 14 xfailed. The only failures were the three `test_pythonpath` cases that
  `66ab031b` fixes; that file then passes 5 of 5.
- **Targeted:** `protocols tests packages/verity/tests/test_boundaries.py tools/research/tests/test_repo_replicas.py`: 82 passed,
  6 skipped.
- **Merge gate:** a passing `check` record at `66ab031b`, run by you as the merger.
