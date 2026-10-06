---
id: red-team-vbridge-c/20261006T0708Z-finding-pr1283-review
campaign: proofs
lane: red-team-vbridge-c
kind: finding
status: final
repo: danielreuter/verity
origin: pr:1283@3d9977368581d925cdd6de708198a2330b6f7f9f
---

# Red team, VBridge C2's headline (#1283, `sound_recOpen`): GRANT at 3d9977368

I reviewed #1283 from 5 Oct 9:40 PM to 6 Oct 12:10 AM PDT, as red-team-vbridge-c (agent
bc-cf768002-48a3-53ab-ab77-5a07f1ce8abc) for the proofs coordinator. The head is `3d9977368581d925cdd6de708198a2330b6f7f9f` (`cursor/vbridge-recopen-95d4`), on #1274's
`2434949b9`, with B2 (#1272 `7c5cb816e`) merged in as `203ddd6ce`. I used my own worktree and Lake output directory.
Evidence: `art:547fabd7fc224c972ff54610264f4467f2108c233d4eb80b555d3c7c0ff740b0` (probes, logs, dump digests, record
diffs, local replay) and audit run `r20261006-044346-2f12` (vy-nebius-2). "rec_open" means
`backends/flock/python/verity_flock/rec_open.py` at rec-step3 `2730170682d21b687505981158b3ba02218cbee1`, the commit
the PR cites. Lean paths are relative to `verity/Security/`.

**Verdict: GRANT at `3d9977368581d925cdd6de708198a2330b6f7f9f`.** `sound_recOpen` restates `RecOpen_v3._steps`
exactly; the Lean builder is `rec_open.unit_circuit` gate for gate. The statement is not vacuous: an honest run meets every hypothesis at once. The
record adds only `sound_recOpen` and its three definitions, and changes no other record. The B2 merge keeps both sides
and nothing else. Nothing blocks.

## The five checks

1. **The restatement.** `consStructure` is `cons_structure` term for term: `ops` = `[w l]` for `l < LANES`, then
   `[v i]` for `i < 2·LANES`; `res[r]` = `mul [(LANES + r·LANES + l, l)]`, `add [w (LANES + r)]` for `r < 2`. It drops
   `nw` and `nv`, and that is safe: `rec_residuals.residual_forms` reads only `S["ops"]` and `S["res"]`
   (`rec_residuals.py:294-338`). `recOpen` is `_steps`: residuals over `row ++ acc.take 256` and `coef` first, then
   `climbRow H row aux (dirs.take 16)`, returning `(out, t ++ acc.drop 256)`. `_Forms.residuals` is `residual_forms(self.C,
   S, w, v)` (`rec_open.py:227-228`). `consTerm` is `acc_ref`'s element `k` with the same index `c[k·LANES + l]`; it sums
   from `a[k]` instead of XOR-ing `a[r]` in last, and XOR is commutative. Executable confirmation:
   - `recOpen` on variable ports (allocated from the empty state in `row, aux, acc, coef, dirs` order) against
     `unit_circuit(LANES, H)` (`in0..` words in that order, `out0..63` then `acc0..63`), dumped one line per AND row and
     one per output form. The dumps are **byte-identical** at (LANES, H) = (8, 1), 324,548 rows, sha256 `08739261…`, and
     (16, 2), 583,752 rows, sha256 `e726cc85…`.
   - `open_ref` on the honest ports agrees with the bits Lean's forms carry and with the statement's right-hand sides
     (`Flock.climb` of the plain leaf, and `consTerm` with `F128.mul`), at (8, 1) with `pos` 0 and 1 and at (16, 2) with
     `pos` 2. That checks `consTerm` against `gf2k.mul` numerically.
2. **The byte layout.** Lean's `F128.toBytes` is `le64(lo) ‖ le64(hi)`; `rec_live.f128_bytes` is `struct.pack("<QQ", lo,
   hi)`, and `rec_vstar.row_bytes` concatenates it per element. `bitOf x k` reads `w128 lo hi = 2^64·hi + lo`
   (`Level3/GF128.lean:18`). So bit `t` of `rowBytes` is bit `t % 128` of element `t / 128` (`bitL_rowBytes`, through
   `Refine.rowBytes_data`), which is also the order of the Python circuit's inputs (word `8i + k` = bits `16k..` of
   element `i`, port bit `16j + b` = bit `b` of word `j`). The leaf is `Sha512.hash (rowBytes r)`, which is
   `rec_vstar.leaf(row)` unsalted and `(MerkleScheme.sha512 "flock-leaf/sha512-unsalted").leaf r s` by `rfl`.
3. **Satisfiable, no `c.size`.** `sound_recOpen (MerkleScheme.sha512 "flock-leaf/sha512-unsalted") (fun _ _ => rfl) 8 1
   (by decide)` and `sound_recOpen MerkleScheme.hm96Sha512 (fun _ _ => rfl) 8 16 (by decide)` elaborate. An honest run
   at the real port sizes (row `128·LANES`, aux `16·aux_words(H)`, acc 1024, coef `256·LANES`, dirs 128 bits), with
   every committed bit forward-evaluated, gives `stHolds = true`, all seven hypotheses true, and both conclusions true,
   at (8, 1, `idx` 0), (8, 1, `idx` 1) and (16, 2, `idx` 2). A control, `acc_out` checked against `consTerm` at a `c`
   with one element changed, is false in each run. No `c.size` hypothesis is needed: `Carries z coef (rowBytes c)` fixes
   `coef.length = 128·c.size`, the forms past `coef`'s end read as zero (`bit_eq_wbit`), and `c[i]!` past the end is 0.
   On the Python side `coef` is always `2·LANES` elements (`coef_words`), so G instantiates `c` at that size anyway.
4. **The record.**
   - The audit: `r20261006-044346-2f12` on vy-nebius-2, `audit.py --build --no-runs verity/Security` in the run's own
     clone at `3d9977368`, comparing records (no `--update`), with the kernel replay. Run record
     `art:3c9a4c60e6a88478b66124d5f727897391c36f23a1c158c91801c7d51fdcc05e`. Both packages **PASS**, with 0 failures,
     0 escapes and axioms `propext`, `Classical.choice`, `Quot.sound`. `security`: 1753 guarantees in 6873
     declarations, 6,794 accepted by the replay. `security_proofs`: 57,911 declarations in 882 modules, 57,336 accepted
     by the replay, the six VBridge modules among them. The records it computed equal the committed ones for all 1753
     guarantees and every `reads` entry.
   - The diff: against the merge `203ddd6ce`, `lean-audit.json` adds the guarantee `FlockVBridge.sound_recOpen` (owner
     `@proofs`, no assumptions) and the module entry `Proofs.Flock.VBridge.RecOpen`, which reads `consStructure`,
     `consTerm` and `recOpen`. Its only other edits add `sound_recOpen` to the `guarantees` lists of the 13 modules it
     reads. No guarantee record, definition digest or module digest changes against the merge, #1274 (`2434949b9`), B2
     (`7c5cb816e`) or #1258 (`17cfcdae8`). `3d9977368` differs from `8e729fbe7`, where the lane's `--no-replay` audit
     `r20261006-033234-afc7` ran, only in `lean-audit.json`.
   - Locally, `tools/lean/Replay.lean` on the six VBridge modules (Sha, Climb, Open, Karatsuba, Residuals, RecOpen,
     compiled at `3d9977368` against identical imports) accepted all 465 constants, with body axioms `propext`,
     `Classical.choice`, `Quot.sound`. `#print axioms` gives the same three for `sound_recOpen`,
     `resVal_consStructure`, `bitL_rowBytes` and `carries_split`. `RecOpen.lean` has no `sorry`, `native_decide`,
     `axiom`, `implemented_by`, `extern`, `unsafe` or `csimp`, and compiles with no warnings, here and on the pod.
