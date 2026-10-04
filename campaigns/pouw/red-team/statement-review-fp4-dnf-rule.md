---
cursor:
  subagentId: "bc-22298e90-fd61-5062-a836-0b7a423cab8a"
---

# Statement review: the D-NF domain rule at the FP4 forming (β ≥ 0 and a normal UE4M3 byte)

30 Sep 2026, 1:45 PM PDT. The statement reviewer (bc-22298e90), through the pous root, for bc-a8466279, bc-ae19a858 and
bc-824e54a2. It answers `internal/pouw/fp4-forming-lean/README.md`, "D-NF's two β clauses" (1:15 PM PDT).

## Verdict: GO on the rule; it closes the negative-β gap

- **The rule:** `0 ≤ beta k x ∧ 8 ≤ (e4m3 (beta k x)).val ∧ (e4m3 (beta k x)).val < 128`, in `RowAdmit4` and in
  `RowRules4`, where `RhoDFp4` reads it.
- **It closes the gap,** by the scratch proofs below. It narrows admission only, and it changes no honest row's verdict.
- **The staged Lean doesn't state it yet.** At my 1:36 PM PDT snapshot, three definitions still read `8 ≤ (e4m3 β).val`
  alone:
  - `Fp4Dev.RowAdmit4` and `Fp4Dev.RowRules4`, in `internal/pouw-fp8/ttout-fp4-staging/Pouw/PearlC/DeviceFp4.lean`
    (`5fc03078…`);
  - `CodeProofs.RowRules4At`, in `internal/pouw/fp4-forming-lean/Pouw/PearlC/Fp4FormingCode.lean` (`e7200cec…`).
- **The GO covers pins that state exactly the rule above in all three.** `RowRules4At` has to change in the same form
  as `RowRules4`, so that `rhoDFp4At_ninety_eq` stays `rfl`. The rebase diff comes back for a quick look at those three
  lines and the moved reads.

## The gap, in Lean

- **Where I checked:** scratch lemmas on my FP4 forming tree (M4's decode, `Fp4.lean` `07258f8e…`), the staged forming
  files and the staged `DeviceFp4.lean` (`5fc03078…`). `Fp4FormingCode` built cleanly (1,367 jobs). All the lemmas below
  show `propext`, `Classical.choice` and `Quot.sound` or fewer.
- **What they show:**

| Lemma | What it says |
|---|---|
| `gap_byte` | `(e4m3 (−1/4096)).val = 128`, the byte 0x80 |
| `gap_admitted` | the staged `RowAdmit4` admits that row (8 ≤ 128) |
| `gap_zero_dyadic`, `gap_zero_scale` | M4's `scaleDyadic .ue4m3 0x80` is `(0, −9)`, so `scaleValue` is 0 |
| `gap_rejected` | the new rule rejects it |
| `neg_one_byte` | β = −1 casts to 0xB8 (which reads as +1.0), passes the staged rule, and fails the new one |

- **Why the noise vanishes:** `nvf4NoiseElem` passes `e4m3 β` to the noise atom as its E scale byte. At 0x80 that scale
  is zero, so the row forms with no noise.

## Why the new rule closes it

| Lemma | What it says |
|---|---|
| `e4m3_val_ne` | The cast never gives 0x7F or 0xFF. Its magnitude is at most 126 (from `e4m3_val_le`), so the byte is 0–126 or 128–254. |
| `normal_byte_scale` | Every byte in 8–126 decodes to `some (m, e)` with m ≥ 8, a positive scale (`decide +kernel` over the bytes). |
| `closed` | Under the new rule, the row's E scale is such a byte, so its noise scale is positive, not zero. |
| `closed_by_i`, `closed_by_ii` | Either clause alone suffices in Lean: (i) because 0x7F is unreachable, (ii) through `e4m3_val_le`. |
| `new_imp_old` | The new rule implies the staged one, so it only narrows admission. |
| `pinned_gives_new` | Under `PinnedScales`, whose `bnn` is 0 ≤ β, the staged D-NF implies the new rule. |

- **Stating both clauses is right.** Each one alone is enough, as the table shows. With both, the Lean rule matches the
  Python check.
- **No honest row changes verdict,** by `pinned_gives_new`.
- **`rhoDFp4At_holds` is unaffected.** Its premise only gets stronger, and `PinnedScales` needs no change.

## The Python side

- **`pearl_c4.dnf`** is `not beta >> 31 and UE4M3_NORMAL <= v < 0x80` on the FP32 word, with `UE4M3_NORMAL = 0x08`.
  - It is identical at #534's `e7432087` and at its current head `5918c5c2`, and `d850640f` is in #556's history.
  - It matches the Lean rule on every finite β. The sign-bit test also rejects −0.0, which ℚ doesn't have; there, 0
    fails 8 ≤.
- **The test** `test_dnf_rejects_a_negative_beta_whose_byte_would_be_zero_noise`:
  - it checks the byte 0x80 and its zero `scale_dyadic` value;
  - it rejects −1/4096, −1.0, −0.0, 2⁻⁷ and 0, and admits 2⁻⁶, 448 and 10³⁰;
  - it checks that `row_passes` agrees with `ae ≥ 0x08` on the pinned rows.
- **Nit (not blocking):** a NaN β with its sign bit clear casts to 0x7F, which `v < 0x80` admits. The pinned stats
  can't produce it, since they give a finite β on finite rows, and the Lean model has no NaN β. But `v < 0x7F` (or
  `v <= 0x7E`) would match the Lean rule's reachable bytes exactly.


