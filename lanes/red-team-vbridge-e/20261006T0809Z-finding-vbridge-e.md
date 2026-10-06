---
id: red-team-vbridge-e/20261006T0809Z-finding-vbridge-e
campaign: proofs
lane: red-team-vbridge-e
kind: finding
status: final
repo: verity
origin: "pr:1289@34cefd872f740404f38aa308c721b64b5e2f7721 pr:1290@48998a034965896f7b00d51d05b64d3c43c6ee23 pr:1291@af17cb171a5324668e38223e9fa3102bb0da9380 pr:1292@c6d76f158e5ae3f14a48d2f56c857df17d3ee10f pr:1294@a1d1b469c6304dfc500ec41cc0a23706f8900fd4 pr:1295@df3fc037823696a21b94ee96347ee34cdb80a49e pr:1296@44e61ada296f479f2c2d6bc8bca52bc8cd954363 pr:1297@1e3a3db1bae6b80e6376e0274c79f606b2b0ef33"
---
# Red team, VBridge piece E (#1289 to #1297, V*'s algebra unit in Lean): GRANT, all eight; one merge blocker

Reviewed the night of 5 to 6 Oct, ending 1:15 AM PDT on 6 Oct, by red-team-vbridge-e (agent
bc-208c8878-5929-5d5d-bb58-687d6d9a9b6c) for the proofs coordinator.

- #1289 E0 `cursor/vbridge-algebra-structure-95d4` at `34cefd872`: **GRANT**.
- #1290 E1 `cursor/vbridge-algebra-sim-95d4` at `48998a034`: **GRANT**.
- #1291 E2 `cursor/vbridge-algebra-build-95d4` at `af17cb171`: **GRANT**.
- #1292 E3 `cursor/vbridge-algebra-eval-95d4` at `c6d76f158`: **GRANT**.
- #1294 E4 `cursor/vbridge-algebra-zerocheck-95d4` at `a1d1b469c`: **GRANT**.
- #1295 E5 `cursor/vbridge-algebra-lincheck-95d4` at `df3fc0378`: **GRANT**.
- #1296 E6 `cursor/vbridge-algebra-ringswitch-95d4` at `44e61ada2`: **GRANT**.
- #1297 E7 `cursor/vbridge-algebra-ligerito-95d4` at `1e3a3db1b`: **GRANT**.

Audit: r20261006-061444-3e11 (vy-nebius-2, CPU, its own clone and `.lake`, compare mode, kernel replay on) at `1e3a3db1b`.
`verity/Security` PASS: axioms only `propext`, `Classical.choice`, `Quot.sound`, no escapes, replay 6,794 constants; all
1,772 computed records and the `reads` section equal the committed ones; E's 24 new guarantees have `assumptions: []`.
`verity/Security/Proofs`: every Lean check passes (same three axioms, no escapes, replay 58,354 constants); its one failure
is the `runs` check `Proofs.Pouw.Bulk`, whose generator could not import numpy under node 2's `python3`. That check reads
nothing E changes, passed in r20261006-040139-db49 on a tree that differs only in `Flock/VBridge*`, and its generator
reproduces both pinned hashes locally. The first attempt, r20261006-055029-5533, failed cloning Mathlib from GitHub.
Each PR's `lean-audit.json` only adds the guarantees its body lists; no older record changes.

Evidence: art:1e990d2e77e65cd1c087855d11294cb4af996f7256d42843008805a9e03e5065 (Lean `#eval` probe of E's definitions
against `rec_algebra.py`: 181 comparisons, 0 failed); run record art:d7bf6c89ca4913d868d0acfbad019fee919405b117ab9a34e23779b953fd1b2f.
The full review is at the store's `private/red-team-reviews/1289-1297/review.md`.

Labels: `grant red-team --by red-team-vbridge-e --ref r20261006-061444-3e11` on all eight `pr:N@sha`, verified on the remote.

**Merge blocker (not soundness).** `main`'s `audit.py` now fails an anonymous instance (3b13c61bd), and
`Flock/VBridge/Algebra/Structure.lean` declares two (lines 160, 163). The fix: write `instance instValF128 : Val F128` and
`instance instValLin : Val Lin`, the names the records already read, so no record changes. Put it at the top of the stack
(E7's branch, or a small PR on it): an edit in E0 changes every stacked PR's own change and voids all eight grants for a
train, while one at the top needs one fresh grant on a two-line diff.

One-line notes, none a condition of a grant:

- Merges: each PR is a fast-forward of its base touching only `verity/Security/`; E7 onto `origin/main` (68e614869) is clean.
- Conformance: E's S, `w` layout, `v`, drawn points and residuals equal Python's at Shape(25,22,8), (35,24,8), (22,22,3) and `cons_structure(8..256)`, honest and perturbed.
- Non-vacuity: every premise of E3 to E7 holds at once at honest reps 0 and 1, the proof decoded by the verifier's own `decodeProof`.
- Stage conclusions are the verifier's checks: Piop.lean:85, :99, :146, :148; Opening.lean:80 to :88; `finalProg_of` is `finalProg_ok`'s converse plus the leftover-lists check.
- G: Opening.lean:69 and :75 (ring-switch and claim shapes) and Verify.lean:49 (every recorded round consumed) are verifier checks outside E's conclusions.
- F: E's `sh` must be Verify.lean:40's `Shape` (claims `2 + extras.size`, `fast100 m`, `digestLen`, `saltLen`), and `folded_size` needs `ts.size + 6 = st.c.kLog`.
- B2 bridge: E's `.wt i u` terms all have `u < 128` (the probe's maximum is 127), which `termVal`'s transpose reading needs as a lemma.
- Friction: note:red-team-vbridge-e/20261006T0809Z-friction-replay-audit-deps.
