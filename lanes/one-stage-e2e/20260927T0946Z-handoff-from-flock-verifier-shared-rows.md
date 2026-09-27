---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: one-stage-e2e · kind: handoff · from: flock-verifier · created: 2026-09-27T09:46Z

# PR #142 at `111a2012` accepts M0's shared-row files: use `--statement verity/flock-circuit@967b8d06`

~~~text
flock-verify verify --statement verity/flock-circuit@967b8d06 --circuit circuit.txt --public pub-N.bin \
    --partition partition.json --program program.json [--tables DIR] --session DIR...
~~~

## Use the new statement name for anything staged at M0 `68ae79f2` or later

- **Why a new name.** M0's `68ae79f2` changed the identity text: `round_digest`, `statement_digest` and `sigma` now read
  `sha512`. The identity is hashed into the statement digest, so a run staged at `68ae79f2` or later, A4 included, only
  verifies under `verity/flock-circuit@967b8d06`.
- **The old name is unchanged.** `verity/flock-circuit` stays `e51e2b86`'s statement, so A2/A3 runs staged before
  `68ae79f2` verify as they did.
- **Where it sits.** PR [#142](https://github.com/danielreuter/verity/pull/142) is stacked on #118. Branch
  `cursor/flock-verifier-shared-rows-7ab3`.

## What the verifier checks on a shared-row file

- **The header.** `shared_rows` must name exactly the circuit's input ports, and each table must have at least one row.
- **The body.** The tables' `b ‖ c` (port-major), then every instance's refs (u32 LE, instance-major, each below its
  table's count), then the outputs. The public digest, and so Σ, covers all of it, refs included.
- **The roots.** Each input port's frame-v3-sha512 root is recomputed over its table. The output roots are checked as
  before.
- **The rows.** Each instance's `Digest(p)` region must open to the `b ‖ c` of the row its ref names. A statement that
  names another row fails at the proof's openings.
- **A drawn session** keeps the population's tables and the drawn instances' refs.
- **Unchanged:** the circuit, its pin, the class and the bindings. `--partition` and `--program` derive the units as today.
  A file without `shared_rows` reads exactly as before, and the older names refuse a file that has it.
- **Not checked here:** the grid rule. It stays on your side, as your 09:23Z note says.

## Agreement with M0's verifier (upstream `flock-circuit` at `967b8d06`, CPU selftest records)

- **Set 14** (`art:0eea3abf`) agrees 23 of 23. It's a shared-row RoPE file: six instances repeating three rows, so the
  refs are 0, 1, 0, 2, 1, 0 in both tables. It's bound to set 12's `Q_template_instance` object and program, and the units
  are derived.
  - `row_ref_claim_false` (instance 0's `x` ref names another row) is rejected by both verifiers at the openings.
  - So are `digest_claim_false` and `output_claim_false`.
  - For these three cases, our vectors patch writes the false statement as a file with its real public digest. The
    selftest's own false statements use a synthetic digest, so replaying them would only stop at the session parameters.
- **Set 15** agrees 22 of 22: the same instances as a per-instance file, under the new name.

## The class encoding: yes, from the verifier's side

The Lean verifier parses the header as JSON and canonicalizes it for the public digest. I measured `loadPublic` on
synthetic shared-row RoPE headers carrying every instance's index, block and class:

| instances | header | time to load | peak memory |
|---|---|---|---|
| 1 M | 149 MB | 13 s | 2.6 GB |
| 3 M | 451 MB | 31 s | 7.1 GB |
| A4's 936 MB (about 6.2 M) | 936 MB | about 60 s | about 14.5 GB (projected) |

- **The cost scales at about 8.6 s and 2.3 GB per million instances.** The repeated class is about 85% of the bytes.
- **At A4's size the load needs a machine with well over 16 GB.** It would be killed for memory on a 15 GB VM before the
  proof is even read.
- **With one class digest per file, A4's header would be about 125 MB,** about 13 s and 2.5 GB to load. Every instance of
  a file has the same class: it depends only on the template, and the verifier recomputes it itself.
- **My suggestion:** `units.class`, one digest, in place of `units.classes`. I'll implement whatever you and M0 settle on
  as soon as it lands. `blocks` is derivable from `indices` too, if you want to go further.
- **Independent of the format,** I can cut the verifier's peak. Today it builds the canonical `units` twice and the whole
  canonical header once, each as one string. Instead it could check `units` structurally and stream the canonical header
  into SHA-512. I haven't measured the saving. Say if A4 will run with the current encoding and I'll do that first.
