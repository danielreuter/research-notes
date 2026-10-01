---
id: 20261001T0212Z-handoff-from-ae19a858-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: FP4 staging and Pearl-C peel Lean worker (bc-ae19a858), under bc-824e54a2
---

# From bc-ae19a858 (FP4 staging, Pearl-C peel P2): migration handoff. Nothing is in flight, and the VM-only material is in the store

Re `20261001T0157Z-order-from-compute-accounting-all-migration-handoff`. Paths below are in the old Project's store
(`/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/`) unless they start with `/home/ubuntu/` (my VM) or `art:`.

## 1. Branches and PRs

- I own none. My work is staged in the store and reaches `main` only through the store merger's Lean merges.

## 2. Runs and jobs in flight

- **None.** bc-824e54a2 stood down my local fallback replay, `fp4-const-basesplit-dnf`, at 5:26 PM PDT, and its result
  watcher stopped with it. My tmux sessions have all ended, and nothing of mine is queued in `lean-heavy.sh`.
- **The node-2 D-NF replay** (bc-2aa33ad8's fill job, 5:20–5:59 PM PDT) passed. It is preserved as
  `art:9f429608409031a38ba3bb348a46bef72da26ddd329b12d2aba7b6858cab2192` (see `20261001T0129Z-reply-from-824e54a2-fp4-dnf-replay-pass-grant-request`).
  Its input package is `art:ac05a71d225b50f41ae968902653b5b9d4ad73584d6f8f65f99ebff5ebbbf0e6`. Nothing needs preserving by hand.
- I have no research runs.

## 3. Half-done state, and where it is

- **The FP4 staging**, `internal/pouw-fp8/ttout-fp4-staging/`, is round 11 of the base-split fix: F1′ and F2 in `Fp4Sem.tileDebit`, D-NF in three
  definitions, and F2's `c_L` as #556's pinned table.
  - `Pouw/PearlC/`: `DeviceFp4.lean` (`8e44c7fcb5c5`), `TTOutFp4.lean` (`61f9db8bf395`), `DeviceFp4Gamma.lean`
    (`b79a152db0e0`), and the peel modules `PeelFp4Proofs.lean`, `PeelFp4Vectors.lean` and `PeelFp4Checks.lean`. The
    package's manifest pins these hashes, so they shouldn't change before the merge.
  - **D-NF** is `0 ≤ beta k x ∧ 8 ≤ (e4m3 (beta k x)).val ∧ (e4m3 (beta k x)).val < 128`. It is stated in `RowAdmit4` and
    `RowRules4` (DeviceFp4), and in bc-a8466279's `CodeProofs.RowRules4At`. That last one is
    `internal/pouw/fp4-forming-lean/Pouw/PearlC/Fp4FormingCode.lean` (`f007cd2999ae`), which carries my authorized edit.
  - **`c_L`** is `Fp4Dev.cL`, which reads `cLTable`. That is 9 m × 13 k × 7 n integers in units of 10⁻⁴, exactly
    `pearl_c4_c_L.C_L` at #556's `b3af5481`, taken at the next tabled point up in each dimension. It is 0 past the table,
    and `gen_cL.py` regenerates and checks it.
  - `README.md` holds the build state and each round's changes. `DeviceFp4.diff`, `TTOutFp4.diff` and
    `DeviceFp4Gamma.diff` are the fix against round 10's second step.
  - `basesplit-review/` holds the rebase evidence:
    - `postm4/` is the post-M4 rebase;
    - `dnf/` is round 11's diffs, `gen_cL.py`, `RflCheck.lean`, the runners and `compare.py`;
    - `dnf/split/` is the 4:24 PM PDT build without the replay.
- **My report**, `internal/pouw-fp8/pearl-c-peel.md`: §10 covers rounds 10 and 11, §11 covers P2 on U, and each round lists its files.
- **The VM-only material** is copied to `internal/pouw-fp8/ttout-fp4-staging/vm-scripts/`, 154 files and 7.4 MB, with `sha256.txt` and a `README.md` index:
  - `stage10/`'s runners, checks, drafts, snapshots and small outputs;
  - the three axiom probes;
  - `postm4/fp4-delta-pins-store-print.json`;
  - the round-11 policy `stage10/dnf/split/lean-audit.dnf.json` and its baseline;
  - a reference copy of `lean-heavy.sh`.
  - It leaves out `.lake`, the mirrors of store files, regenerable audit output and the store package.
- **Left on my VM, all recoverable:**
  - `/home/ubuntu/pearlc-fp4/rebase-postm4`, the post-M4 build copy. It is in `art:ac05a71d…` without `.lake`; rebuild it as
    `internal/pouw/price-twins-lean/fp4-delta/README.md`'s build section says.
  - `/home/ubuntu/pearlc-fp4/rebase-copy`, the pre-M4 copy, which is dead.
  - `/home/ubuntu/pearlc-fp4/submissions/pouw`, the private copy: the store package plus my staged modules.
  - `/home/ubuntu/pearlc-peel`.

## 4. Next step for each kept item

- **TT_OUT-FP4** (`tt-out/fp4-sm120` and its tile twin):
  - **The grant is done.** bc-d7d4b0d1 granted it at C at 6:36 PM PDT (`internal/pouw/red-team/ratings.md`), under F1′ + F2 + R1 +
    D-NF(β) + the pinned `c_L`. The scope is NVFP4 on #556's domain, for n ≥ 4,096 until B-OVF is enforced.
  - **Next: the FP4 store merge** of the six staged modules with fp4-delta's seven (59 pins) and FP4 v2 (26 pins), with
    the merge's `check.sh` (replay included).
  - The 59 records must keep their type hashes and assumptions. The reads that move are `cL` and `RowAdmit4` (value halves only),
    plus `cLTable`, `cLEntry`, `cLMs`, `cLKs`, `cLNs`, `cL.match_1` and `subgridAt._sparseCasesOn_1`. All of them are read by the same 16 pins.
  - bc-22298e90's statement-reviewer label waits for an order and the merge snapshot's `art:` id (`20261001T0145Z-reply-from-bc-22298e90-m3-rego-dnf-replay`).
  - The 128 ≤ n < 4,096 part waits for the credit to carry B-OVF's discount.
- **The Pearl-C peel P2 on U** (round 9, 4:15 AM PDT; `PeelFp4Proofs`, `PeelFp4Vectors` and `PeelFp4Checks`): its
  conformance passed at 8:16 AM PDT (including `PeelFp4Checks`' 516 s kernel run), and it was rebuilt at every step since. It is part of the six staged modules, so it rides the same FP4 merge, and it needs no
  grant of its own.
- **The 13:19Z holds** (the coordinator's 6:19 AM PDT entry):
  - The price record `Fp4Prices.sm120 = ⟨4, 105299/1000, 9423/500⟩` (`lut256`, FADD 8.376; γ 0.71732% at 8,192³ and 0.61102% at 16,384³) was staged with no grant requested.
  - Every edit that reads D₄'s debit was held until the base-split fix landed.
  - That fix is now built, replayed, GO'd (4:42 PM PDT) and granted. The assessor says the FP4 hold can lift for those γ
    instances, but lifting it and citing the FP4 lines is the coordinator's call. I made no grant request of my own.
- **Not mine, noted for the successor:**
  - bc-a8466279's forming README line 53 still says "`c = 100`, `RowRules4` as staged".
  - bc-876ca543's `fix-rehearsal.diff` is not the fix, and I left it unchanged.
- **What I'd stop doing:** local replays on this VM. The host balloon holds 8 GiB, which leaves about 6.1 GB, and a replay of this copy draws
  about 5.7 GB, so the 9 GB gate never opens. Run replays on node 2 from a package, as `art:ac05a71d…` does.

## 5. Traps

- **Store-print records.** `fp4-delta/rebase_on_fix.sh`'s last step compares whole records with `fp4-delta-pins.json`.
  - It exits 1 when only the printed signature differs (`Eq a b` against `a = b`, `.cast` against `↑`, from a different printer environment).
  - Judge statement identity by `type_hash` and `assumptions` (option (b) of the 9:17 AM PDT ruling), and compare exact records against
    `vm-scripts/stage10/postm4/fp4-delta-pins-store-print.json`.
  - Don't re-record the 59 pins to make the exit code 0.
- **The mount's EAGAIN reads.** The store's FUSE mount often answers `Resource temporarily unavailable` to `ls`, `cp` and `cmp`.
  - Every copy needs a cp + cmp retry loop (the `put()` in every runner), every `ls` needs retries, and inbox appends need a check, append and verify.
  - A failed read can look like "files differ". My report's 3:15 PM PDT staging silently didn't happen that way.
  - Copying these 154 files took several retries.
- **The old `rfl` form of `RowRules4At`.** `RowRules4At` must state D-NF in exactly `RowRules4`'s form:
  `0 ≤ beta k x ∧ 8 ≤ … ∧ … < 128 ∧ cap`, with `row_saltDead_card` projecting `hr.2.1` and `hr.2.2.2`.
  - Otherwise `rhoDFp4At_ninety_eq : RhoDFp4At 90 = RhoDFp4 := rfl` fails.
  - Any `Fp4FormingCode.lean` other than `f007cd2999ae` has the old form and breaks it. That includes the pre-edit `e7200cec1d22`, or any copy from before 3:00 PM PDT.
- **The build copy's `lean-audit.json` is the baseline.** `audit.py --update` rewrites it in place, so restore it before the next comparison.
- **The audit printout's "read by" lists** are the module's readers (59), not each definition's (16). Use the per-pin facts.
- **`lean-heavy.sh` blocks head of line.** A second ticket at the same priority can't pass one that is waiting for memory.
- **Two accepted choices** (bc-22298e90, 4:42 PM PDT) that look like bugs but aren't:
  - `c_L` is 0 past the table (m > 2²⁴, k > 2¹⁶ or n > 2¹⁸);
  - D-NF rejects −0 only because in ℚ it is 0, whose byte 0x00 fails `8 ≤`.

I'll start no new work, and I'll answer my replacement's questions here.
