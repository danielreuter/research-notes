---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
lane: coordinator
kind: handoff
from: flock-netlist / M0 (bc-ff572e70)
to: flock-verifier, Lean (bc-8e519ca0)
created: 2026-09-28T01:10Z
---

# To the verifier lane: point the Lean verifier's tags and vectors at M0's PR (a), and drop the per-head ones

M0 is landing on `main` as two PRs (fix 6):

- **(a):** the circuit prover with inline reads, [#192](https://github.com/danielreuter/verity/pull/192), head `adcf38bf`.
  `check` is running, and I'll post the final head here if it moves.
- **(b):** the multi-table statement with private glue, [#193](https://github.com/danielreuter/verity/pull/193), stacked on
  (a).

Daniel's go is to merge as soon as possible. The coordinator asks that the Lean verifier's tags and vectors point at (a)'s
final head, and that the stale per-head tag entries and vector patches go.

**What I checked (so the change can be one tag set):**

- (a)'s `verity/flock-circuit` statement is byte-for-byte your `Tags.circuit967b8d06`:
  - `identityHm96 seedInjection (sha512Text := true)`, with `seed_injection` true only in the selftest build;
  - `sharedRows`, `bindings`, `hm96Rows` and `retainRounds`;
  - the pinned `leafSchemeHm96`;
  - coins `coin-commit/sha512`.

  From `967b8d06` to `73a273d4`, #83 changed only the writer's META (`program_digests` keyed by descriptor id, `e226a920`),
  the converge order and memory. `main`'s merge changed none of `circuit.rs`, the session or the identity.
- The red-team-classed Table 1 cells (`art:e352f2ad` attention, `art:a83371c2` GEMM) were recorded at `855fe81f`, which comes
  after `967b8d06`. So they are in the same tag set, and one entry keeps them verifiable.
- `circuit-vectors-967b8d06.patch` applies cleanly (`git apply --check`) to (a) at `adcf38bf`.
- Every template's circuit pin changed on (a), because train K's lowering makes smaller unit circuits. Regenerated vectors
  will carry new circuit files; nothing else about them changes.

**The change I'd suggest (yours to shape):**

1. **`Flock/Tags.lean`.**
   - One `circuit` named `"verity/flock-circuit"`, with today's `circuit967b8d06` values, plus `circuitSelftest`
     (`+seed-injection`).
   - Drop `netlistV1`, `circuit19c7269a`, `circuitFd02e847`, `circuit631567f7`, `circuitEb90718f`, its selftest variant,
     the old `circuit` (`e51e2b86`'s SHA-256 identity text) and the `@967b8d06` names.
   - `all` becomes those two.
2. **Vectors.**
   - Rename `circuit-vectors-967b8d06.patch` to `circuit-vectors.patch`, and regenerate `vectors.json`'s circuit sets once at
     (a)'s final head.
   - Delete `netlist-vectors.patch` and `circuit-vectors-{25519ba1,eb90718f,967b8d06}.patch`, and the old
     `circuit-vectors.patch` it replaces.
   - `ci-bundle.sh` gets one spec, `<(a) head>:circuit-vectors.patch:HEAD`. Update the matching lines in `agree.py`,
     `selftest_records.py`, the README and PROTOCOL §16.5.
3. **If you'd rather have no patch at all:** the generator can move into `flock-circuit` behind `seed-injection` in a small
   follow-up to (a). Say so and I'll put it up.

Please land it after (a) is on `main`, or stack it on #192. Tell me if you need the final head or a regenerated vector
bundle from me.
