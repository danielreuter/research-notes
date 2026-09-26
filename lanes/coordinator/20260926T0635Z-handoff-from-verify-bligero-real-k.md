---
lane: coordinator
kind: handoff
from: verify-bligero-real-k (bc-30d7a020-fc45-5944-9ceb-1ac513232a9e)
created: 2026-09-26T06:35Z
---

# verify-bligero-real-k: 16/16 real-K pins confirmed; art:be42c41a, c8cc8514, 67fb03cb and db9f01bf verified=accepted; reverify.py's entry point misses bench.cell dumps

- **Pins:** 16/16 of the lane-bligero-real-k PINS rows in `leaf.rs` equal the digests of my own compile from main 1b818427.
  - Checked with main's `ligero-verify system-digest`, twice: VM build and pod build (run r20260926-061022-eac8).
  - The binary pins each system to its own `<fold>-k<K>+<leaf>`, and Python's `system_id` and the Rust `at_k!` steps/tags agree.
  - `cargo test`: 38 + 8 + 27 pass.
- **Cells:** all 4 are verified=accepted, labelled by verify-bligero-real-k with ref r20260926-062503-d9c2 (PRESERVED). Each label
  carries a note, verifier, verifier_seconds and same_device=false.
  - I re-staged each input set myself: files match the manifest, the digest equals the cell's, every instance passes the IR
    evaluator, and each file equals the prover's staged copy.
  - main's `reverify.verify_tree` on my staged set: custody, PINNED, commitments recomputed, coverage, and a batch at ≥ 2^-128.
  - 5/5 live sessions per cell are accepted. Their system.bin equals my compile, and the rep-1 proofs, statements and coins equal the dump.
  - The session snapshot is art:948270a5. Negatives rejected 7/7.
  - Details: `lanes/verify-bligero-real-k/20260926T0553Z-report-verify-bligero-real-k.md`.
- **Not judged:** the interaction cell_problem (your 0437Z/0551Z decision). Per bligero-real-k's 06:22Z checkpoint these four get
  re-run and superseded. The re-runs need a fresh verification, which the same scripts in `evidence/` can do.
- **Tooling gap, for whoever owns reverify:** `python -m backends.direct.ligero.reverify <bench.cell result>` returns ERROR ("no
  proofs/ or dumps/ manifest.json") on every bench.cell result.
  - Cause: the dump sits at `meta.artifacts[0]` = `sweep/<point>/proofs`, and the entry point searches only the tree root.
  - `verify_tree` itself is fine. My `cell_check.py` locates the dir and calls it.
  - Fix: `reverify()` should try `meta.artifacts[0]` first.
- **Pod:** the verifier's CPU ran on an A4000 because no CPU pod existed in any DC. Terminated 06:31Z, about $0.10.
