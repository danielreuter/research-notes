---
id: proofs/20261002T0535Z-finding-flock-protocol-md-trim-730
campaign: value-hiding
lane: proofs
kind: finding
status: final
repo: danielreuter/verity
origin: cursor/registered-values-95d4@51b2f5586
---

# Text moved out of `backends/flock/verifier/PROTOCOL.md` (PR #730, head `51b2f5586`)

The lander (10:28 PM PDT) found #730 merged onto the train tip `1c7d509e2` put the verifier's PROTOCOL.md 715 bytes over
the 128 KiB cap. `51b2f5586` trims 1,054 bytes, so the merge is 130,733 bytes. These lines left the spec. They are
evidence or test detail, not protocol; the vectors and tests they describe are unchanged.

Removed (the old text, as it stood at `c5680d024`):

~~~text
  and `sigma` read `sha512`. Set 14 (a shared-row RoPE file whose six instances repeat three rows) agrees 23 of 23 with
  upstream on M0's selftest records, `row_ref_claim_false` included; set 15 (the same instances per instance) agrees 22 of 22.
  The `967b8d06` vectors patch writes each false statement as the verifier's file (`<case>.pub.bin`) under its real public
  digest, so replaying those negatives reaches the proof's openings rather than the session parameters.
  - Set 13 (GEMM k1024, recorded on a CPU pod) agrees 27 of 27.
  against #131's `template_instance_vectors.json` (16 of 16: the population, the ranges, every unit's node, member and gates,
  the refusals word for word, the malformed parameters).
  may name `registered`, `{port: {value, positions, paths}}`: those tables' rows are rows of a value committed at
  registration. The verifier then needs its own `--registered F` (`verity/registered-reads/v0`: per port the value, its
  root, leaf count and domain, and the position each unit reads). Every table row's `b ‖ c` must open the root at its
  position (its `hm96-sha512/row/v1` leaf, climbed through its path), and every instance's ref must name the position the
  verifier's program reads for its unit, so the units must be `derived`: a position binds only as far as its unit does. A
  port one side names and the other doesn't refuses. Verdicts report `registered`.
  - **Tested** on #273's GEMM (`test_lean_typed_template.py`): of the prover's 20 recorded CPU selftest sessions, the
    verifier accepts the 3 honest ones, so its statement digest and Σ are the prover's, and it refuses the 17 negatives.
  refuses a row that does not open its registered root. Set 16 exercises it: fresh salts, rows committed afresh, a wrong
  position, no `--registered`.
~~~

What replaced them: "Sets 14 and 15 exercise it." (§16.10, shared-row files); "Set 13 (GEMM k1024) exercises them."
(§16.10, tail outputs); `template_query_agree.py` checks the decoding against #131's `template_instance_vectors.json`
(no count); "**Tested** on #273's GEMM (`test_lean_typed_template.py`)." (§16.11); the registered-reads bullet and D5
reworded shorter with the same requirements; `docs/region-word-check.md` (not in the repo) dropped from the region-word
check's citation.
