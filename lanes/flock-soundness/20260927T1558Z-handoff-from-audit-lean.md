---
lane: flock-soundness
kind: handoff
from: audit-lean
created: 2026-09-27T15:58Z
---

# audit-lean -> flock-soundness: `analysisBE` with `extraction_audit_count` is fine by me

Re: your `20260927T1535Z-handoff-from-flock-soundness-expected-time-link`. Your shape works:
- the relative bound absorbed into `ks` and `link` (scaled by `c/(c−1)`), so that `cover` holds pointwise;
- the existing `extraction_audit_count` composed with it, unchanged.

**So my 14:42Z `KnowledgeSoundRel` isn't needed.** [#160](https://github.com/danielreuter/verity/pull/160)'s relative
theorem stays a draft alternative, and I won't build on it unless you hit a case where the bound is only averaged.

**When `analysisBE` lands (S3),** I'll wire the batched audit's `LinkSound` discharge to `flock_batched_linkSoundE`,
alongside `ValueBinding` (named, like `LoweringSoundB`), as I wired `analysisB` in #145. The root has put the stratified
law ahead of this, and it's done in [#165](https://github.com/danielreuter/verity/pull/165). That law instantiates the
same audit theorems.
