---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

# Merge request: c4ir, IR analyses to core (phases 1+2), from vLLM coordinator bc-ecac3029, 18:20Z

**Merge the tree of `lane/vllm-rf-c4irc` @ `26964de2`, but through a two-parent commit (recipe below).**

## A history snag, and the recipe
`26964de2` is labelled "merge origin/main 38a8d35d into lane/vllm-rf-c4ir 793f14af", but it has **one parent**
(`793f14af`). Its tree is the correct merged tree; git just doesn't know `38a8d35d` is in its history. Merged as is into
main `b989a321`, it re-raises 14 conflicts (everything main changed since a4). With the same tree given its two real
parents, the merge is **clean**. On the merging machine (the lane is FINAL; neither my VM nor the control pod can push):

~~~bash
git fetch origin lane/vllm-rf-c4irc
M=$(git commit-tree 26964de2^{tree} -p 793f14af -p 38a8d35d -m "merge origin/main 38a8d35d into lane/vllm-rf-c4ir 793f14af (two-parent form of 26964de2, same tree)")
git diff --quiet 26964de2 $M && git merge --no-ff $M      # same tree as the gated 26964de2
~~~

## Recheck against main `b989a321` (a5 merged)
- Merging the two-parent form onto `b989a321`: no conflict. On the merged tree, every ratchet lint runnable without
  pytest passes (37/37).
- Since `38a8d35d` (the lane's gate (b) base), main added a5 (plus b5patb and backends). Within `integrations/vllm` and
  `packages/`, c4ir shares only `README.md` and the p07/p10/p11 allowlists with those changes, so the gates below carry.

## Evidence (c4irc handoff `20260925T1811Z-handoff-from-vllm-rf-c4irc.md`, READY `lanes/vllm-rf-c4irc/READY.md`)
- **Scope:** core `verity.ir` gains `intervals`, `liveness`, `boundary`, `partition` and `layout.resolve_gate`. The
  integration switches to them and deletes its copies, with no shims. `family_tiling` and `CheckedTiling` are public in
  core (owner morning-list item 1: public was the reversible default taken). Allowlists only shrink.
- **Gates** (all on `vyv-rf-c4ir-reg`, `--custody-r2`, preserved):
  - lints 45/45 at head and base (`r20260925-171611-f856` / `r20260925-171615-d852`);
  - gate (b): head `26964de2` against base `38a8d35d` on the same pod, jdiff rc 0, 0 new failures, skips or skip
    reasons. The 6 tests only in base are lint parameters over the deleted modules; 1 test is the listed-unstable
    weakref one;
  - gate (a) T0+T1 at `7313e799` (same subtrees): tests 1–130 from `r20260925-120631-fb6b`, killed at the 4 h default
    stage timeout with no JUnit, equal to base by position on the progress line (custody `r20260925-163128-6c84`). Tests
    131–158 from `r20260925-170630-1889`, with JUnit, equal to base test by test. That's 158/158. The first 130 are a
    positional comparison, not per-test JUnit; I accept it, because the outcome string matches base character for
    character;
  - core: the same single pre-existing failure at head and base;
  - GPU #101 = record (program `ccc21347…`, manifest `90f81868…`, run root `7adcef49…`).
- **Invariant:** no Program, manifest, commitment root, leaf id or verdict change.
- **Found, not fixed:** the 4 h default stage timeout in `research run`, which killed a gate (a); a core kernel
  self-check test fails on main with the integration on PYTHONPATH (pre-existing); store EAGAIN. Spend about $3.6 of $5
  (the raise to $5 was approved).

