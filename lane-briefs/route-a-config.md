---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

# Renderer fix: route (a) needs its own Table 1 configuration, or its verified cell renders as "weaker statement"

For the renderer agent (bc-150e) or tables-switch (bc-a6473c97). **Merge-ready by 00:15Z** (5:15 PM PT) for the 01:00Z switch
render. Base: `origin/main` (`1fdcc268` or later).

## The problem

The route (a) cell art:4b52879f (A100 BF16, 4,096 VUs, 16.67 s at the reference network) is verified by verify-night-3
(verdict art:317fe4b7) and labelled NON_ZK_PROOF by red-team-flock (21:40Z). The published render at 1fdcc268 still shows
the A100 · BF16 · frame-v3 · keyed-BLAKE3 row's A-GKR cell as `—`, with the footnote "results only for a weaker statement
(A-GKR CPU (Rust), A-GKR GPU (torch/Triton))".

`views.configuration_of` → `drilldown.classify(features(meta))` maps the result to the existing A-GKR GPU variant, whose
statement is "x, W private (unbound); y public endpoints". Nothing in `views.CONFIGURATIONS` describes route (a)'s full
committed relation.

## What to add

- A drill-down variant that recognises route (a) results: the A-GKR prime side plus the Flock session and link, e.g. from the
  result's live-verifier / link fields or its `derived_by` (`backends/gkr/tools/cell.py`). Choose a signal that the plain A-GKR
  GPU results don't have. It sits in the A-GKR family (FAMILY_NOTES already says so).
- A `views._cfg(...)` configuration, marked FULL:
  - statement: A-GKR prime proof of the relation, with the operands committed as keyed-BLAKE3 rows (`blake3-keyed/row/v2`)
    proved in Flock (flock-128-r2, live coins) and joined by the sigma link (two GF(2^128) points);
  - scheme `frame-v3/blake3-row`;
  - hashes: SHA-256 transcript and root_F, keyed BLAKE3 row leaves in Flock, SHA-512 Merkle on the A-GKR Ligero side;
  - soundness 2^-130.19 (A-GKR's interactive terms; Flock 2^-195.5; link 2^-243.9 / 2^-246.4); interaction live coins;
    class NON_ZK_PROOF;
  - assumptions: collision resistance is a Table 1 assumption (decision 57).
  Sources: PROTOCOL §17.5–17.6, red-team-flock's report (sections "Third/Fourth/Fifth audit").
- A test: a route (a) result renders in the A-GKR column of its line as a full-relation cell, and plain A-GKR GPU results
  still read "weaker statement".
- Re-run parity (`views --parity`: must stay ok, since the legacy rules ignore the new configuration) and the bench suite.
  Add a CHANGELOG line.

## After merge

The coordinator re-renders on vy-control-verity. The expected A100 · BF16 · keyed-BLAKE3 A-GKR cell is about 16.67 s at
4,096 VUs. If it can't be merged by 00:15Z, route (a) goes in the next publish, and the 01:00Z switch runs without it.
