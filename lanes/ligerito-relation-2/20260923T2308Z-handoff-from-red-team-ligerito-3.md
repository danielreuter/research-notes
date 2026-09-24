---
lane: red-team-ligerito-3
kind: handoff
to: ligerito-relation-2
created: 2026-09-23T23:08Z
---

# red-team-ligerito-3 -> ligerito-relation-2: 0db857a9 / 32e9bd59 reviewed; R3-7 verify-session coin binding (BLOCKING for the live claim)

**R3-2 FIXED in Python (32e9bd59).** `read_proof` rejects all 8 of my framing re-encodings ("non-canonical proof framing":
the 4 FS fixtures `fixtures/framing_malleability_fp8-ada_e3ad950/` + 4 local ones). Honest fp8-ada, fp8-ada-zk (with `t_pad`)
and local proofs still parse. Duplicate keys, floats, booleans and missing keys also fail the byte-equality check. I ran
the committed `proof.py` with numpy only. Your framing negatives are a unit test (`prove_test.py`), not gate negatives, so the
Rust cross-check never sees one. Rust 60d9cbd1 still accepts all 4 FS re-encodings (batch exit 1). Please add one framing
re-encoding to the gate so `rust_batch` disagrees until verify-rs-3 adds the rule.

**R3-3 FIXED in Python (0db857a9 + 32e9bd59):** y off the chain ends must be 0; operand words in pad units must be 0;
`n_vus` needs zeros only at the end (`prove.py:1092`); `lay.S == stmt.S`; pad sub-batches carry no words.

## New

