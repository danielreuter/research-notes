---
lane: verify-night-2
kind: handoff
from: b-ligero-standard-hash
created: 2026-09-25T09:58Z
---

# 3 more B-Ligero +blake3 RTX 4090 cells on main's GPU committer: fp8-ada+blake3 4096 frozen, fp8-ada-x4+blake3 4096 + 8192 plateau

This follows my 0905Z handoff. These cells were measured on tree **806a2f73**, which is lane/b-ligero-standard-hash with:
- main 94b1c4d2 merged (commit-gpu's device committer; device vs host `--commit-evidence` is byte-equal, r20260925-090404-6311);
- ligero-steps-pin's R1 / R2 / R4 fix merged.

The red team confirmed R1 / R4 / H2 refused on this tree (art:be211735…).

Settings for all three:
- `--zk --mode interactive --auth included-hash --commit-per-rep`, l = 4096, p2, 5 reps, rep 1 dumped;
- `blake3-keyed/row/v2` leaves, frame-v3 trees;
- pod ligero-verify sha256 e1ed499c….

Each is a bench-result/v1 with ref `run_files` = its proof tree (rep1/, system.bin, manifest.json, and the producer-side
rust_batch.json / rust_digest.json).

| Line | bench-result | proofs (run_files) | VUs | sub-batches | t.total | commit | e2e | VU/s | pinned sys | attempt |
|---|---|---|---|---|---|---|---|---|---|---|
| fp8-ada+blake3 (frozen, no sweep block) | art:e7d59ab6a7bad2140c776f1d160efa302f46439ea1ceda9edff68d228a6df022 | art:08225c8c209777cde883d544ed19b59704b2e9d3e8c60000137b5f2cdbfa1c4a | 4096 | 49 | 3.574 s | 0.011 s | 3.585 s | 1142 | 71f39e44… | r20260925-094242-269c |
| fp8-ada-x4+blake3 (no sweep block) | art:017a706919fd4f694ab7bfa25f63e3123a1fbd2ddd7b0bb0aff800cb447c2ae4 | art:0a95eb1e36bf2003501911d5d7983eb2c39a9356635994007ac60eab78ebc240 | 4096 | 13 | 2.038 s | 0.009 s | 2.048 s | 2000 | 1168788f… | r20260925-094821-b197 |
| fp8-ada-x4+blake3 (sweep plateau) | art:6b6d4484c7a3911946431ec8a7d3ef609137274157003e47654313d25be77631 | art:f35d43aa392b154f2af73bc41920ce1dc17c96b58d9ccd5a608aed9ebf7a453f | 8192 | 25 | 3.870 s | 0.015 s | 3.885 s | 2109 | 1168788f… | r20260925-091922-a390 |

The producer checked each one (not a label): Rust batch ACCEPT on every sub-batch, system pinned. The union bounds were
2^-128.40 (x1), 2^-128.33 (x4 4096) and 2^-128.05 (plateau), all against a 2^-128 target.

**Instances**
- The x1 cell carries the frozen fp8-ada set (`e66ff0f2…`).
- The x4 fold carries a relation-named manifest over the same numbers: `c86e51a1…` at 4096 and `5ca6851d…` at 8192. At 4096 it
  should count via fp8-ada-x4's instance-equiv/v1 file (kb/bench-instances.md). Please check that the file's digest is
  `c86e51a1…`; the `+blake3` suffix does not enter `instances_digest`, as far as I can tell. The 8192 plateau is n-keyed.
- The x4 sweep's other points hold no proofs: p0 art:0320e7a7…, p1 art:e8af8d31…, p2 art:b281a660…, p4 art:82a3e0ba….

**Verifier:** use reverify with R1 + R2 + R4 (ligero-steps-pin 06176b41 + 806a2f73). Pass `pinned` = the manifest's
`statement_relation`. Footnote per the coordinator (0915Z): "file re-verification (runner's coins), not transferable".
Measured with the old host committer, and superseded by the x1 row above as the headline: art:5d20ad00… (0905Z handoff).

A same-pod live-verifier run of the x1 frozen cell (verifier's own coins) is running: r20260925-095340-c456. A handoff follows.
