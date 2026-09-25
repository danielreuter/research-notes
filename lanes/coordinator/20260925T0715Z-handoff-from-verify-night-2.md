---
lane: coordinator
kind: handoff
from: verify-night-2
created: 2026-09-25T07:15Z
---

# verified: RTX 4090 FP8 B-Ligero +hash (Poseidon2, alg.) art:71a37756 (before) art:abb219fa (after) + 3 intermediates; 20-run byte identity holds

hash-commit's 0612Z baselines (your handoff folder). All five full-tree results labelled `verified=accepted --by verify-night-2`:

| result | step | verdict |
|---|---|---|
| art:71a37756 | before, 6e1cc576 | art:9b700f03 |
| art:4be5c412 | step 1, 5d14dafa | art:7b57c75f |
| art:381bcee8 | step 2, 515ed32a | art:ae489182 |
| art:9fdb64e0 | step 3, 0b40ae8a | art:2cb926f3 |
| art:abb219fa | after, b862be30 | art:403784a7 |

Evidence bundle (binding, core roots, byte identity, negatives, steps): art:ad2bc9e1. All six preserved.

- ligero-verify built on my pod from main 7fcedf47 (sha256 d89cffc7, unchanged crate; hash-commit touched Python only).
  reverify PASS 5/5: custody 76/76, pinned fp8-ada+hash, 25/25 at 2^-128.50. Mode interactive, so this is a file
  re-verification that replays the runner's coins (not transferable).
- Statements BOUND to my tree's fp8-ada set: 25 statements, 0/4096 y words differ.
- The commitment roots were recomputed from my tree's instance set with the core only (`verity.commitments`: identity_digest bindings,
  rowleaf + poseidon2_babybear.hash_row leaves, MerkleTree): a c8c8746a, b 886cef1f, y 49023558. They equal the statements'
  auth block (all 25) and the commit evidence of all five.
- Byte identity across all 20 runs, the 15 slim trees included: commit-evidence.json 3df32610, evidence sha 247e44ca, rep-1 statements
  897697c9, system.bin c540b778, roots identical, and every file present equals its proofs.sha256 line. The claim holds.
- Negatives on the before and after trees: base accepted; proof byte, statement byte ("auth: y: multiproof rejected (root
  mismatch)") and swapped statements all rejected.
- Steps: main's Rust verifier already pins them (check_vu_shape, steps == the relation's steps, hashed K == 1536; steps-pin
  c5cf7f6d). I also checked the 25 statements myself: they carry (48, 1536), and 1536 / k 32 = 48.
- I left the 15 slim runs unlabelled. They carry no .proof files, so there is nothing to verify (F).
- Per the Amendment, these are algebraic-hash results and carry the mark in Table 2; they do not fill a SHA-256/BLAKE3 line.
