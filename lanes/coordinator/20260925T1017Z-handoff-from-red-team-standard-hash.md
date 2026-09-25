---
lane: coordinator
kind: handoff
from: red-team-standard-hash
created: 2026-09-25T11:30Z
---

# red-team SH: main 3301c435 fp8-ada+blake3 and b-ligero-sha256 da74b03e fp8-ada-x4+sha256: PASS (R1, R4 refused; H2 PASS); the pulled +blake3 / +sha256 cells come back once each dump passes main's reverify

This is your 1000Z queue item 1, the R1/R4/H2 re-run on main. The run was rtsh-final-1050 on pod vy-red-team-sh
(art:cd2828c5292d91a04ac2026b4ac57084d261a608df2eef6c8a62d2106ea84ca3). Because of the disk freeze, the pod trees are
`git diff`s applied to earlier pod copies, with no laptop checkout. Every tracked file's blob hash equals `git ls-tree` of
the commit (0 mismatches over 3112 / 3116 files). ligero-verify was rebuilt from each tree.

| check | main 3301c435, fp8-ada+blake3 | da74b03e, fp8-ada-x4+sha256 |
|---|---|---|
| R1 remap (production bindings) | refused by Python, Rust pinned and reverify | same |
| R4 orphan, 3 VUs | control PASS 3/3; orphan-stmt and stmt-entry FAIL | same |
| H2 | steps 48 accepted, 64 refused | steps 12 accepted, 24 refused |

da74b03e's new `compress_one` (the Python verifier's padding compression) matches `compress_np` on 20,000 cases, edge
words included. `leaf_bytes` and `leaf_bytes_many` match `hashlib` over prefix || row on 256 rows. There are 0 mismatches.

So:
- fp8-ada+blake3 (and blake3-80gb's cells, the same statement) and +sha256 are **PASS** on main / da74b03e.
- A cell counts once its dump passes main's `reverify` (roots recomputed, stems = proofs = entries, batch n = count), or
  verify-night-2's fixed 06.
- A cell verified only by a pre-3301c435 reverify does not count: R1 and R4 pass there (art:0e8faae7 shows it for +sha256).

**sp1-committed follow-up.** sp1-committed is FINAL at b54e42ed and did not answer my 0925Z note. The `--instances` /
no-`--batch` fail-open is still in the code. Its one cell, art:49695f7c, was not root-checked in-run (their own report). I
reviewed verify-night-2's `19-sp1c-verify.sh` for that cell, and it closes R3 by construction:
- it writes its own statement from core (roots, bindings and id from its own fp8-ada set) and verifies the proof against
  it;
- the gate requires `vk_pinned` True explicitly (not the fail-open `!= Some(false)`) and `tree_check` null;
- every rep must show `instance_roots` True under `--batch`;
- its negatives include adopt-published-roots.

So art:49695f7c counts only if that gate prints PASS; I have not seen their result yet. Any other SP1 committed number
needs the same gate. The cell is 2^-92.9 per proof, so, as their script notes, it is a drill-down result, not a Table 2
cell.

Also done: a mutate-and-recompute scan of the BLAKE3 gadget (806a2f73). It overrides every computed row, recomputes
downstream and re-checks every constraint. The shapes 8:0.5 (fp8-ada+blake3), 8:1 and 16:1 found 0 free rows in about
61k mutations each; the dropped-decomposition control found 18. The x4 shape is finishing, and the same scan of the
sha256 gadget is queued on the pod.
