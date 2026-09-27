---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

# Re-baseline epoch prerequisites (coordinator tracking)

The re-baseline epoch is on hold (Daniel, 2026-09-26; `docs/project-context.md`). This list is what has to be in place
before a claim can be made there.

## HM96 hiding leaves (`hm96-sha256/v1`, PR #88)

PR #88 is opt-in and off by default. red-team-hm96 granted it with conditions:
- **C1:** fail-closed on every commit path.
- **C2:** wording fixes.

**Merged 2026-09-26 22:10Z** as main `10726738` (PR #88 @ a53900df, confirmed as the merge commit's parent, with C1 and C2 met). It's still opt-in and off by
default, and the default path is byte-identical.

The re-baseline's prerequisites. E1–E4b must be done before hm96 hiding is claimed for rows of record or in Table 1; E5 is
circuit hygiene that lands with the same digest change:

| # | Prerequisite | Owner | Status |
|---|---|---|---|
| E1 | A setup claim for the pinned key: how it is generated and fixed, and what the hiding claim assumes about it | salted-leaves (PR #93, merged); the rest open | partly covered: PR #93 (merged) adds the `hash-derived-key` setup claim (hm96 §2a, the keys from SHA-512 counter mode over a public label). Anything left over is to be confirmed at red-team-hm96's review of #93 |
| E2 | A GPU hm96 kernel with padding, for the serving leaves at the committer's throughput | open | open |
| E3 | red-team-hm96's finding 6 applied in the Flock circuit | flock-netlist (sent by the root) | open |
| E4 | Data commitments (hm96 leaves and frame roots) on SHA-512, replacing SHA-256 (Daniel, 2026-09-26; `docs/project-context.md`) | salted-leaves (bc-60166fec) | **code merged 2026-09-26 23:12Z** (PR #93 @ 6338450b → main `2d5cbb8a`): `hm96-sha512/v1` and the frame-v3 and vllm-v1 SHA-512 framings, with their own identity digests on SHA-512. All opt-in, and the SHA-256 defaults are byte-identical: vectors unchanged, default leaves unchanged. **Left for the re-baseline:** switching the vLLM committers, Python and CUDA, to SHA-512 |
| E4b | The remaining SHA-256 dependencies, on 64-byte SHA-512 all at once: a fixed-width change with new vectors, since a mixed width would break the one-way parsing (salted-leaves, `lanes/coordinator/20260926T2320Z-handoff-from-salted-leaves.md`). (1) The IR identity digests `program`, `ctx` (context), `geo` (geometry) and `layout`, `domain_digest`, and the integration's `template` and `names` digests; (2) frame-v3's `binding`. These are IR content digests, so the switch belongs with the IR redesign at the re-baseline | TBD | open |
| E5 | Remove redundant gates within units. It changes program digests, so the default switch lands with the re-baseline and the IR redesign, when all digests move anyway. Until then the checker reports these as `redundant_gates` (32 on #101). (a) **The sampler, fixed directly (Daniel):** restate `GumbelTopPTokenSelect_v1` and `GumbelTokenSelect_v1` so `temp == 0` is computed once, bit-equal, opt-in until the re-baseline. (b) A general common-subexpression-elimination pass in circuit construction | (a) vllm-cross-call-check (bc-f7aadce6-d64c-5681-a2c7-47a635ef666c); (b) TBD | (a) code merged 2026-09-27 (PR #101 → main c822ca7a: `GumbelTokenSelectSharedGreedy_v1` / `GumbelTopPTokenSelectSharedGreedy_v1`, opt-in, bit-equal, no digest moves); the default switch waits for the re-baseline. (b) open |
| E6 | **Roots bind the partition digest** (Daniel, 2026-09-27; `internal/commitments-decisions-routing.md` §1). (a) Define the partition digest: a canonical description of a program's partition whose content digest names the program digest. (b) Replace `query_id` with it in `vllm_v1.semantic_root` and `SemanticDomain`, the integration's `commit/scheme.py` and `query/query_artifact.py`. (c) Move `verity.ir.partition.Level.query` to carry the family's partition digest; `verity.proofs.profile` levels follow. It moves digests of record, so it lands at the re-baseline | per the routing doc (partition checker for the levels); others TBD | open |
| E7 | **The code renames to the adopted terminology that touch serialized names** (conformance vectors, manifests, statement ids, recorded roots): they change only with regenerated vectors, at the re-baseline. Hold the non-serialized renames until the open PRs land too, to avoid conflicts. List: `internal/commitments-decisions-routing.md` (the renames section) | owners per the routing doc | open |

**Until E4b lands:** any Table 1 row citing the SHA-512 schemes (`hm96-sha512/v1`, frame-v3-sha512, vllm-v1-sha512) lists
SHA-256 collision resistance beside SHA-512's. The IR digests they bind are still SHA-256.

**Table 1, once flock-netlist ships SHA-512 proof trees:** state the proof trees' hash as SHA-512, with plain collision
resistance for arbitrary provers.

PR #88 is merged. Once E1–E4b are done, the switch lands with the re-baseline, committing whole rows of 1.5 KB or more
(`docs/project-context.md`).

## At the re-baseline: a fresh decision list

`docs/decision-previews.md` is parked (Daniel, 2026-09-27). At the re-baseline, bring back a fresh list of open calls, built
from current evidence and focused on Flock. Drop calls that only affect the frozen backends (A-GKR, B-Ligero, D-SP1, VOLE).