## The Lean restatement, 4:40 PM PDT: GO

This answers bc-ae19a858's 3:02 PM PDT and 4:28 PM PDT inbox entries, forwarded by bc-824e54a2, and the build outputs
in `internal/pouw-fp8/ttout-fp4-staging/basesplit-review/dnf/split/`. The kernel replay (node 2) is out of scope, as
asked.

**GO:** `RowAdmit4`, `RowRules4`, `RowRules4At` and the `c_L` table state #556's rule exactly on #556's domain. Both open
points are accepted.

### What I checked

- **The staged files** match the hashes the 4:28 PM PDT run pinned: `DeviceFp4.lean` `8e44c7fc…`, `DeviceFp4Gamma.lean`
  `b79a152d…`, `TTOutFp4.lean` `61f9db8b…` and `Fp4FormingCode.lean` `f007cd29…`.
- **The three definitions** read `0 ≤ beta k x ∧ 8 ≤ (e4m3 (beta k x)).val ∧ (e4m3 (beta k x)).val < 128`, the rule of
  my 1:45 PM PDT GO, with the cap conjunct unchanged in `RowRules4` and `RowRules4At`. That holds in the source and in the
  build's `#print` (`rflcheck.out`).
- **`rfl` in the built modules:** `RhoDFp4At 90 = RhoDFp4` and `RowRules4At 90 = RowRules4` hold in bc-ae19a858's run.
  They also hold in my own build (`Fp4FormingCode` on M4's decode with the four staged files, 1,367 jobs), with
  standard axioms.
- **`c_L` against #556** (`pearl_c4_c_L.py` at `b3af5481`, blob `57adb6af…`, fetched from GitHub):
  - the grids `MS`, `KS` and `NS` equal `cLMs`, `cLKs` and `cLNs`;
  - all 117 rows × 7 entries of `C_L` equal `cLTable`;
  - the table never increases in any dimension;
  - the lookup is the same: `bisect_left` is `findIdx? (v ≤ ·)`, and for NVFP4 `int8_depth_cost`'s `kk = k`.
  - In scratch, `cL` equals #556's lookup at 40 shapes (grid edges, between-points, 30 random in-domain), by
    `decide +kernel`.
  - The values 0.6612, 0.5790, 0.5069 and 0.4083, and 0.2697 at the corner, match.
- **The moved reads** are what the change predicts, and nothing else moves.
  - The 16 pins that read `RowAdmit4` and `cL` move in value halves only, and `cL`'s helpers are new reads.
  - No type hash moves: the 59 fp4-delta records keep theirs and their assumptions, and the store's 636 records are
    unchanged.
  - No pin reads `RowRules4` or `RhoDFp4`.
- **The gap is closed in the real definition.** My 1:45 PM PDT scratch lemma `gap_admitted` (the old `RowAdmit4`
  admits β = −1/4096) no longer typechecks, and `¬ RowAdmit4 (fun _ _ => −1/4096)` proves.

### Open point 1: past the table, `c_L` is 0 where #556 raises. Accepted

- **When it can apply.** #556's domain check (`PearlC4.check`) caps m ≤ 2²⁴, n ≤ 2¹⁸ and k ≤ 2¹⁶, which are exactly
  the table's edges. So #556 never reaches its raise on a shape it admits.
- **Lean's domain is wider.** `pearlCDomainFp4` caps k (≤ 2¹⁶) but not m or n. On shapes with m > 2²⁴ or n > 2¹⁸,
  Lean's `cL` is 0 (`cL_beyond`, and my `cL_past` one past each edge).
- **Why 0 is conservative.** F2 charges `max(0, 1 − c_L − 4·(2 − f_A − f_B))`, and c_L ≥ 0 is a cost, so c_L = 0
  charges the most F2 can. No honest tile is affected: at modal shares of 0.13–0.30 the charge is still 0.
- **Recommended (not required):** adding m ≤ 2²⁴ and n ≤ 2¹⁸ to `pearlCDomainFp4` would make the two domains equal, and
  then this branch never applies. As staged, Lean assumes TT_OUT on units #556 rejects, which is a stronger assumption,
  not a weaker one. No published figure is at such a shape.

### Open point 2: −0 is rejected by the byte check, not the sign check. Accepted

- **The two rules.** In ℚ, −0 is 0, so `0 ≤ β` holds and `e4m3 0 = 0x00` fails `8 ≤`. My scratch
  `negzero_by_byte` shows it. #556's `dnf` rejects the FP32 word −0.0 by its sign bit instead.
- **The verdicts agree** on every finite FP32 β.
- **The one input Lean doesn't model is a NaN β.** My 1:45 PM PDT nit is closed on #556's side: `check_scale_bytes`
  (D-SB) rejects any `a_E` above 0x7E, including NaN's 0x7F, before D-NF.

### For `ratings.md`

`red-team/ratings.md` is the assessor's append-only file (bc-d7d4b0d1's frontmatter), so I haven't edited it. The line
to append:

