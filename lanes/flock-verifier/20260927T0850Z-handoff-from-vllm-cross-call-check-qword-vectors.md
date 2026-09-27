---
cursor:
  subagentId: "bc-f7aadce6-d64c-5681-a2c7-47a635ef666c"
---

lane: flock-verifier (bc-8e519ca0) · kind: handoff · from: vllm-cross-call-check · created: 2026-09-27T08:50Z

# New Q_word v1 vectors for the Lean port: `qword_vectors.json` at #111 `cf0ad7a8`, including your random corpus

The independent review of #111 asked for vectors that determine the behaviour the port relies on. They're in
`packages/verity/tests/ir/qword_vectors.json` (`test_qword_vectors.py`), on #111's branch at `cf0ad7a8`. Programs are descriptor
bytes, each Call's graph is dumped in `partition_vectors.json`'s format plus `external` and `input_ids`, and everything is
evaluated from the bytes.

**What's in it:**
- **`constants`:** `wiring`, `wide_fan_in` = 4096, `width_rule` = [16, 32, 0], `param_max` = 65536. These are part of Q_word v1,
  and `cut.WIDE_FAN_IN` is now the query's own constant.
- **`evaluations`**, with per Call the graph, owner, units, kinds and committed set, plus the object, the digests and `locate`:
  - X packing at X = 16, 32 and 64 (5, 3 and 1 output units);
  - a wide gate beside a narrow control;
  - returned wiring inputs through all three wiring primitives;
  - a source read twice;
  - the dead-unit second pass;
  - the separable branches: a structure node, a scan, partial returns;
  - primitive root Calls.
- **`verify_refusals`, `served`, `object_refusals`:** every refusal code.
- **`corpora`: your conformance corpus.** It uses `qword_agree.py`'s generator at #129 `34b6fb0e`, copied verbatim, seed
  20260927. Each digest is the SHA-512 of `codec.canonical_json` of the list of cases, or of core's answers (your `expected()`,
  in order). Your per-case files are `json.dumps(case)`; canonicalise the list to compare.

| cases × max gates | units | cases SHA-512 | answers SHA-512 |
|---|---|---|---|
| 500 × 12 | 11,833 | `31d1d2bd5a634f772591882f9897d1cdb18c9fe59940e7e207c7bdba4f8dfe5a16d910f97efc195655aba99adb9c5a01090a12b54a8fbcd5bcd560cb655ae678` | `bbd9c508f908c6c5601696554c4b39c2fc164b129a1036957b5de27f64e7f7b785cf6c4260ba3a983f5bc895eb5d8abd81e005411eee963823bb8c410a303b9f` |
| 3,000 × 40 | 267,832 | `aa0581bbd0b6152c3d382fcd86a8edcd17400a559d908a62d72bc4fd125036df305fdcc5d656c7564ccce58a9466592eaee368c2ef15c21f263aa6e32ee1ac94` | `8fd5307ac70921b3b406587ddb8f6cf27c5f6c7cb59c31964ef51ab301834b71b3a68c60438c8766c484f20872d0b1561bd81ada6d4707547d4e7edfd1cb9672` |

**What changed that the port must follow:**
- **Applicability (step 0 of `cut.py`).** A root `batch` or `scan` makes Q_word inapplicable, and `verify` refuses with
  `query-inapplicable`. With #120, a Call in which a gate reads a later gate is refused the same way.
- **A primitive root Call** is one gate that reads its inputs and is returned.
- **X and W** are integers in 1..2^16.
- **`verify`'s check of served commits changed.** Details are in the store, private until #111 merges:
  `internal/red-team-reviews/pr111-partition-v1-review-response.md`, §B3.
- **The template queries (#131).** They now refuse with `query-inapplicable` too;
  `template_instance_vectors.json` is updated at `8e5fd38e`.
- **The format spec (#120, `456fac0d`)** has §8 and the vector `forward_reference` for the non-topological refusal.
