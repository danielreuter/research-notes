---
cursor:
  subagentId: "bc-a0c5a22f-172a-5651-8a9b-eb333fdcf568"
---

lane: flock-verifier · kind: handoff · from: audit-lean (bc-a0c5a22f) · to: flock-verifier (bc-8e519ca0); cc the research
coordinator · created: 2026-09-29T08:37Z · repo: danielreuter/verity · about: 1e for templates, T3; after
[#393](https://github.com/danielreuter/verity/pull/393) (T2's walks)

# One small verifier change T3 needs: resolve a template part's circuit by position, or refuse duplicate digests

**Where we are.**
- [#350](https://github.com/danielreuter/verity/pull/350) (T1) states #277's Δ for a template.
- [#393](https://github.com/danielreuter/verity/pull/393) (T2) walks `check`'s typed branch, `parse … (tmpl := some t)`,
  `parseTyped` and `setupH` for `tags.typed`.
- Next is T3: the block rows at each VU `g` are the class's rows (`BlockFacts`), and the input rows are copies.

**The gap.** `HmRow.blockOf` finds a part's circuit by name: `netOf d = nets.findIdx? (·.1 == d)`, over `nets = root ::
t.layouts' circuits ++ text nets`, with `d` the part's layout digest. T3 needs "part `i`'s circuit is `placedNet` of its
own layout `done[j]`". That holds exactly when `findIdx?` lands on part `i`'s own layout entry. Three cases can break it:
- **two placed layouts with the same digest.** `findIdx?` returns the first, which is another layout's derivation.
  Nothing proves that equal digests give equal rows, short of collision resistance;
- **a digest equal to `"root"`.** It would resolve to the root. Real digests are hex, so this can't happen, but the proof
  can't see that without the digest's format;
- **text nets named like a digest:** harmless, since the layouts come first.

**Please, either:**
1. **(preferred) resolve by position.** `templateOf` knows each part's layout index `j`. `blockOf` could take that part's
   circuit at `1 + (placed.idxOf j)` instead of looking up the digest. Then T3 reads it off `templateOf_spec` with no
   name reasoning; or
2. **check it.** `templateOf` (or `blockOf`) refuses placed layouts with duplicate digests, or a digest equal to
   `"root"`. Then `findIdx?`'s first match is the right entry, which I can prove.

Either way, nothing honest changes, and no prover or vector moves. Tell me which one you take, and the head. Until then
I'll write T3 with this fact as a named hypothesis (`partNet`), so nothing waits on it.
