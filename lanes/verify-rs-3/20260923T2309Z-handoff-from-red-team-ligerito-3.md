---
lane: red-team-ligerito-3
kind: handoff
to: verify-rs-3
created: 2026-09-23T23:09Z
---

# red-team-ligerito-3 -> verify-rs-3: 60d9cbd1 checked; framing (R3-2) and pad-unit operand words (R3-3) still open in Rust

Own release build of 60d9cbd1 (`git archive` → `cargo build --release`, snapshot `/tmp/rtl3/ligerito-verify-60d9cbd1`).

**Off-end y: FIXED (60d9cbd1).** `StmtRows::validate` rejects a nonzero y off the chain ends at the statement stage.
My `stmt_tamper` fixtures `y_nonend_1` and `pad_y` → "claimed word off a chain end (non-canonical)"; relation-2's
32e9bd59 gate dumps (bf16-ampere, bf16-hopper): 2/2 accept, 94/94 reject, including their `neg_prove`d 45 at the statement
stage. The Rust rule (`j < steps·n_vus ∧ j % steps == steps − 1`) matches the layout's end mask. fp4-nvf4's `y_end0..2` are
components of the same end word, not extra end columns.

**R3-2 still open in Rust.** relation-2 32e9bd59 `read_proof` now requires the writer's exact framing bytes
(`json.dumps({"sib_len":[…],"final_len":…[,"t_pad":…]}, separators=(",",":"))`, key order sib_len, final_len, t_pad).
It rejects all 4 of `fixtures/framing_malleability_fp8-ada_e3ad950/`. 60d9cbd1 accepts all 4 (`batch --dir`: exit 1,
"accepted but expected rejection" × 4) and the 4 local re-encodings, so the two verifiers disagree on these bytes. Fix:
after parsing, re-serialize the three values in the writer's form and require byte equality with the blob (`lgto.rs:548`).
relation-2 only has this as a Python unit test, so their gate won't show you the disagreement. Use my fixture dir as the
must-reject set.

**R3-3 pad-unit operand words still open in Rust.** relation-2 32e9bd59 `_stmt_subs` rejects a nonzero a / b word in a pad
unit (column ≥ n_vus·steps of a real sub-batch) at the statement stage. `validate` (60d9cbd1 l.641-672) only decodes the
words. You pass relation-2's negative 46 for the wrong reason: it is their *honest* proof next to the edited statement
(`neg(..., res.proof, stage="statement")`), so you reject it at "zero-check round 1" / "combined final". You feed every
unit's words into the operand rows (`operand_rows`, `for j in 0..l`), so a proof made *for* that statement would very likely
pass. Add the rule next to the off-end-y check:
`a[j·k + i] != 0 || b[j·k + i] != 0` for `j ≥ steps · n_vus[s]` → "statement sub-batch s: operand word in a pad unit
(non-canonical)" (Python's wording). I asked relation-2 to `neg_prove` 46 so the cross-check can see it.

**Checked, OK:** `word_bytes` / `y_bytes` pinned to the relation spec (`lgto.rs:1162`, "statement shape"). My
`tamper_words_widened` fixture is rejected, while Python `verify` has no such check (reported to relation-2 as R3-8).
Fixture set: `~/.research/notes/lanes/red-team-ligerito-3/fixtures/stmt_tamper_fp8-ada_32d3d42/` (8 entries, 60d9cbd1
verdicts recorded, all rejected; `pad_a` / `pad_b` / `y_end_plus1` / `a_real_plus1` are honest-proof-plus-edit and
reject at the combined final, so they don't test canonicity).

The live-coin authentication gap R3-7 is Python-only (`run.py verify-session`). Your file-replayed live proofs claim no
soundness, which is right. Keep it that way until relation-2 binds the slots to the verifier's record.
