---
id: 20260930T2359Z-reply-from-coordinator-l1-and-generic-lowering
campaign: verity
lane: proofs
kind: report
status: open
repo: danielreuter/verity
origin: old research coordinator (bc-8ece7cde), answering @proofs 4:51 PM PDT (Daniel: "L1 is not a real thing")
---

# L1, the generic lowering, and the path to a statement with no lowering assumption

All references are to `backends/flock/verifier/lean/soundness/` on main `e3ea0c9a`.

## (1) What L1 states today, and why it is proved only for RoPE

- **Statement** (`ASSUMPTIONS.md`, "L1"): *each template's rows compute its gates*. A template's pinned rows, when satisfied, carry on their outputs the outputs of the program's Boolean circuit, on every input. The audit certifies drawn units against their rows, so it says something about the program's Boolean circuit only through L1.
- **It is not a lowering assumption in the protocol's sense.** The lowering itself is proved generically, for every template (`README.md` §1.5, `lowering_sound`):
  - a witness satisfying a statement in which a unit's rows are placed in a block decodes to values on which the unit is correct;
  - the placement for the executable's statement is proved too (`placement_of_setupH`).

  L1 only relates the *rows* to a separate *gate circuit* (the unit's Boolean export).
- **Why only RoPE:** it is a per-template data check, and only RoPE's was run.
  - `GateRows.rows_sound` is generic: rows derived from **any** gate circuit and layout by the v2 lowering rule compute that circuit.
  - What is per template is `Rope.pinned_eq`: the pinned file's rows *are* the rows derived from RoPE's gate circuit. It is a kernel check (`decide +kernel`) in 18 chunks, about 3 min and 4 GB.
  - The other templates need their gate circuits and pinned rows as data, and the same chunked check (`python -m verity_flock.lean_rows`); nobody has generated them yet (`assumptions/l1-template-rows.md`).
  - Separately, and outside L1: that RoPE's gate circuit computes the IR's bf16 RoPE is tested on samples only (`test_ir_lowering.py`).

## (2) The generic form, and where it is written

Daniel decided on **option 1** at 09:19 on 27 Sep (done in PR #144):
1. The audit's circuit C **is the pinned rows the verifier parses**. A computed row is one gate, `Op.row a b = xorSum a v && xorSum b v`. A program's circuit is `Prog.circuit`, each unit an instance of its template's rows (`Prog.isRowsUnit`).
2. The lowering is proved **generically for every template** (`lowering_sound`), with no per-template proof.
3. "Each template's rows compute its gates" is named separately, as L1.

It is written in the store at:
- `internal/lanes/flock-soundness/20260927T0925Z-draft-rope-lowering-scope.md`: the options, with option 1's statement that "the claim that the pinned unit computes the IR's bf16 RoPE pair then sits outside the audit's soundness, as a property of C";
- `internal/lanes/audit-lean/20260927T0957Z-handoff-from-flock-soundness-rows-circuit.md`: C's definition, as agreed.

**Daniel's point now matches option 1's C.** The circuit is whatever the untrusted side put in the statement, and the lowering does nothing but read rows. What doesn't match is the documents: they still list L1 beside the soundness theorems as if the protocol needed it.

## (3) The shortest path to an end-to-end statement with no lowering assumption

1. **State the end-to-end theorem over C = `Prog.circuit` of the statement's rows**, as option 1 defines it. Acceptance then implies that the committed values satisfy C, by `lowering_sound` plus `placement_of_setupH` (`unitPlace_of_setupH`). L1 does not appear.
2. **Two opens remain on that path. Neither is an assumption about the lowering:**
   - `Layout.Aliased`: a unit's input columns on one gate carry one value, from the flat statement's copies (open, `README.md` §1.5);
   - joining the parser's reading of a unit (`Rows.ofNet`) to `setupH`'s unit net: the "link from `setupH`'s unit net to the derived rows" in §1.5's table, with the placement wiring (W6).
3. **Move L1 out of the soundness column and into a certificate about C.**
   - Per template: rows = `GateRows.rows(G)`, a kernel check like `Rope.pinned_eq`.
   - Then G ≡ the Definition's primitive, as an equivalence check per primitive piece or a proof.
   - It is a checkable fact about the chosen C, produced by the untrusted side and checked by anyone. It is not a hypothesis of the protocol.
   - `ASSUMPTIONS.md` and `README.md` §1.5 should say that. Changing them rewrites a named hypothesis in a Lean package, so it needs a statement reviewer under AGENTS.md.

**Is `HmRowComputes` the same kind?** It is the same kind of *fact*: particular rows (the `sha512x3`/`hm96` sections) compute a known circuit, SHA-512 / HM96, and it is checkable the same way (derived rows plus a kernel check). Its *role* is different:
- the commitments' binding and the coin commitment rely on those rows really being SHA-512;
- so it cannot be dropped by restating the theorem over C;
- it stays a named hypothesis until it is proved, and it is the natural second target for the chunked check after the templates.

## (4) Live coins and the batched session

- **Coins.** The non-ZK path (`flock-circuit.rs:470`, `cfg.coin_seed = true`) is M0's *live coins from a committed seed*, not fixed coins.
  - The verifier draws a 256-bit seed and nonce **from the OS** at step 0 and sends `SHA-512(TAG‖nonce‖seed)` in answer to `Hello`.
  - Every coin comes from the seed via `verity.randomness.derive`, and the verdict reveals seed and nonce (`live/src/coin_seed.rs`).
  - Coins are fixed only in a build with the `seed-injection` feature. `70-class-sweep.sh` builds that into `flock-circuit-selftest` only; the prove binary `flock-circuit` is built without it.
  - `--zk` (a statement with `hooks.zk`) switches to the coin tree: every coin committed at `Hello` and opened round by round.
  - **So for OS-random live coins:** use the release `flock-circuit` built without `seed-injection`, as today.
- **The batched serialized session:** `--session-tables J`, with 1 ≤ J ≤ 64 and default 1. The session's tables share one link exchange (`config_with`), and each table's two repetitions share one commitment root (R1).
  - `session_sound_of_table` / `session_knowledge_sound` (`Session.lean`) are the session bounds (Σ tableError; the extractor reruns the table), and `table_sound_exec*` (`Instance.lean`) the per-table bounds.
  - **The ask:** pass `--session-tables J` wherever the harness proves more than one table.
- **Timing I know of:**
  - The coins cost nothing measurable: one seed per session.
  - The loopback verifier's round runs in series with the prove. Tonight's K=2048 chunks were held about 6.5–7.3 s per statement beyond the 1.02 s prove (`note:20260930T2230Z-handoff-from-backend-sweep-2-whole-row-is-verifier-bound`).
  - Batching tables into one session shares round trips, so it should cut that per-statement wait. I have no measurement of by how much.
