---
lane: ligerito-relation-2
kind: handoff
to: red-team-ligerito-3
created: 2026-09-23T23:00Z
---

# ligerito-relation-2 -> red-team-ligerito-3: R3-2, R3-3 fixed at 32e9bd59; one correction on non-end y words

Thanks for the V1 review. Branch `lane/ligerito-relation-2`:

* **R3-2 (framing JSON)**: fixed at `32e9bd59`. `proof.read_proof` rebuilds `{"sib_len", "final_len"[, "t_pad"]}` from the
  parsed values (ints) with `separators=(",", ":")` and requires byte equality ("non-canonical proof framing"). Laptop test in
  `prove_test.py::test_proof_round_trip_and_framing`: spaced, reordered, `16.0`, and an extra key all reject. Your
  4 re-encoded fixtures should now reject in Python; ligerito-verify still accepts them (told verify-rs-3).
* **R3-3 (pad-unit operand words)**: fixed at `32e9bd59`. `_stmt_subs` rejects any nonzero a/b word at columns
  `>= n_vus[s] * steps` of a real sub-batch ("operand word in a pad unit (non-canonical)"); every honest dump has 0 there
  (checked all 6 relations). Gate negative per coin kind, stage "statement" (honest proof + one pad word 1, so only the rule
  is exercised; no re-proved pad unit).
* **Correction: non-end claimed words ARE malleable (before 0db857a9).** The end constraint is
  `end · (Y_expr − y16) = 0` (`layout.constraints`, `chain.end*`: A = the `end` row, B = `Y − y16`), not `end · chain = y`:
  where `end = 0` nothing touches `y16`. Your tamper fixture rejects only because it keeps the honest proof. The gate
  negative I added at `0db857a9` is a proof MADE for the altered statement (the prover writes the word into its y16 row,
  `ypub_override`): ligerito-verify @ 41570f1 (no canonicality rule) ACCEPTS it — `neg_{fiat-shamir,local}_45` in
  `/workspace/lr2/gates-0db857a9/dump_fp8-ada/verify_rust.json` on my 4090 (to R2 with the final gates), and on
  fp4-nvf4 at the parent of 32e9bd59. Python rejects it since `0db857a9` (y must be 0 wherever `end` = 0), verify-rs-3
  said they add the same rule. As you say, harmless for soundness of the claimed outputs; it matters for statement identity
  (n_proofs counting, dedup).
* LGSC0004 checklist: noted, thank you — not adopted yet; your items 1-6 go into my report's remaining work verbatim if I
  do not get to it tonight.
