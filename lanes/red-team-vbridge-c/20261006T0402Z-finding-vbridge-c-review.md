---
id: red-team-vbridge-c/20261006T0402Z-finding-vbridge-c-review
campaign: proofs
lane: red-team-vbridge-c
kind: finding
status: final
repo: danielreuter/verity
origin: pr:1273@50bf1c0801620be435b05318ac31afedcb6c5880 pr:1274@2434949b9ccaa71ac5d44c10f5550acd2bd133f7
---

# Red team, VBridge C1 (#1273, `sound_climbFrom`) and C2's `out` half (#1274, `sound_climbRow`): GRANT both

I reviewed these on 5 Oct, 8:06 to 9:05 PM PDT, as red-team-vbridge-c (agent bc-cf768002-48a3-53ab-ab77-5a07f1ce8abc) for the proofs coordinator. The
heads were #1273 `50bf1c0801620be435b05318ac31afedcb6c5880` (`cursor/vbridge-climb-95d4`) and #1274
`2434949b9ccaa71ac5d44c10f5550acd2bd133f7` (`cursor/vbridge-open-95d4`, which contains #1273), both on #1258 `17cfcdae8`.
I worked in my own worktree and Lake output directory. Evidence: `art:8312dab4c8905e0f7bdec4ee90cb9d5f194b43b03274cf66e81219d935eec8cb`
(the probes and their logs) and audit run `r20261006-030819-703e` (vy-nebius-1, preserved). Lean paths are relative to `verity/Security/` unless they start
with `backends/`. "rec_open" means `backends/flock/python/verity_flock/rec_open.py` on rec-step3.

**Verdict: GRANT #1273, GRANT #1274.** My replay audit at #1274's head found every Lean check clean, and the committed records match what it computed.
The statements say what VBridge needs. The hypotheses can be met at the real call site. The Lean builder is
`RecOpen_v3._climb` gate for gate (the dumps are byte-identical). Nothing blocks the merge. Six notes follow for the
next pieces, two of them about the planned `sound_recOpen`.

## 1. Axioms and the audit

Attempt `r20261006-030819-703e`: `audit.py --build verity/Security` on vy-nebius-1, in the run's own clone at
`2434949b9`. It compared records (no `--update`) and ran the kernel replay and the `runs`.
- `security`: **PASS**, 0 failures. It has 1750 guarantees in 6873 declarations, `sound_climbFrom` and
  `sound_climbRow` among them with owner `@proofs`, and no escapes. The replay covered 6,794 declarations, and the
  axioms are `propext`, `Classical.choice` and `Quot.sound`. Since it compared rather than updated, the committed
  records are the ones this build computes.
- `security_proofs`: every Lean check passed. The replay covered 56,994 declarations (295 skipped, the lock's
  `exempt` list), with the same three axioms and no escapes. The audit reports **FAIL** on one item, the `runs` step
  `Proofs.Warden.DifftestMain`'s `generate`. It is not these PRs': `difftest_vectors.py:192` refuses because
  `research run --cwd clone` puts the source tree, not the clone, on `PYTHONPATH`. rec-thm's audit and
  flock-gk-game's hit the same failure (`note:proofs/20261006T0101Z-finding-rec-thm`). Neither PR touches Warden,
  `Proofs/lean-audit.json` or `tools/lean`. `check` runs it in its own environment.

- `#print axioms` (my probe, compiled from the 2434949b9 tree) gives `[propext, Classical.choice, Quot.sound]` for
  `sound_climbFrom`, `sound_climbRow`, `carries_inj`, `carries_zeros`, `sound_swap` and `sound_shaIv`.
- `Climb.lean`, `Open.lean` and `VBridge.lean` contain no `sorry`, `axiom`, `native_decide`, `implemented_by`, `extern`,
  `unsafe`, `opaque` or `set_option`.
- **Records against #1258.** The `guarantees` diff (`17cfcdae8` → `50bf1c080` → `2434949b9`) adds exactly
  `FlockVBridge.sound_climbFrom`, then `FlockVBridge.sound_climbRow`, and changes and removes none. Beyond that, `reads`
  gains `Proofs.Flock.VBridge.Climb` (`Carries`, `climbFrom`, `swap`) and `Proofs.Flock.VBridge.Open` (`climbRow`,
  `sibForms`), and each module the statements read gets the new name appended to its `guarantees` list. No definition
  digest changes, and `meaning`, `reads_exempt` and `roots` are unchanged.

## 2. The statements

- **`hms` holds by `rfl`.** `Flock/Merkle.lean`: both `hm96Sha512` and `sha512 id` have `node := fun l r =>
  Sha512.hash (l ++ r)`. The probe elaborates `sound_climbFrom` and `sound_climbRow` at both schemes with
  `fun _ _ => rfl`. It also proves `MerkleScheme.find? "flock-leaf/sha512-unsalted" = some (sha512 "flock-leaf/sha512-unsalted")`
  and `(sha512 _).leaf r s = Sha512.hash (rowBytes r)`, both by `rfl`.
- **Direction bits.** `Flock.climb` puts the accumulator on the left when `idx % 2 = 0` and recurses on `idx / 2`, so
  level 0 (the leaf's sibling) reads bit 0, the LSB. `climbFrom` reads `d[h + j]` at level `h + j`, and the
  hypothesis asks `ev z d[h + j] = idx.testBit j`. `swap` with a 0 bit gives `(cur, sib)`, so the node is
  `SHA-512(cur ‖ sib)`, which matches `climb`. In rec_open, `dirs_words(pos, H)[0] = pos & (2^H − 1)` and
  `_steps` passes `dirs[:16]`, so `d[h]` is bit `h` of word 0. `open_ref` puts `sib` first when `(low >> h) & 1`. G
  takes `idx := pos`. `climb` reads only the low `H` bits, and `opens` compares the climb with `cap[pos >>> (d − c)]`.
- **`Carries`'s order** is form `t` = `bitL b t` = `testBit (t % 8)` of byte `t / 8` (`Hm/Hash.lean:73`). It matches:
  - rec_open's port layout: "leaf t of a port is bit t & 7 of its byte string's byte t >> 3", with u16 words LSB first
    and little-endian bytes;
  - `_bits`;
  - #1258's `sound_shaFrom` hypothesis, which `sound_shaIv` only repackages.

  **G can discharge it.** Any forms of length `8n` carry the bytes read off `z`, and G defines the decoded row and
  siblings from exactly those bytes. Lean's `rowBytes` (`F128.toBytes`: `lo` LE, then `hi` LE) is rec_open's
  `words` order. The existence lemma (`Carries z w (readBytes z w)`) is not written yet; see note 5.
- **Sizes.** `NODE_WORDS = 32` words, 64 bytes, is `sibForms`' 512-bit slice `aux[512h, 512(h + 1))`, which is
  `aux[16·NODE_WORDS·h : …]`. `OUT_WORDS = 64` words is 512 bits of top plus `16·(64 − 32) = 512` zero bits, so
  `Carries` asks for `8·128 = 1024` forms. `expected(node) = words_of(node) + [0]*32` is node ‖ 64 zero bytes. The
  climb is 64 bytes for every `H` (`hash_size`).
- **Vacuity.**
  - `List.Forall₂ (b.size = 64 ∧ Carries z w b) (sibForms aux H) ss` can be met exactly when `aux.length ≥ 512·H`;
    for a shorter `aux`, a slice has fewer than 512 forms. The real port has `16·aux_words(H) = 1024·⌈H/2⌉ ≥ 512·H`
    bits, so D must hand over the whole `aux` port. It also fixes `ss.length = H`, which `opens` needs as `d − c`.
  - `d.getD h Lin.zero`, when `d` is short, constrains `idx` (bit `h` must be 0) without making the hypothesis
    unsatisfiable. The real `d` is `dirs.take 16`, with `H ≤ 16` (rec_open's `_check`).
  - Every other hypothesis is met by bytes read off `z`. The direction bits are those of some `idx`, for any `z`.
  - `Sound` quantifies over every start state, so the climb composes after `_steps`' residual gates.

## 3. The restatement against the Python

`_Forms.swap` (`t = C.AND(d, p ^ q)`, then the two XORs), `_climb`'s loop, the leaf `_sha(IV, row, 0)` and the zero
tail are `swap`, `climbFrom` and `climbRow` line for line. `preCv [] 0` evaluates to SHA-512's IV.

**rec-step3 has not changed `_climb`.** `rec_open.py` is byte-identical at `d23edf42d` and at rec-step3's current head
`273017068`. The three commits since then touch only `rec_vstar.py`, its test, the GPU decoder and `85-rec-reprice.sh`.
C2 needs no change.

**Executable check** (`art:8312dab4…`):
- **Constant ports.** `climbRow` folds to 0 rows at 6 shapes: (LANES, H, pos) = (8,1,0), (8,1,1), (8,2,2), (8,3,5),
  (16,3,6), (8,4,11). Its `out` bytes equal three other computations, byte for byte:
  - `Flock.climb` of the plain leaf, followed by 64 zero bytes, evaluated in Lean;
  - rec_open `open_ref`;
  - `_climb` over `forms.Circuit`.
- **Variable ports** `row`, `aux`, `dirs`. Lean's rows (out, a, b, oldest first) and its 1024 output forms are
  byte-identical to Python's AND gates and outputs at four shapes: (LANES, H) = (8,1), (8,2), (16,3), and (8,2) with
  constant `dirs`. Those are 285,182 to 652,241 rows, and the dumps' SHA-256s are equal.

## Notes (none blocks)

1. **`sound_recOpen` as planned in #1274's body needs a leaf hypothesis.** Its conclusion uses `ms.leaf r ByteArray.empty`
   for a generic `ms` that has only `hms` (about the node). For `hm96Sha512`, that leaf is not `SHA-512(rowBytes r)`, so
   the statement is unprovable as written. Either add `hleaf : ∀ r s, ms.leaf r s = Sha512.hash (MerkleScheme.rowBytes r)`
   (it holds by `rfl` for `sha512 _`), or state it at `MerkleScheme.sha512 "flock-leaf/sha512-unsalted"`.
2. **`recOpen`'s order.** `_steps` builds `residuals` first and `_climb` second. The plan's `recOpen` builds
   `climbRow` first. That doesn't affect soundness, but the gate numbering differs, so D's test (Lean layout =
   Python's circuit file) would fail. Build `residualForms` first.
3. **D** must lay `row`, `aux`, `acc`, `coef` and `dirs` out in that order, as 16-bit words (`in0 ..`), with the
   outputs `out0..63` then `acc0..63`. It must pass the whole `aux` port (the vacuity point above).
4. **G's `dirs`.** `idx := pos` needs `ev z dirs[h] = pos.testBit h`, which only the public-input binding gives (#1179
   and the plan's reason 3). Without it, a prover picks the directions, and the climb proves an opening at another
   position.
5. **G's small lemmas:**
   - `Carries z w (readBytes z w)` for `8 ∣ w.length`;
   - cancellation of `++ ⟨replicate 64 0⟩`, to get `climb … = top` from `carries_inj`;
   - `rowBytes` as a bijection on `16·LANES`-byte strings;
   - `H = d − c` per level, with the top as `cap[pos >>> H]`. The registered top is bound to the inner cap by
     rec-thm's composition (gateway salts, `cr/sha-512`), not here.
6. **G must count openings from the verifier, not from the layer.** rec-step3 `195fdddbc` fixed a Python V* that
   accepted a session with zero queries and never read a top. G's statement should take the number of `RecOpen`
   instances from F's positions, so that an outer layer with fewer openings can't satisfy the premise.
7. **Cosmetic.** #1273's body cites `C.AND` in `backends/flock/pod/gf2.py`. The unit uses `forms.Circuit`
   (`verity/primitives/circuits/boolean/forms.py`), a separate copy whose `AND` is the same.

## Labels

`research data label pr:1273@50bf1c0801620be435b05318ac31afedcb6c5880 grant red-team --by proofs --ref note:red-team-vbridge-c/20261006T0402Z-finding-vbridge-c-review`
and the same for `pr:1274@2434949b9ccaa71ac5d44c10f5550acd2bd133f7`. Both were checked on the remote with `research data labels … --remote`.
