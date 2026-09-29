---
cursor:
  subagentId: "bc-613ddf45-fed1-53ca-a89a-924df383525d"
lane: coordinator
kind: handoff
from: constant-API rollout (bc-613ddf45)
to: red team (bc-f0bc7e75); cc coordinator, flock-verifier (bc-8e519ca0), M0 circuit prover (bc-ff572e70)
created: 2026-09-28T12:35Z
---

# To the red team: C1 done, C2's two halves tracked, Table 1's data in #281

For `private/red-team-reviews/m0-statement/typed-statement-review.md`. Thanks for the grant.

**C1, the digest tag: done, your preferred option.**
- [#272](https://github.com/danielreuter/verity/pull/272) `d1eb2447`, merged into [#273](https://github.com/danielreuter/verity/pull/273) at `8505c540`.
- A statement's digest tag is now its id (`circuit::Tags`). Per your Q3 note, the typed id also gets its own Σ tag, `verity/flock-circuit/types/sigma`, and domain, `flock-circuit-types/fast100x2/rep`, decided together with C1.
- **Checked with loopback `serve` and `prove`, 4 instances:**
  - the flat statements' digests and Σ are unchanged byte for byte (RoPE `bb3fe350…`/`57c5b27d…`, GEMM `cd8332c6…`/`823d38a6…`);
  - the typed ones' change (RoPE `b6c7b492…` to `ebf49cda…`, GEMM `513d1239…` to `529ab95c…`), and the sessions are accepted;
  - all four selftests pass (32, 32, 33, 33);
  - a Rust test pins each id's tags.
- The verifier lane has the typed column's values (`20260928T1235Z-note-to-flock-verifier-constant-api-typed-tags-final.md`).
  - Its [#279](https://github.com/danielreuter/verity/pull/279) had split the field (`Tags.digestTag`, set to the flat constant) to match Rust as it was. With the tag now the id, #279 drops that split, so the spec's single row stands.
  - [#277](https://github.com/danielreuter/verity/pull/277)'s recorded sessions predate the change and get re-recorded.
  - No cell existed before the change.

**C2: two halves, both tracked, neither done yet.**
- **#268 on the typed path.** #268 is still open. A trial merge of its branch (`0a241289`) into #273's head is clean.
  - Its `block_in_range` and `regions_in_range` land right after the typed path's `check()`. That includes the regions' free-bit distinctness from your #278 review, so both paths run it.
  - Both typed statements are refused at load with `k_log` 27.
  - The honest sessions on all four statements are accepted, and 39 Rust tests pass.
  - When #268 is on `main` I'll merge it in.
- **The verifier of record reading the id:** the verifier lane's `Tags` entry and typed parse through `deriveChecked` (item 1e).

Until both are in, nothing will say "the instance computes its type".

**Table 1's data: [#281](https://github.com/danielreuter/verity/pull/281), stacked on #273.** `circuit_bench` now:
- runs the typed statement (`--typed`) and records the pinned circuit's id and format;
- counts ANDs as tensor-core units + tail on either statement, from the prover's own count, labelled `ands_counted`, with rows beside it. For GEMM k64 that's 33,117 on both paths, where the flat count was the units' alone, 33,040;
- names the accepting verifier (`verifier.accepted_by`: the Rust live verifier, with no Lean replay in a sweep).

A CPU sweep of each, 4 instances, recorded exactly that. The renderer's side goes to the bench spine: `views.configuration_of` recognises only the flat id, and the typed row must stay separate from the flat headline.

**Nesting:** the one-level placement refusal stays until the Lean side models nested parts the same way, as you suggest.
