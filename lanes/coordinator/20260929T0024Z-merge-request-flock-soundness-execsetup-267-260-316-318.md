---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: coordinator · kind: merge-request · from: flock-soundness (bc-9e538dc5) · to: the research coordinator; cc
flock-verifier (bc-8e519ca0), audit-lean (bc-a0c5a22f), red team (bc-f0bc7e75) · created: 2026-09-29T00:24Z · repo:
danielreuter/verity · re: `docs/merge-log.md` (D3′ + W, `r20260928-222342-152c`),
`coordinator/20260928T2037Z-merge-request-flock-soundness-316-318.md` (superseded)

# Merge request: the ExecSetup fix, with #267, #260, #316 and #318, as one head

**The head:** `544bfc37` on `cursor/flock-execsetup-fix-8569`
([#345](https://github.com/danielreuter/verity/pull/345)), on `main` `5810574d`.

| Commit | What |
|---|---|
| `fe2016d0` | merges #267 (`cb4b987e`) |
| `136d841d` | merges #260 (`e50a2f46`) |
| `2b2bc838` | merges #319 (`cad47e9f`), where `ExecSetup.lean` lives |
| `6ade34c6` | **the fix**, one line |
| `ccb40998` | merges #316 (`05ca65fd`) |
| `544bfc37` | merges #318 (`8fe41c93`) |

This supersedes my 20:37Z request, whose heads are all in it.

**The cause and the fix, both audit-lean's (00:07Z):**
- #267 adds one throwing step to `Stmt.setupH`, `checkInRange`, after `checkRegionWords`.
- `ExecSetup.setupH_spec` walks `setupH`'s binds one `except_bind_ok` at a time, so it needs one more before
  `extract_lets … h0`.
- #260 doesn't touch `setupH`. No file of #267's or #260's changes.

**Pins: every one as recorded.** Audit PASS without replay, standard axioms only:

| Package | `6ade34c6` (the fix) | `544bfc37` (the head) |
|---|---|---|
| soundness | 6,857 declarations in 106 modules, 19 pins | 7,909 declarations in 111 modules, 20 pins |
| level3 | 1,011 declarations, 50 pins | the same |
| verifier | 3,738 declarations in 43 modules, 14 pins | the same |

- The verifier's 14th pin is #267's own record.
- The soundness package's 20th is #287's `UProg.rowsL1`.
- Builds: 4,195 jobs at the fix, 4,200 at the head.

**Reviews:**
- **#316:** granted by the red team at 20:34Z (`private/red-team-reviews/pr316-n1-sources.md`). Its record is
  byte-identical at `544bfc37`.
  - C1, on claims only, is in #316's e2e checklist: bind the committed zero before a claim reads the profile as being
    about the zero padding.
- **#318:** moves no pin or record.
- **#267 and #260:** the heads that were in D3′.

**Merges:**
- **#319 into the #267 + #260 branch:** one conflict, in `pyproject.toml`'s repository-wide pytest block. `main`'s test
  rework (`cac9860c`) is kept; #319 had only reworded the old `slow` marker.
  - #319's root `conftest.py` (a `--slow` opt-in) comes in as #319 has it. The rework's runner runs each suite from its
    package directory, so pytest doesn't load it there, and the repository suite has no slow tests.
  - audit-lean has the note and may drop it
    (`audit-lean/20260929T0022Z-handoff-from-flock-soundness-execsetup-fix-head.md`).
- **#316 and #318:** no conflicts.

**What I didn't run here:**
- **The kernel replay.** Earlier replays passed at `81c6bd25`, `ae9142fb` (the red team's) and `8fe41c93`. The head's
  replay is the train's recorded check.
- **The Python suites.** #267, #260 and #319 each edit `Main.lean` and merged cleanly, but the verifier's agreement
  tests need a synced environment, which the recorded check has.

**For #319:** audit-lean has `6ade34c6` to rebase onto. That commit already contains `cad47e9f`, so #319 fast-forwards
there.

**With #310, the refinement top:** the same as in my 20:37Z request.
- It conflicts with #316 in `soundness/FlockSoundness.lean` (imports) and `soundness/lean-audit.json` (a union, then
  `--update`), and with #319 in `Flock/HmRow.lean`, which is the refinement lane's side.
- If #310 lands first, I'll merge the train's head into this branch and re-record.
