---
cursor:
  subagentId: "bc-8e519ca0-db91-5212-bb38-5b9865237ab3"
---

lane: one-stage-e2e · kind: handoff · from: flock-verifier · created: 2026-09-27T07:12Z

# The Lean verifier accepts M0's `e51e2b86` statements: PR #118 at `636dc78f`

**Build.** `cd backends/flock/verifier/lean && lake build` gives `.lake/build/bin/flock-verify`.

**Verify.**

~~~text
flock-verify verify --statement verity/flock-circuit --circuit circuit.txt --public pub-N.bin \
    --partition partition.json [--tables DIR] --session DIR...
~~~

- **Statement name.** `verity/flock-circuit` is `e51e2b86` in a proving build (`seed_injection: false`). Use
  `verity/flock-circuit+seed-injection` only for records from M0's selftest build.
- **`--partition`** is the verifier's own copy of the `verity/partition/v1` object:
  `{"format", "program", "query": {"name": "Q_word", "version": 1, "params": {"X", "W"}}}`. Its tagged digest must be META's
  `partition.digest`, and its `program` must be META's `program_sha512`. A circuit bound to the provisional unit cover takes
  no `--partition`.
- **Archive mode.** With `--archive DIR`, `--circuit`, `--public` and `--partition` are SHA-512 keys into `DIR/sha512/`.
- **Drawn sessions.** A session whose record carries `unit_draw` is verified against the drawn units' statement, derived
  from the population file and the draw.
- **Output.** One `VERDICT {"accepted", "session", "why"}` line per session. Exit code 0 means every session was accepted.

**What it checks beyond `eb90718f`.**
- META has `program_sha512` and `partition` in their SHA-512 shapes.
- Each `units.classes` entry equals the verifier's own class of the circuit.
- The partition object's form and tagged digest.

A mismatch is a setup rejection with a specific reason, for example "an instance's class is not this circuit's class" or
"partition digest is not the verifier's partition object's".

**Agreement.** On `e51e2b86`, RoPE at caller indices [3, 17, 40, 1001], 21 of 21 sessions agree with upstream,
including a drawn session (`vectors.json` set 10, `art:62afd0ae`, recorded run `r20260927-070106-614e`; the partition object used is
`art:62afd0ae/rope-head/partition.json`).

**Update, 07:25Z: open query names and the partition finding.**
- **Open query names.** PR #118 at `636dc78f` accepts a `verity/partition/v1` object with any query name. It checks the
  form (exactly `format`, `program` and `query {name, version, params}`; for `Q_word` v1 also `X` and `W`), the tagged
  digest and the program. An object without `format` is still refused ("the object's keys are not format, program, query").
- **The partition finding.** Every verdict now carries
  `"partition": {"rule", "query", "digest", "units", "note"}`. `units` is `"as stated"`, not `"derived"`, until the verifier
  decodes the program and evaluates the query itself, and `note` gives the reason. For `Q_word` v1 the note says the query is
  evaluable but the program is not yet decoded. For any other query, `Q_template_instance` included, it says the verifier
  does not evaluate that query. Please report `"as stated"` as a gap in the audit.
- **Agreement.** A `Q_template_instance` v1 statement: honest and drawn sessions agree with upstream (`vectors.json` set 11,
  `art:3f2298b6`).
