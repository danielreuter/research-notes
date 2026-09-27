---
cursor:
  subagentId: "bc-c520c11b-172b-5758-a4c3-07b2e7956014"
---

lane: red-team-flock-3 · kind: handoff · from: one-stage-e2e · created: 2026-09-27T11:20Z · status: open · repo: danielreuter/verity ·
origin: your #116 review at 66ab031b (GRANT WITH CONDITIONS C1–C3), PR #116 @ 120adc37

# #116 delta check, please: `66ab031b` → `120adc37` (C1–C3, N1, and the five missing negatives)

- **Head:** `cursor/one-stage-e2e-6014` @ **`120adc37`**
  ([#116](https://github.com/danielreuter/verity/pull/116)). The delta is `git diff 66ab031b 120adc37`: `18a07a76`
  merges main `792704d7` (train C, which brings #135), then there are two commits.
  - `aa8aa59b` changes `protocols/one_stage`: `audit.py`, `registration.py` and the tests.
  - `120adc37` changes `benchmarks/one_stage`: `a0.py`, `a2.py`, `a3.py` and `pod.sh`.
- **C1:** `audit_record(..., served=)` refuses unless the served units equal the audited draw (check `served`).
  - With `--draw-file`, A3 now audits against the Lean draw itself (`split`) and passes the sessions' own draws as
    `served` (`a3.py`, the lines after `union = …`).
  - The A4 driver on [#143](https://github.com/danielreuter/verity/pull/143) does the same.
- **C2:** acceptance, and both profiles, now require at least one `of_record` verdict, and every `of_record` verdict must
  have run and accepted. `test_audit_record_needs_every_check_and_verdict` is flipped (Lean `None` gives no acceptance and
  no profile), and it adds "no verifier of record" and "verifier of record refuses".
- **C3:** `wrong_units_bound` is now `p.worst_case(lambda m: float(m))`; the bisection is deleted. The test
  `test_the_wrong_unit_bound_matches_worst_case_and_scales` is kept.
- **N1:** R4 is `rec["leaf_layer"] != leaf_layer`, so a null leaf layer is refused whenever the verifier holds one.
- **Also changed:** `audit_record(..., session_roots=)` refuses a session root that isn't the registered one (check `roots`).
  M0's verdict is now M0's alone; it used to fold `roots_are_registered` in.
- **Your missing negatives (a)–(e):**
  - (a) A3 `served-share-not-the-verifier's-draw (C1)`, which re-decides the real record with one served unit swapped.
  - (b) `verifier-of-record-did-not-run (C2)` and `no-verifier-of-record (C2)`.
  - (c) `session-root-not-registered`.
  - (d) `public-body-altered-leaf-layer-updated (Lean roots)`, in `a0.altered_public`. The public file's last output byte
    is flipped and the record's leaf layer is updated to the altered file's SHA-512, so R1–R6 pass. Lean `verify` then runs
    on the altered file with the real session.
  - (e) `registration-null-leaf-layer (R4)`.
  - (a)–(c) are `a0.audit_negatives`, used by A0/A1, A2, A3 and A4. (e) is in all four drivers.
  - Unit tests cover (a), (b), (c) and (e).
- **Evidence:**
  - Tests: `protocols tests/test_repository.py packages/verity/tests/test_boundaries.py packages/verity/tests/proofs`
    `tools/research/tests/test_pythonpath.py tools/research/tests/test_repo_replicas.py` gives 567 passed.
  - **A1 bound at `120adc37`,** `r20260927-110313-402a` (PRESERVED; stand-in RoPE, k = 256; M0 `e226a920`, Lean #142
    `712ae5f7`, `verity/flock-circuit@967b8d06`):
    - accepted and complete, with all 3 verdicts accepting;
    - at most 46 of 1,024 at 2⁻²⁰;
    - **21 of 21 negatives refused,** including (b), (c), (d) and (e). (d) is refused by Lean with R1–R6 passing.
  - **Tonight's records re-decided under the new rules** by feeding each run's `audit.json` inputs back to `audit_record`.
    All still accept, and every re-decided negative refuses:

    | run | bound |
    |---|---|
    | A1 bound `r20260927-075018-180a` | ≤ 46 |
    | A2 bound `r20260927-080759-2c1e` | ≤ 9,675 |
    | A3b `r20260927-081249-3764` | ≤ 37, with the served-draw check applied against its Lean split |
    | A4 P4 `r20260927-101433-97d7` | ≤ 158 |

  - **An A3b rerun at `120adc37`** (six templates, `--draw-file`) runs after A4 P6 on the same pod, so (a) runs end to
    end. I'll send its run id when it's done. The code and the evidence above don't wait on it.
