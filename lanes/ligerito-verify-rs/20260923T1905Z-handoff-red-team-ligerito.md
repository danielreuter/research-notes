---
lane: red-team-ligerito
to: ligerito-verify-rs
kind: handoff
created: 2026-09-23T19:05Z
severity: BREAK (ref.py dialect: `refpcs.rs` accepts forged evaluation claims; the proto dialect `pcs.rs` is not affected)
---

# BREAK: `refpcs.rs` (ref.py dialect) does not bind the statement into the transcript, so a prover picks z after the coins

`ref.py`'s `verify` starts the transcript with `absorb(root_1)`. The point `w`/`z`, the claimed `value` and `dims` (hence |S|)
are never absorbed, and `refpcs.rs` mirrors it (first absorb at `refpcs.rs:382`). Forgery: send level-1 sumcheck messages that
merely sum to a FALSE value, take the challenges `r`, then choose `z` so that `b(r)·<ra(z), v_1> = final claim`. That is one linear
equation in the last column coordinate of z. From then on every level is honest, and this works for any L.

Reproduced against your release binary (0254f65, built 18:53Z):

~~~
ligerito-verify ref-fixtures --file ~/.research/notes/lanes/red-team-ligerito/fixtures/weakfs.ref.json
weakfs.ref.json#redteam-weakfs/L1          accept   DISAGREES WITH ref.py      (expect.ok = false: these are forgeries)
weakfs.ref.json#redteam-weakfs/L2-radix3   accept   DISAGREES WITH ref.py
~~~

(ref.py accepts them too. "Disagrees" only because I labelled them expect-reject.) Generator: `backends/direct/ligerito/redteam_ref_weakfs.py
--dump F` on `lane/red-team-ligerito` @ 361a9de; run it with a python that has `blake3` (e.g. `ligerito-proto/.venv`).
`main.rs` says `batch` consumes `*.ref.json`, so this reaches the batch path as well.

**Ask:** version the ref dialect (`ligerito-ref/v2`) with a statement prefix before `root_1`: absorb `header(dims) || w (or z) ||
value`, the same as `pcs.rs`/proto (`header, z, root, v`). Do it together with whoever owns ref.py (handoff to ligerito-pcs-fast, same
time). Keep both fixture files as permanent must-reject regressions. After v2, the weak-FS pair must fail at the first sumcheck round.

**Second finding, where you are already right:** `refpcs.rs` rejects non-canonical words. ref.py does not, and that is a real
forgery, not malleability. Its round check `escale(c0, 2)` wraps int64 for a lifted `c0 + t·p ∈ [2^62, 2^63 − p)`. The transcript hashes `c0 mod
p`, so the coins don't move, and ref.py accepts `v − (2^64 mod p)` for a statement that IS bound before the first coin
(`redteam_ref_overflow.py`, `overflow.ref.json`: your binary rejects all three, ref.py accepts all three). So the `/noncanon` tampers with `expect_ok`
= true in ref.py's column encode a ref.py bug. Flip their expectation once ref.py is fixed.

Also: `ref-fixtures` accepts 8-query toy proofs, so the 0254f65 target default does not apply on that path. That is fine for fixtures, but say so in
its help text so nobody reads a `ref-fixtures` accept as a 2^-128 statement.

Full report: `~/.research/notes/lanes/red-team-ligerito/20260923T1830Z-report-red-team-ligerito.md` (F10, F11).
