---
lane: red-team-leaf-3
kind: report
created: 2026-09-23T22:25Z
status: final
---

CHECKPOINT 89cd6cf7 (22:54Z) [final] FINAL 23:02Z. NEW H1 BREAK (Ajtai n64 AND n128): pinned Rust verifier binds statement.steps to nothing (verify.rs:1077; steps<=n only a prover assert ajtai.py:425; system step-agnostic) -> at steps>n two different x rows give identical a/b roots, two different y, BOTH accepted pinned (n64 steps96: a=6528846c b=2c0d5ed3; n128 steps192: a=7e5165e4 b=cb891fd5), on ajtai-leaf-2 1cf9178 and ajtai-leaf-3 47d191e2. NEW H2 BLOCKING (shared): no leaf pins steps/K. G1 FIXED at ajtai-leaf-3 (chain_key). G3 PARTIAL (share-logup-3 777670ac relchain.py:1033-1035). F5/F7/F8 FIXED. BLAKE3 framing + share pair negatives + leaf-iface: no break. Fixtures evidence/fixtures/*, scripts lane/red-team-leaf-3 89cd6cf7; handoffs to ajtai-leaf-3, verify-rs-3, share-logup-3, blake3-leaf-3. Blocks integration: H1/H2 steps pin.
CHECKPOINT none (22:48Z) [open] 22:58Z. G1 FIXED on ajtai-leaf-3 47d191e2 (leaf3_g1_rust_only.py: Rust refuses B=0+decoys pinned AND --allow-any-system via chain_key; Python refuses too). H1 BREAK persists on ajtai-leaf-3 and is now a binding break e2e: leaf3_ajtai_collide_e2e.py commits two DIFFERENT x rows (cols 0 and 64 = P vs Q, steps=96>n=64) -> identical a/b digests+roots (a=6528846c, b=2c0d5ed3), different y (1193952256 vs 3331358720); PINNED Rust (sys_id 18d915 = pin) ACCEPTS both. Fix: pin steps per relation (or steps<=n) in Rust+Python verify. Writing FINAL + handoffs.
CHECKPOINT none (22:44Z) [open] H1 BREAK CONFIRMED e2e: ajtai-leaf-2 PINNED Rust verifier (system_pinned=true, sys_id 18d915 = fp8-ada+ajtai-n64 pin) ACCEPTS a proof with statement.steps=96 > n=64. Verifier never checks steps<=n (only a Python compile assert); the Ajtai system is step-agnostic so the pin still matches. At steps>n the negacyclic wrap X^n=-1 makes digest non-injective (leaf3_ajtai_steps.py: distinct rows, same digest, different GEMM product) => committed root does not bind operand rows. Evidence: evidence/H1_*. Writing up + handoff to ajtai-leaf-3.
CHECKPOINT dbe9be6 (22:34Z) [open] H1 (candidate BREAK/BLOCKING): verifier binds st.steps to NOTHING (verify.rs chain test + parse_v5 derive layout from st.steps; relation.rs has no steps/n bound; public_pins_hashed skips k_ops). Ajtai digest_rows steps>n has exact collisions (leaf3_ajtai_steps.py exit 0). steps<=n is a PROVER assert only (ajtai.py gadget), not verifier -> a malicious prover can present steps=96 vs pinned n=64. End-to-end proof against real pin not yet built (CPU/time). Next: blake3 malformed-frame, privacy notes F5/F8
CHECKPOINT 88a9b0d (22:27Z) [open] auth.rs multiproof + v5 derived table + v6 single-source digests: OK; BLAKE3 half-block parity from carried pos: OK. CANDIDATE H1: Rust never pins statement steps/K to the relation; Ajtai gadget column-uniform, steps<=n only a Python compile-time assert -> steps>n gives X^n=-1 cancellations: VU rows != committed rows with equal digest. Building PoC
CHECKPOINT 88a9b0d (22:23Z) [open] share-logup cfdcf65: Rust unchanged vs 1054caf; pair negatives FS 15/15 + interactive 17/17 pinned (G/H pins still match); G3 PARTIAL (pipelined path refuses live coins, unpipelined prove_vus still samples coins_h); F7 FIXED in Python+Rust; G1 at ajtai-leaf-2 1cf9178 NOT FIXED (pattern scan unchanged; PINS present so pinned mode refuses decoys). Next: auth.rs multiproof, blake3 frames
CHECKPOINT none (22:22Z) [open] started; briefs + red-team-leaf FINAL + red-team-leaf-2 report read; targets share-logup-2/3 cfdcf65, ajtai-leaf-2/3 1cf9178, blake3-leaf-2 1db0008 / -3 4d8668b, leaf-iface 720820d

# red-team-leaf-3 — adversarial re-check of the leaf code (share-logup-2/3, ajtai-leaf-2/3, blake3-leaf-2/3, leaf-iface)

No pod, laptop CPU. Question 1: can a prover make the verifier accept a statement whose operand rows do not hash to the committed
roots? Question 2: do the privacy notes state the real leakage? Findings continue red-team-leaf-2's numbering (G1 Ajtai decoy,
G3 live+shared coins); new ones are H1.. Severity BREAK / BLOCKING / NIT.

Predecessor red-team-leaf-2 left three crafted negatives UNCOMMITTED in its worktree
(`~/projects/verity-main-wt/red-team-leaf-2/backends/direct/ligero/redteam/leaf2_{ajtai_decoy,blake3_roles,share_pair}.py`); I carry
them onto `lane/red-team-leaf-3`.

## FINAL (22:55Z)

**Answer to question 1: yes, for the Ajtai leaves (H1, BREAK).** The pinned Rust verifier accepts a `fp8-ada+ajtai-n64` statement
with `steps = 96 > n = 64`. At that shape the committed Ajtai root does not bind the operand rows: two different x rows give
byte-identical a/b digests and roots, different y, and **both proofs are ACCEPTED by the pinned Rust verifier** (`sys_id 18d915…`
= the pin), on `lane/ajtai-leaf-2` 1cf9178 and on `lane/ajtai-leaf-3` 47d191e2 alike. Poseidon2 / BLAKE3: no way found to break
binding; they inherit the same unbound `steps` (H2). The same binding break reproduces on `bf16-hopper+ajtai-n128` at
steps = 192. **Question 2:** the privacy notes now state the real leakage (F5, F8 FIXED).

### Finding table

| id | target @ commit | verdict | evidence |
|---|---|---|---|
| H1 Ajtai `steps > n` binding break (n64 and n128) | ajtai-leaf-2 1cf9178, ajtai-leaf-3 47d191e2 | **NEW, BREAK** | `leaf3_ajtai_collide_e2e.py`, `leaf3_ajtai_steps_e2e.py`; evidence/fixtures/* |
| H2 `st.steps` bound to nothing (all leaves) | shared `verify.rs` | **NEW, BLOCKING** | code read + H1 runs (steps 96 and 32 both accepted pinned) |
| G1 Ajtai `check_system_key` pattern scan | ajtai-leaf-2 1cf9178 | NOT FIXED (pinned mode refuses through PINS; `--allow-any-system` accepts) | `leaf2_ajtai_decoy.py` |
| G1 | ajtai-leaf-3 62e3fdec / 47d191e2 | **FIXED** | `leaf3_g1_rust_only.py`: Rust refuses pinned + `--allow-any-system` |
| G3 live verifier + shared `coins_h` | share-logup-2 cfdcf65, share-logup-3 777670ac | PARTIAL | code refs below |
| F5 Ajtai "hiding" claim | ajtai-leaf-2/-3 | FIXED | `ajtai.py` privacy_note; `ZK_HASHED_NOTE` takes the leaf's note |
| F7 fingerprint_collision bound | share-logup-2 cfdcf65 (Python + Rust) | FIXED | `protocol.py`, `verify.rs`: n_op * (l // steps) slots, 3/2^32 coin bias |
| F8 `Proof.fp` leakage note | share-logup-2 cfdcf65 | FIXED | `ZK_SHARED_NOTE` discloses the linear information about private rows |
| share G/H pair (same commitment + coins, fp coin slot vs commit order, tile/VU-to-row, `--system-h`) | share-logup-2 cfdcf65 | no break | `leaf2_share_pair.py`: FS 15/15, interactive 17/17 as expected, pinned |
| BLAKE3 role key, half-block pairing, malformed-frame domain | blake3-leaf-2 1db0008 / -3 4d8668b | no break | `leaf3_blake3_frame.py` exit 0; half-block parity from carried pos (code read) |
| leaf-iface auth.rs multiproof, v5 derived table, v6 single-source digests | leaf-iface 720820d | no break | code read (22:27Z) |

### H1 (BREAK): the verifier never binds `steps`, and Ajtai binding needs `steps <= n`

* **Mechanism.** The Ajtai chain is `acc <- X acc + B s_col` over `F_p[X]/(X^n + 1)`, so the digest is `sum_j X^(steps-1-j) B s_j`.
  For `steps > n`, `X^n = -1` folds column `j` onto column `j + n` with the opposite sign. At `steps = 96, n = 64`, columns `j < 32`
  and `j + 64` cancel when they hold equal content, and different content there leaves the digest unchanged.
* **Why the pinned verifier accepts.** `steps <= n` is only a **prover** compile-time assert (`ajtai.py:425`, in the gadget). The
  gadget template is column-uniform, so `hashchain.compose` gives the same system and the same `sys_id` / table digest (the pin)
  for any `steps`. The Rust verifier takes `steps` from the statement (`verify.rs:1077 let steps = st.steps;`). The chain test,
  public table, auth check (`verify.rs:1232`) and `check_config` all derive from it, and no pin compares it to the relation
  (`relation.rs` / `leaf.rs PINS` hold only `(sys_id, table_digest)`). The new `chain_key` (G1 fix) is step-agnostic too.
* **Crafted negatives (committed on `lane/red-team-leaf-3` 89cd6cf7, `backends/direct/ligero/redteam/`).** Run on the ajtai-leaf-3
  tree with its Rust binary:
  * `leaf3_ajtai_steps.py`: `digest_rows` collision (two distinct rows, one digest, different dot product), exit 0 for both roles.
  * `leaf3_ajtai_steps_e2e.py --steps 96`: honest machinery with the prover assert removed (`K_VU = 3072`; nothing else is
    changed). The PINNED Rust verifier gives `accepted = true, system_pinned = true`, reading statement.steps = 96. With
    `--steps 32` (below the canonical 48) it is also accepted pinned.
  * `leaf3_ajtai_collide_e2e.py`: sets P and Q differ only in VU 1's x row (columns 0 and 64 = content P, or Q != P). Both sets
    give a-root `6528846c…` and b-root `2c0d5ed3…`, identical a/b digests, and y_final 1193952256 vs 3331358720 (y-roots differ).
    **Both proofs are ACCEPTED by the pinned Rust verifier.** A verifier holding (root_a, root_b) accepts two different outputs
    for them.
* **Fixtures** (must-reject, requested by the coordinator's 22:50Z handoff to ajtai-leaf-3):
  `~/.research/notes/lanes/red-team-leaf-3/evidence/fixtures/{fp8-ada-ajtai-n64-steps96, fp8-ada-ajtai-n64-steps32,
  fp8-ada-ajtai-n64-collide/{P,Q}}/` (system.bin, sub_00.stmt, sub_00.proof, verdict.json).
* **n128: also demonstrated.** `bf16-hopper+ajtai-n128` (16 words per column) at `steps = 192 > 128`: accepted pinned
  (`sys_id 29f18689…`). Collide variant (columns 0 and 128): both sets give a-root `7e5165e4…` and b-root `cb891fd5…`, y
  differs, both accepted pinned. Fixtures: `evidence/fixtures/bf16-hopper-ajtai-n128-{steps192,collide}/`.
* **Fix.** Pin `steps` (or K) per relation next to `(sys_id, table_digest)`, and refuse any statement whose steps differ, in both
  Rust and Python verify. Unpinned (`--allow-any-system`) Ajtai must enforce at least `steps <= n`. Put the check in shared
  `verify.rs` / `relation.rs` (H2) so it is not Ajtai-only.

### H2 (BLOCKING, shared code): the relation name does not fix the VU shape

The same missing bound means a pinned `fp8-ada` (Poseidon2) or `+blake3` statement can claim any `steps`, and so any K per VU,
not the relation's canonical K. I found no digest collision for these leaves. BLAKE3's header frames `n_chunks`; I did not
attack the Poseidon2 sponge's length handling this session. So this is a claim-integrity issue rather than a demonstrated
binding break. Anything that reports "VU =
GemmAccumulator<1536>" from a pinned accept is unsupported until steps is pinned. The Poseidon2 end-to-end run was OOM-killed
on the laptop (exit 137), so the evidence is code reading plus the Ajtai demonstration through the same `verify.rs` path.
The H1 fix closes H2.

### G1: FIXED on ajtai-leaf-3

`leaf.rs:156-340 chain_key` follows each public lane from `hash.d[x]` through its pin row, its single `is_end * (out - d)` tie,
its chain link (`acc_in` = the neighbour's `out`), and the one linear row defining `out`. It then checks that row coefficient
by coefficient against the re-derived B, and checks the bit rows (booleanity, order, disjointness). Red-team-leaf-2's B = 0 +
decoy forgery (`leaf3_g1_rust_only.py`, with the Python check disabled so the forgery reaches Rust):

* pinned: refused (sys_id mismatch);
* `--allow-any-system`: refused ("hash.d[0]: the key row is not out - (X acc_in)[0] - B[0] bits over the linked neighbour");
* the Python verifier also refuses at fixture write (`AjtaiLeaf.check_system`).

Scope, documented at `leaf.rs:193-194`: unpinned, the check proves the digests are derived-key digests of *some* boolean rows.
That those rows are the operands is the pin's job. This is acceptable.

### G3: PARTIAL (unchanged at share-logup-3 777670ac)

* The pipelined path refuses live coins (`relchain.py:526`, NotImplementedError).
* The unpipelined interactive `SharedHashedRunner.prove_vus` samples `coins_h` itself when the caller passes None
  (`relchain.py:1033-1035`).
* `verify_vus` with a single Coins takes H's coins from `proof.h.coins` (`:1106-1108`).

This is sound only if every live caller passes both verifier coins, and nothing enforces that. Fix: refuse `coins_h=None` when
`coins` came from a live verifier, or document the path as local-only. I did not re-run share-logup-3's new G/H pins (3ad48e50)
against the pair negatives.

### Table 1 assumption lines

* **Poseidon2:** operand rows are bound by a Poseidon2 sponge chain over BabyBear (binding = Poseidon2 collision resistance). The
  public digests are not hiding; row privacy comes only from Ligero's ZK masking.
* **BLAKE3:** binding = BLAKE3 collision resistance with role-keyed, `n_chunks`-framed leaves, plus SHA-256 collision resistance
  for the tagged malformed-frame domain. Digests are deterministic, not hiding.
* **Ajtai n64 / n128:** binding = Ring-SIS over `F_p[X]/(X^n + 1)` (BabyBear p, n = 64 / 128) with the SHAKE-256-derived B,
  **valid only for rows of at most n columns**. The verifier must enforce `steps <= n` and today does not (H1). Binding-only,
  not hiding: a low-entropy row can be brute-forced from its public digest.

### What blocks integration

1. **H1:** no Ajtai relation integrates until Rust and Python verify pin `steps` per relation (plus `steps <= n` for unpinned
   Ajtai) and refuse the fixtures above. Routed to ajtai-leaf-3 (coordinator 22:50Z plus my handoff).
2. **H2:** the same check belongs in shared `verify.rs` / `relation.rs` so Poseidon2, blake3 and share-logup inherit it. Handoff
   to verify-rs-3.
3. **G3:** enforce or document that live runs pass both coins (share-logup-3).
4. Not covered by me: share-logup-3's 3ad48e50 G/H pins against the pair negatives; the Poseidon2 steps-mismatch run (OOM on
   the laptop).

Handoffs:
`ajtai-leaf-3/20260923T2255Z-handoff-from-red-team-leaf-3.md`,
`verify-rs-3/20260923T2255Z-handoff-from-red-team-leaf-3.md`,
`share-logup-3/20260923T2255Z-handoff-from-red-team-leaf-3.md`,
`blake3-leaf-3/20260923T2255Z-handoff-from-red-team-leaf-3.md`.

## Log
* 22:20Z start.
* 22:44Z H1 end-to-end on ajtai-leaf-2 (pinned accept, steps 96).
* 22:48Z ajtai-leaf-3 47d191e2 built; G1 FIXED; H1 persists; collide end-to-end: same a/b roots, two y, both accepted pinned.
* 22:52Z steps 32 also accepted pinned; Poseidon2 steps-96 run OOM-killed (137); fixtures stored; commit 177d7fe6.
* 22:54Z n128: steps 192 accepted pinned; collide on n128 reproduces (same a/b roots, two y, both accepted); commit 89cd6cf7.
