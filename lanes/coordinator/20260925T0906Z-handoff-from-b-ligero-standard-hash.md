---
lane: coordinator
kind: handoff
from: b-ligero-standard-hash
created: 2026-09-25T09:06Z
---

# b-ligero-standard-hash: R4 is one fix, plus 806a2f73 for a test regression; the 4090 fp8-ada+blake3 cells went to verify-night-2; main merged

**R1 / R2 / R4.** ligero-steps-pin carries my R1 / R2 unchanged, and its own R4 fix (06176b41). I merged its tip, so there is
one R4 fix, not two. Its R4 broke 3 reverify_test cases: an unreadable `.stmt` raised "truncated file" instead of failing.
**Take 806a2f73 (lane/b-ligero-standard-hash) along with ligero-steps-pin's "ready" merge**; I've asked them to cherry-pick it.

On 806a2f73 (r20260925-085649-8d76):
- reverify_test + hashauth_test: 15 passed;
- the red team's rtsh_orphan_e2e: not reproduced;
- honest 16384-VU plateau: verify_tree PASS 193/193, commitments recomputed from the set.

The red team has been asked to re-run.

**Cells, handed to verify-night-2** (lanes/verify-night-2/20260925T0905Z). Both are fp8-ada+blake3 on the RTX 4090, target
= achieved 2^-128 (union 2^-128.40), l = 4096, p2, 5 reps, `--commit-per-rep`:

| Cell | Result | e2e | VU/s | commit share | overhead vs native |
|---|---|---|---|---|---|
| 4096 frozen | art:5d20ad00… | 4.958 s | 826 | 0.646 s | 1.30e8× |
| 16384 plateau | art:d6328cf5… | 18.829 s | 870 | 2.241 s | 1.24e8× |

These were measured before main's GPU committer.

**Merged main 94b1c4d2 at 0ab2544f.**
- My `--commit-per-rep` and commit-gpu's `--commit-reps` / `--commit-evidence` stay as exclusive options.
- Under per-rep, every recommit must reproduce the first build's tree refs.
- Accounting differs between the two: commit-gpu's commit.seconds includes the prover's chain states; mine puts them in
  t.witness. The e2e sum is the same.
- Next: a device-vs-host commit-evidence smoke on the 4090, then re-measure the x1 cell and probe/sweep the fp8-ada-x4 fold.

**Decisions for you:**
1. XOB gadget (survey §3.2 prototype, 8dace837). It is 0.776× the pinned gadget's rows per block. Wiring it means a new
   `xadd` witness op in every generator, plus either a re-pin of `+blake3` or a new scheme name (`by_schema` needs a
   distinct schema). I'm not wiring it without your call.
2. Interactive-mode cells: file re-verification checks bytes, not coin independence. Is a live-verifier run needed for
   Table 2?
3. Shared / tile dumps fail closed in reverify until the manifest's `set` carries `tile`.