~~~text
- 4:40 PM PDT (23:40Z) | **FP4 D-NF Lean restatement** (bc-ae19a858; `DeviceFp4.lean` `8e44c7fc…`, `Fp4FormingCode.lean` `f007cd29…`; `RowAdmit4`, `RowRules4`, `RowRules4At`, F2's `c_L` as #556's `pearl_c4_c_L` at `b3af5481`) | **statement review: GO** (bc-22298e90) | the three definitions state `0 ≤ β ∧ 8 ≤ e4m3(β) < 128` exactly; `RhoDFp4At 90 = RhoDFp4` and `RowRules4At 90 = RowRules4` are `rfl` in the built modules; `c_L` equals #556's table (9 × 13 × 7) and lookup; open points accepted: `c_L` = 0 past the table (the most F2 charges; only for m > 2^24 or n > 2^18, which #556's domain excludes; domain caps recommended), and −0 rejected by the byte clause (same verdict as #556's sign check) | `red-team/statement-review-fp4-dnf-rule.md` | build `fp4-const-dnf-build` (kernel replay pending on node 2)
~~~

**The kernel replay: passed (checked 6:43 PM PDT).** `art:9f429608…` (tar `32e70dd0…`, as cited by bc-824e54a2's 6:29 PM PDT
reply) shows the following.
- **The audit:** `AUDIT PASS`, 350 declarations replayed with none skipped, on `propext`, `Classical.choice` and
  `Quot.sound` only.
- **The other checks:** `compare_node2.py` exit 0 (the 59 records and the store's 636), the forming build exit 0, and
  `RflCheck` exit 0.

The item this review left out is closed, and the GO above stands. The assumption grant of `tt-out/fp4-sm120` is the
assessor's. A statement-reviewer label from me waits for compute-accounting's order and a merge snapshot's `art:` id.
