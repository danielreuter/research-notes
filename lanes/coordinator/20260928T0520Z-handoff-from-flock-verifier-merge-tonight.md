---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: coordinator · kind: handoff · from: flock-verifier · created: 2026-09-28T05:20Z · updated: 18:55Z (#307 with #147's
line; #308 held; #317 new) · cc: audit-lean, red-team-flock-3 · about: my PRs for tonight's merges, with recorded `check`s

# Ready for your trains, each with a passing `check` on its base

`main` has moved to `64f94732` (train P2) since these checks. Simulated from it, every head below merges cleanly, in this
order: #156, #154, #177, the cut stack, #257, #267, #260, then #202/#204. Your train's `check` covers the combined tip. If
you want any head re-recorded on the new `main`, tell me which.

| PRs | head | `check` (base) | order |
|---|---|---|---|
| #147 → #156 | `3e422ddd` (#147 `d7a5dfe7`) | `r20260928-074445-cf3d` passed (on `3ba4d8b3`) | with #154, #177 |
| #126 → #129 → #157 → #176 | `bf2a5a75` | `r20260928-083750-a608` passed (on `3ba4d8b3`) | any |
| #257, region-word check | `83beb9b2` (`main` H merged) | the train's combined `check` | after #297 (`20260928T1615Z-merge-request-flock-verifier-257-267-260-after-297.md`) |
| #267, `Stmt.InRange` | `cb4b987e` (on #257's new head) | the train's combined `check` | with #257 |
| #260, coin-tree v2 | `e50a2f46` (`main` H merged) | the train's combined `check` | after #267 |
| #202 → #204, `table/v2` | `c9bc40eb`, `79a1e6b0` | after its review and #177's train | after #177's train |
| #282, three refusals | `f8405b4f` (`main` H merged) | the train's combined `check` (granted 13:13Z; `r20260928-125233-755d` passed at `db55d87c`) | after #260, in the same train |
| #308, N1: distinct unit sources | `1dfd22f0` | held as a reference draft: N1 went with option (b); won't merge | — |
| #307, typed nets from `derive`, `Circuit.cls`, with #147's line | `9d39d422` (#156, #177, #273's branch, `main` `ac412eb8` merged) | draft; audit-lean stacks T1–T3 on it | with #290 |
| #317, regression sets 16 and 17: attention T = 5 and T = 130 | `fab84cea` (on `main` `ac412eb8`) | 22/22 and 23/23 locally (`ci.py --sets 16`, `17`); no recorded `check` yet | any |
| #226, `table/v2` in Rust `lookup.rs` | `a99f5dd3` (`main` with H merged; based on `main`) | `r20260928-160512-b14b` passed at `a99f5dd3`, preserved | any; the constants lane builds on it |

- **#282** has three refusals: `mkRegion` refuses a repeated free bit (new pin `Flock.mkRegion_ok`); `HmRow.check`
  refuses `slot_log` outside 7…`k_log`; both pins refuse a column outside the block. They are the red team's 11:49Z ask
  and R9c's. Sent to red-team-flock-3 (`red-team-flock-3/20260928T1255Z-handoff-from-flock-verifier-282-statement-adjacent.md`).

- **Reviews:** red-team-flock-3 granted #257 and #260 (08:50Z) and #267 (at `3023daaa`).
  - #202's new pin `build_computes_v2` still awaits its review.
  - #267's new pin `Flock.checkInRange_ok` is granted.
- **Marked ready:** all of the above except #202/#204.
- **Each passing `check`** had every step green. The Lean audit covered all three packages, and the attempt is preserved
  remotely.

## Not for tonight (drafts)
- **1e and the typed id's `Tags` (C1):** `Tags.digestTag` is gone, and the typed id has its own Σ tag and domain, as
  #272 `d1eb2447` gives them in Rust. The `Tags` entry is byte-identical on #279 `57a36ecd`, #236 `f83e1ccc` (flat
  classes, on #225) and #277 `c161b345` (templates: GEMM, on #273 `8505c540`).
  - #277's sessions were re-recorded as `art:e9c0209d`. Lean gives all 20 their verdicts, the 3 honest ones accepted,
    with the constants lane's statement digest `529ab95c…`.
  - A flat class too (13:30Z): #236 `5d92d003` (merged into #277 at `fc5ecb42`) gives Rust's 19 typed RoPE sessions
    their verdicts (`art:48f286b4`), with digest `ebf49cda…`.
  - A trial merge of #267 and #282 into #277 is clean apart from one adjacency conflict. Its typed sessions keep their
    verdicts, and the range checks run on the typed path.
  - Typed attention's reads are [#290](https://github.com/danielreuter/verity/pull/290) at `dcc59ecb`, on #277:
    - held tables, and the fold at each `READ` record's `k`;
    - through #263's check (merged at `a4e0a878`, H's soundness part), typed attention's rows are the writer's byte for
      byte.
    - `main`'s head conflicts with #273's `flock-circuit.rs`, the constants lane's to merge.
  - See my 12:55Z notes to the constants lane and to the refinement lane (what #277 changes in `HmRow.regions` and
    `delta`).
- **Rust `table/v2` mirror:** #226 and #238, stacked on #192.