**R3-7 (BLOCKING for any live / interactive claim) verify-session does not bind the coins it replays to the verifier's
record.** `run.py:_file_coins` (32e9bd59 l.442-457) re-derives each slot as `expand_challenge(batch_context(stmt, ccom), k,
label, r_k)`. Here `ccom` and `label` come from the dump's own `stream_binding.commitments` / `.labels`. `verify_session`
(l.460-514) checks that the openings equal the record's, that the STMT digest matches, and that `rd["label"] == vc.labels[k]`.
But `vc.labels` are the labels the replaying verifier *asks for* (the protocol's), not `stream_binding.labels`. Nothing
compares `stream_binding.labels` with `rd["label"]`, and nothing checks that `commitments` has exactly the record's R
entries. So a prover can:

* send MSG k with the protocol label (recorded), get `r_k`, then derive its own challenge from
  `expand_challenge(ctx, k, L', r_k)` for any `L'`. That means grinding each round's challenge after the coin is open.
* or append an extra "commitment" (changes `batch_context`, hence every slot).

Both pass `_file_coins` and every check in `verify_session`, and the item is labeled `authenticated` with
`soundness_claim(..., "live", verifier_record=True)` (the interactive union, 2^-128.017). The actual soundness is the
Fiat-Shamir level: 2^g hashes per round choose among 2^g challenges, the same Q·ε as FS, ≈ 2^-64.66 at Q = 2^64.
Demonstration (pure Python, execs your committed `_file_coins` / `batch_context` / `expand_challenge` / `coin_commit` from
git): `backends/direct/ligerito/redteam_live_labels.py` on `lane/red-team-ligerito-3` 87fe4faa.

~~~text
honest                                  accepted, 0 slots differ from the issued coins
label grinding (slot 0: 16 zero bits)   accepted, slot 0 never issued by the verifier   (ground label "zc/r#5191")
extra trailing commitment               accepted, slots 0-5 never issued
control: random slot 2                  rejected "coin slot 2 is not the stream's"
~~~

Fix (one place): derive the slots from the record, not the dump. `ctx = batch_context(stream_stmt, [coin_commit(r, s) for
the record's coins])`, `slot_k = expand_challenge(ctx, k, rec["rounds"][k]["label"].encode(), r_k, 32)`, require equality
with the `.coins` slots and `len(slots) == len(rec["coins"]) == len(rec["rounds"])`. The existing
`rd["label"] == vc.labels[k]` check then closes the loop. Add a gate negative: an honest live dump with one
`stream_binding.labels` entry changed and `.coins` re-derived to match. It must come out NOT authenticated. Until then, no
live proof should carry the interactive claim.

**R3-8 (NIT) Python verify does not pin the statement's word widths.** `read_statement` accepts `word_bytes` / `y_bytes` in
{1, 2, 4}. `verify`'s shape check (`prove.py:1089`) compares l / steps / K but not `stmt.word_bytes == self.word_bytes`,
`stmt.y_bytes == self.y_bytes`. The same words re-encoded at 2x width are a second statement encoding. Rust rejects it
("statement shape", `lgto.rs:1162`). Fixture: `fixtures/stmt_tamper_fp8-ada_32d3d42/tamper_words_widened.*`, stage
'statement'. Also, `_udtype` raises `KeyError` on other widths, not `ValueError` / `Reject`.

**R3-9 (NIT) your negative 46 does not exercise the pad-unit rule in a verifier without it.** It is
`neg(..., _stmt_with(bt.stmt, a=a_pad), res.proof, stage="statement")`, the *honest* proof next to an edited statement. Only
45 is `neg_prove`d. Rust 60d9cbd1 has no pad-unit rule, yet rejects 46 at "zero-check round 1" (FS) / "combined final"
(local): the honest witness does not match the edited public rows. Rust feeds every unit's words into the operand rows
(`lgto.rs` `operand_rows`, `for j in 0..l`), so a proof made *for* that statement (pad-unit witness marshalled with the
word) would very likely pass Rust. Build 46 with `neg_prove` like 45, and check it is accepted with the Python rule
disabled. Then the Rust cross-check disagrees until verify-rs-3 adds the rule.

**R3-10 (NIT) verify-session's job claim trusts the dump's `n_proofs`.** `job_claimed_log2 = max(per) + log2(n_proofs)` with
`n_proofs = manifest["n_proofs"]` (prover-written). Nothing requires `n_proofs ≥` the number of distinct authenticated
statements, which Rust's batch mode enforces. Take it from the verifier's records (the sessions' `n_batches`), or at least
require `n_proofs ≥ len({stmt digests})`. The record dirs are also trusted as given. State in the claim that they must
come from the verifier's storage, and record their sha256.

## Addendum 23:14Z: R3-2 residual in Python (`"t_pad":0`)

32e9bd59's canonical check puts `t_pad` in the rebuilt JSON whenever the key is present, so a non-ZK proof whose framing is
`{"sib_len":[…],"final_len":N,"t_pad":0}` passes the byte-equality check. `t_pad` 0 means no `ybar`, and verify reads
`t_pad` from the absorbed params (`prove.py:1106`), so it parses to the honest proof. I checked this with your committed
`read_proof`: every dataclass field is equal, `absorbed_params()` is equal, the bytes differ. That makes it a second valid
encoding. verify-rs-3 2dfbb90a rejects it ("proof: non-canonical framing"), so the two verifiers disagree on these bytes.
Fix: emit and accept `t_pad` iff it is > 0 (the writer's rule, `proof.py:382-383`), e.g. `if framing.get("t_pad"):
canon["t_pad"] = …`, plus `("t_pad" in framing) == bool(params.get("zk"))`. Fixture (5 re-encodings of your 32d3d42 fp8-ada
FS proof, `expect: reject`, Rust 2dfbb90a verdicts recorded, 5/5 rejected):
`~/.research/notes/lanes/red-team-ligerito-3/fixtures/framing_malleability_fp8-ada_32d3d42/` (`framing_t_pad_zero.*` is the
one you accept today). Please make one of these a gate negative.

## Addendum 23:18Z: R3-10 (abort and retry)

A prover can open many sessions with the live verifier, abandon the ones whose coins don't suit it, and present only
the lucky one. `verify_session` looks only at the record dirs it is given. Per-proof soundness against such a prover is
N_sessions × ε, so the live claim must be a union over every session the verifier opened for that statement (aborted and
incomplete ones included), taken from the verifier's own session log (or the verifier rate-limits sessions per statement).
Same fix site as the `n_proofs` point: the verifier's records, not the dump.
