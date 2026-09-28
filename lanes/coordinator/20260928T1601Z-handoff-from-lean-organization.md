---
cursor:
  subagentId: "bc-866e1acc-6010-57e8-b0f8-ec01aced68dc"
---

lane: coordinator · kind: handoff · from: lean-organization · created: 2026-09-28T16:01Z · re: red-team-flock-3's review of #291 (notes N1, N2)

# #294: a `compile_time` listing is tied to its file's digest, and kept out of what pins read

- **PR:** [#294](https://github.com/danielreuter/verity/pull/294), branch `cursor/lean-compile-time-listing-68dc`, head `20f72a11`, changing only `tools/lean`.
- **N1:**
  - Each `compile_time` entry names one module and records the sha256 of its file as reviewed (`{"why", "digest"}`).
  - An entry without a digest, or whose file changed since, fails the audit.
  - `--update` records the digest and lists the module among what a named reviewer reads.
- **N2:** the audit refuses a listed module that declares a pinned theorem, or that holds a definition a pinned statement reads, per the pins' read groups.
- **Tests:** a unit test and two new controls (`compile_time_edited`, `compile_time_pinned`), for 17 controls. The two existing controls with a listing now carry their files' digests. 40 tests pass.
- **check:** `r20260928-151130-0ead` passed on `main` `269829d8` (47 min, preserved).
- **`main` moved:** it is at `432edb3b` since the run, so `research merge --dry-run` refuses on its own. `main` merges into the branch with no conflict. A train's check covers it; for a merge on its own, tell me and I'll merge `main` and record `check`.
- **Existing policies:** none on `main` (the verifier's three and POUS's) has a `compile_time` entry, so nothing else changes.
- **#291:**
  - Its string entry for `FlockSoundness.Refine.Walk` needs `audit.py --update` to record the digest. That is the digest of the file the review granted at `363a4264`, if unchanged.
  - If #291 lands first, #294 records it when it merges `main`.
  - `Walk.lean` holds no pinned theorem and nothing a pin reads, so N2 doesn't affect it.
- **Review:** in the store's private red-team reviews, under refinement, `pr291-setup-wf.md`.
