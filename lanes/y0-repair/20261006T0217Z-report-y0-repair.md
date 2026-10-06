---
lane: y0-repair
kind: report
created: 2026-10-06T02:17Z
status: final
---

CHECKPOINT 71b5ecaf9 (03:13Z) [final] #1264 @ 71b5ecaf9: 10 J statements' y₀ per-table, non-vacuity + regression pinned; audit r20261006-025822-376c PASS art:f4e68261; 10 records changed (binder only), 21 new
CHECKPOINT e9aa53d91 (02:59Z) [open] #1264 e9aa53d91: non-vacuity for the 10 J statements + whole-draw regression build (r20261006-025349-3b84); audit --update running r20261006-025822-376c
CHECKPOINT cef6316b0 (02:17Z) [open] cold build of cef6316b0 (r20261006-015138-4aae) at 4890/5292; non-vacuity (10 thms, tied to each binder), discharge over AcceptsZK, regression e2e_forces_mPts + 16/2/1 emptiness written; next: targeted build of the 3 new modules

## FINAL

~~~text
tip: cursor/zk-y0-pertable-95d4 @ 71b5ecaf9 (base main@7b410fbf6)        merge-with: none
known-failures: none    pod: none created (shared vy-nebius-1 only); $0 own
artifacts: art:f4e68261b8d230943242f893241f3101acab1b0fcbd823512175f62c04b18c66
~~~

#1264 at 71b5ecaf9 (fast-forward over cef6316b0): 642a0886d non-vacuity + discharge + regression, e9aa53d91 guarantee
listing, 71b5ecaf9 lock from the audit r20261006-025822-376c (PASS; run record art:f4e68261, review.txt and lock declared).
Changed guarantee records: exactly the 10 J statements (y₀ binder + implicit d₀ only); 21 new guarantees; definitions:
2 new (DrawSetupZJ/ZHJ.refused), 24 changed (y₀-taking plan defs in Composed.DefsJ, ZkHidden.DefsJ, ZkReg.BindHJ).
Builds: r20261006-015138-4aae (port, full), r20261006-025349-3b84 (new modules; targeted, outside the Lean slots).
Repository suite 45 passed at 71b5ecaf9. main has moved to c305471c5 without touching verity/Security; merges cleanly.
Open: accepted-session existence is a premise of every non-vacuity theorem; RecordsLiveZKJ, hU/hpub/hpt/hscope, hkd,
A3, count-curve params, TableCRZ, hdm/hKey stay hypotheses; the 10 changed records need a named statement reviewer; no
`check` yet. PR body: /cursor/stores/self/internal/proofs/y0-repair-pr.md. Scripts: lanes/y0-repair/tools/{build,iter,
audit}.sh; scratch tree /workspace/research/scratch/y0-repair-95d4 on vy-nebius-1 (this lane's .lake).
