---
id: 20260930T1125Z-merge-request-lean-value-binding-513-526-after-tlo
campaign: overnight-sep30
lane: lean-value-binding
kind: handoff
status: open
repo: danielreuter/verity
origin: lean-value-binding (bc-a84aadb3)
---

# Merge request (Lean train, after TLO): #513 at 59671040, #514 at f3a60a36, #521 at 4e4ee3e4, then #526 at 04b94af7 (supersedes my 08:54Z #513 request)

**READY (12:14Z): all four heads are granted in both roles, and both of my recorded audits pass.**
- **#513 `59671040`:** re-granted 11:53Z (`lanes/red-team-flock-3/20260930T1153Z-answer-from-red-team-flock-3-513-regrant.md`).
  Recorded audit `r20260930-113409-9f35`: PASS, 11,753 declarations, 172 pins, standard axioms.
- **#514 `f3a60a36`:** granted 11:52Z.
- **#521 `4e4ee3e4`:** granted 12:07Z.
- **#526 `04b94af7`:** granted 12:07Z (`lanes/lean-value-binding/20260930T1207Z-answer-from-red-team-flock-3-514-521-526-verdict.md`).
  Recorded audit `r20260930-114448-9445`: PASS, 11,792 declarations, 176 pins, standard axioms.
- **Labels:** both runs carry `ov.ws`, `ov.metric`, `ov.value` and `ov.note`.
- **Order:** #513, #514, #521, #526, on `main` `f58d76d5` or later, merged in at train time. The red team says that order
  works.
- **Citation:** until #526 lands, the e2e bounds (with `_hm96` and `_classes_zero`) are cited only as "if A2 holds for every
  prover's finder". After it lands, cite them per prover.

**Order (lean-gemm-relation, 11:27Z): #513, #514 `f3a60a36`, #521 `4e4ee3e4`, then #526.** `a738857f`, `a19d2871`, `188e9e0d`
and `aa43e99b` are superseded and must not go into a train. **#526's `cfaa32f2` is superseded too.** Its new head,
**`04b94af77dea7ccdd7aca274c39fc0eb0fb05510`**, merges #521 `4e4ee3e4` (which contains #514 `f3a60a36`). The tree is
byte-identical to `cfaa32f2`'s, so the record is unchanged. Root pushed it from my bundle at 11:48Z (a fast-forward from `cfaa32f2`), so it is on origin. `main` has since moved to `f58d76d5` (TBV, no Lean), so merge it in at train time. #526 contains #513's head, #514 (`a738857f`) and #521 (`188e9e0d`). So if
#514 and #521 aren't landed separately first, landing #526 lands them too. Both of mine are on `main` `fb6a5cf8` and
merge into it without conflicts (`main` is an ancestor of both heads).

## #513: the rows' value binding and `registered_weights`

- **PR:** [#513](https://github.com/danielreuter/verity/pull/513), branch `cursor/lean-value-binding-8d81`, head
  `596710407bf048d1171eb0ded4386e5c184ed5e4`.
- **Since your 09:45Z note:**
  - `main` merged in (`fb6a5cf8`);
  - the red team's C2 and C3 in `eee9c27d`: fixed-address `row`/`salt` readers, and the registered-roots `δ_tree` caveat;
  - the record re-recorded.
- **Record against `main`:**
  - 11 new pins, byte-identical to the records granted at `655d509d`;
  - no existing pin record or definition digest changes;
  - the upstream watch gains `hm-row-computes`.
- **Audit:** `audit.py --update` PASS, 11,753 declarations, 172 pins. The recorded `audit.py --build` at the head is
  `r20260930-113409-9f35`, in flight; I'll label it when it passes. (`r20260930-112220-cd65` failed before building: the
  warm-dependency cache it copied from had moved. My fault, not the code's.)
- **Tests:** `tests/test_repository.py`, `tests/test_lean_packages.py` and `tools/lean/tests/test_upstream.py`: 25
  passed, 1 skipped.
- **Grants:** requested from red-team-flock-3 at 11:23Z
  (`lanes/red-team-flock-3/20260930T1123Z-handoff-from-lean-value-binding-513-regrant.md`). **Pending.**
- **Record size:** 533,072 bytes, under #520's 2 MiB cap.

## #526: A2 asked of the prover bounded (the red team's C1 on #511/#513, and `main`'s `flock_e2e_*`)

- **PR:** [#526](https://github.com/danielreuter/verity/pull/526), branch `cursor/lean-per-prover-cr-8d81`, head
  `04b94af77dea7ccdd7aca274c39fc0eb0fb05510` (on origin).
- **Change:**
  - `LinkCR` and `linkBoundCR`;
  - `flock_batched_linkSoundE` becomes `LinkSound linkBoundCR`, with no A2 hypothesis;
  - every `flock_e2e_*` (with `_exec`, `UProg` and `_hm96`) takes `hCR` only for `(reg σ, cont σ)`.

  The red team read the statements at `010b2c2d` (`lanes/red-team-flock-3/20260930T1006Z-answer-…-526-statements.md`):
  right, and C1–C3 met.
- **Record against #513's head:**
  - nine per-prover pins change;
  - four program forms from #514 and #521 enter;
  - no definition digest changes;
  - all 163 reviewed pins are byte-identical to what the red team read, plus #521's two.
- **Audit:** `audit.py --update` PASS, 11,792 declarations, 176 pins. The recorded audit at the head is
  `r20260930-114448-9445`, in flight.
- **Grants:** one combined request for #514 `f3a60a36`, #521 `4e4ee3e4` and #526 `04b94af7`, sent by me at 11:45Z
  (`lanes/red-team-flock-3/20260930T1145Z-handoff-from-lean-value-binding-combined-514-521-526.md`, also in the notes).
  **Pending.**
- **Record size:** 562,974 bytes, under the cap.
- **`lean-agreement`:** only the nested `soundness` package changes in both PRs, so the agreement key is `main`'s.
- **#514's head:** the red team said `a738857f`'s own record fails on `dependencies.mathlib`. #526 carries `main`'s value
  there, and #526's audit passes. If #514 lands separately, it needs its re-record first.
