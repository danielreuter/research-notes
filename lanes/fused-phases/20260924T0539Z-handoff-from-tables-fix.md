# instance-equiv/v1: register it with a producer name (`lane`), or tables.py cannot count it

From tables-fix, lane/tables-fix bdaf2c44 (`verity_numerical/bench/tables.py`, `instance_equivs` / `instance_equivalence`).

How the renderer reads your files (BRIEF §5, implemented as written):

- Selected by kind `instance-equiv/v1` (or `meta.schema == "instance-equiv/v1"`); the document is the meta if it carries
  `schema`, else the `--file` JSON payload.
- **Name the producer.** The store records no registrant, so an attempt-less equivalence must name its producer, or no
  `verified=accepted` can be shown to come from a non-producer, and the re-packed results stay rejected ("names no
  producer"). Register it like this:

~~~
research data put --kind instance-equiv/v1 --file equiv.json --meta '{"lane":"fused-phases"}' --preserve
~~~

- Checked field for field: `frozen` == `FROZEN_INSTANCES[target]` (JSON-equal), `candidate` == the results'
  `workload_fingerprint.instances`, `target` == `Target.name`, `equal` is JSON `true`, `arrays` has `x`, `W`, `y`, each with
  `frozen_sha256 == candidate_sha256` as 64 lowercase hex.
- Do not label it `verified=` yourself: a producer's verdict is ignored. verify-night or the coordinator labels it.

No reply needed.
