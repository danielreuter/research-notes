---
cursor:
  subagentId: "bc-35ab914e-d276-5d3b-bab0-9f87a3ef3847"
---

lane: vllm-config-run-tp2 · kind: handoff (first check answered; one record-field OK requested) · to: vllm-coordinator · cc: nebius-infra · created: 2026-09-30T16:20Z

# The committed weights root already supports per-slice openings, so the root doesn't change

**Answer: it is a Merkle tree, not a single digest.** `register_weights` (`commit/committer/native_host.py`) does the following:
- It hashes every parameter and buffer as `pos_leaf` leaves over 256-byte chunks of the tensor's row-major bytes.
- It folds each tensor's leaves into a tensor root, using the binary NODE/LIFT fold.
- It commits `weights_root = SHA256(TAG || geo || names_digest(names) || u64be(T) || fold(tensor_roots))` (`verity.commitments.vllm_v1.weights_root`).

A weight slice therefore opens against the committed root through two steps:
- its leaves open to the tensor root;
- the tensor root then opens in the fold of tensor roots, together with `geo` and the names list.

**Changes needed.** No change to the root construction, and no existing record digest moves. Only the Commit's output grows:
- The replay bundle must carry the per-tensor roots, the names list `[name, dtype, shape, nbytes]` and `geo_digest`. Today `self.weights` keeps only the root, so these are a bundle addition, not a record change.
- Some registered tensors are not in the checkpoint: the rotary `cos_sin_cache` buffer and engine scales. For these, the bundle carries their bytes, and the replay opens them against the same root, marked `source: bundle`. Every checkpoint-backed field is composed from the shards on CPU (`check/weights_of_record.compose`), marked `source: checkpoint`.

**Record-field proposal (OK needed before PR B lands):**
- Deferred records (the `--replay-deferred` Commit plus `row stage replay`) get a new field:

  `weights_attest: {pin: {equal, digest}, root_openings: "<opened>/<consumed>", sources: {checkpoint: n, bundle: m}, attests: "every weight slice the replay consumed opened against the committed weights root", replay: "cpu, from bundle <sha256>"}`

- In deferred records it replaces the in-process `weights_check` re-registration, which needs live GPU params.
- Non-deferred runs and old records are unchanged.

PR A (`--replay-deferred` and the bundle) doesn't touch the record, and its PR head follows in a separate handoff.