5. **The merge.** `git show --remerge-diff 203ddd6ce` shows one conflict, `VBridge.lean`'s imports, resolved by keeping
   all four (`Climb`, `Open`, `Karatsuba`, `Residuals`). `lean-audit.json` merged textually; a 3-way semantic check
   against the merge base finds no problem, and the merge's 1752 guarantees are the union of both sides' 1750, each
   record equal to its side's. Against `2434949b9` the merge adds only `Karatsuba.lean`, `Residuals.lean`, two import
   lines and their records; against `7c5cb816e`, only `Climb.lean`, `Open.lean`, two import lines and their records.

## Not blocking

- **The leaf is the plain scheme's**, as in #1274: `out`'s right-hand side is the climb of `Sha512.hash (rowBytes r)`.
  At `hm96Sha512`, whose leaf is salted, the statement still holds (it elaborates with `hms` by `rfl`), but G can turn
  it into `Merkle.opens` only at a scheme whose `leaf r s` is that hash, i.e. the plain one. This is what vbridge did.
- **For G.** `acc_out`'s conclusion has exactly the shape of the next opening's `acc` hypothesis (`rowBytes a' ++ rest`
  with `a' = #[consTerm … 0, consTerm … 1]`, size 2), so the consistency sums chain from one opening to the next with
  no glue lemma.
- **For D.** Because the builder's rows are `unit_circuit`'s, row for row and variable for variable, when the ports are
  allocated in `row, aux, acc, coef, dirs` order from an empty state, D's layout can read `recOpen`'s rows as the
  unit's rows at the same indices. What D still owes is what the PR says: `stHolds` from "no wrong unit", and `Carries`
  of the ports from the committed u16 words.
- The statement is at rec-step3 `273017068`, which has not landed; if `_steps`, `cons_structure` or `acc_ref` change,
  so does this.
- The audit took 2 h 2 min on vy-nebius-2, against 48 min for the same audit on vy-nebius-1: node 2 has no Lean build
  cache (`lean-cache: off on this machine`), so `security_proofs` built ArkLib and VCVio from source, beside about 500
  other processes.

## Label

`pr:1283@3d9977368581d925cdd6de708198a2330b6f7f9f`: `grant=red-team` by red-team-vbridge-c, ref
`r20261006-044346-2f12`, written 2026-10-06T07:07:08Z. I pushed it with `labels-sync --push-only`, and
`research data labels … --remote` lists it on both the local store and the remote.
