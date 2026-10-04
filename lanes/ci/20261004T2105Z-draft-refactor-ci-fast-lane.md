---
cursor:
  subagentId: "bc-81ff5c35-39a9-5232-a6b5-8e933b944292"
id: 20261004T2105Z-draft-refactor-ci-fast-lane
campaign: verity
lane: ci
kind: draft
status: proposed
repo: danielreuter/verity
origin: ci (bc-81ff5c35-39a9-5232-a6b5-8e933b944292, under bc-7f347b4b), moved from internal/hygiene/refactor-ci-fast-lane.md on Daniel's 4 Oct ruling
---

# Making the refactor land fast: what ci proposes

Written by ci (PR captain), 4 Oct 2026, 21:10Z, for the migration plan, `note:20261004T2058Z-draft-repo-organization-principles`.

## The problem in numbers

These are today's checks on node 1:

| Check | Wall | pytest | circuit-check | lean-audit | lean-suites | lean-agreement |
|---|---|---|---|---|---|---|
| `525e5c32d` (f68a, 26 PRs) | 83 min | 2,866 s | 2,896 s (0 of 1,682 hits) | 3,419 s | 976 s | 511 s |
| `06edf032c` (b98c) | 46 min | 2,318 s | – | 653 s (7 of 8 packages reused) | 1,188 s | 473 s |
| b201 (cold Lean audit) | 112 min | 2,429 s | 2,534 s (0 hits) | 4,155 s | 1,254 s | 1,222 s |

Steps run in parallel groups. The wall time is the longest chain, and today that's the Lean audit, then circuit-check and pytest at about 48 min each.

**What a directory move does to that today:**
- Every pass cache is keyed by input paths as well as contents, so a move makes the next check cold: about 85–115 min.
- circuit-check misses every time anyway, until #1126.
- After a move, every open PR touching the moved files needs a restack. Today, each restack round trip (I ask, the owner restacks, re-tiers and posts) took 15–60 min, and I sent about ten of them this afternoon alone.

The plan has about eight Python move trains plus the Lean moves. At about 100 min per cold check plus a restack wave each, that's well over a day of the pipeline.

## The recommendation: make moves cheap rather than skip checks

Skipping checks for refactor PRs looks fast but is a trap. This afternoon's failures were all *interactions* that only a full check catches:
- `test_wired_links` in afac, among the six Lean-side PRs;
- #1108's pins, broken by #1025 after both passed alone;
- #1044's test, which fails only on node 1.

A refactor makes exactly these interactions more likely. So the gates stay, and the work goes into making a pure move cost seconds instead of an hour.

### 1. Caches keyed by content, so a pure move is a cache hit (owner: ci, with lean and circuits)

- **pytest suites:** today a suite's key covers its declared inputs by path. Key instead on (path *relative to the suite's root*, blob hash) plus the suite's own config. A suite that moves as a whole then keeps its key, and so do its per-test passes. (ci; `tools/check/suites.py`.)
- **circuit-check:** #1126 (circuits) adds per-target keys, with 85–99.5% hits after a small edit. The keys should be blob hashes, not paths, for the same reason. (circuits; I'll review it for that.)
- **Lean audit:** the plan keeps module names across moves. If the audit's per-module records are keyed by module name and source hash rather than file path, a moved package reuses them. #1117 (tests and `*.md` out of the key) and #1119 (keep each package's `.lake/build`) are the start. (lean.)
- **Lake builds:** a moved package's `.lake/build` could be seeded from its old location, if Lake's traces hold hashes rather than absolute paths. That needs a test by lean before the first Lean move. (lean.)
- **lean-agreement:** reuse a pass when the built `flock-verify` binary and the pinned inputs hash the same as at the last pass. A move that doesn't change the verifier's code then reuses its 8–20 min. (ci, with proofs.)

With these, a certified move costs about a warm check: 15–25 min once the warm steps are as fast as they should be.

### 2. A certified-move lane (owner: ci)

A tool, `move-check`, certifies that a PR is a pure move:
- every changed path is a rename with identical content, or an edit in an allowlist of path-only files (`ci.toml`, `pyproject.toml` inputs, lakefile `require` paths, `tests/test_lean_packages.py`, AGENTS.md, skills, and import lines);
- the Lean lock is byte-identical (lean's validator already checks this).

A certified move gets the same gates, but the lander can run it at the front of the queue, at a quiet hour, with nothing else in its train. Nothing is skipped; the content-keyed caches make it fast. An uncertified "move" (one that also changes behaviour) is an ordinary PR.

### 3. ci resolves mechanical rename conflicts in the tip itself (needs a ruling)

Today, when a move lands, every open PR it breaks goes back to its owner for a restack. During the refactor, ci would resolve *pure rename* conflicts in the tip's merge commit, and the check of that tip covers the resolution. These are conflicts where the PR's edit applies unchanged at the new path, which Git's rename detection often misses when the file was also touched.
- A conflict that needs judgment (both sides changed the same lines) still goes to the owner.
- This cuts the restack wave after each move from hours to minutes.
- It changes the "owners restack their own PRs" convention, so it needs Daniel's ruling.

My recommendation is yes: for rename-only resolutions, with each one named in the handoff.

### 4. Scheduling (owners: lander, infra)

- One move per train, landed first in its window, then ordinary tips on top. Running two checks in parallel on node 1 worked today (525e and afac, then 9c9f).
- Node 1 caps check's Lean pool at 2 slots. The lean-audit wait was about 440 s of b98c. Raise the cap for move windows, and add node 2 for checks once the 235B Commit ends. (infra.)
- A move lands at a quiet hour with a heads-up to the lanes it touches, as the plan already says.

### 5. What I'd relax, and what I wouldn't

- **Relax:** none of the gates. The one real relaxation available is *when* the slow work runs. The Lean audit's kernel replay of unchanged modules could run as a nightly job instead of on every check, but only for modules whose source hash is unchanged since a replayed pass. That's lean's call. It saves most of a cold audit on a move.
- **Don't relax:** lean-agreement for anything that changes the verifier binary, the full pytest set, and `merge_requires`.

## Order

1. Now: land ci's check-time fixes (#1118, lean's #1079/#1085/#1117/#1119, circuits' #1126). Measure the next warm check against the 60-min goal line.
2. Before the first move: content-keyed suite caches (ci), blob-keyed #1126 (circuits), and a module-keyed audit with a Lake-seeding test (lean). Also `move-check` and the agreement reuse rule (ci).
3. Daniel's ruling on point 3.
4. Pilot on core's Lean move (the plan's pilot). Check it twice, cold and then warm, and compare.

## Open questions for other handles

- **architecture / top:** does the plan's move order allow one move per train, with ordinary tips between them?
- **lean:** can the audit key per module by name and source hash, and does a seeded `.lake/build` survive a package move?
- **circuits:** can #1126's keys be blob hashes?
- **infra:** can the check Lean-slot cap go up during move windows, and when can node 2 take checks?
- **Daniel (via top):** a ruling on ci resolving rename-only conflicts in tips.
