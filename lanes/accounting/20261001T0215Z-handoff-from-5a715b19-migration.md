---
id: 20261001T0215Z-handoff-from-5a715b19-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-5a715b19 (Lean worker under bc-824e54a2; FP4 forming credit, F2 SaltDead, FP4 scale decode)
---

# Migration handoff from bc-5a715b19: Fp4Skip at 90, the F2 `SaltDead` fix and the FP4 scale decode are all in the store; one follow-up is open (the FP4 generator's verity pin)

Per `20261001T0157Z-order-from-compute-accounting-all-migration-handoff`. My backlog rows are in
`20261001T0205Z-reply-from-old-accounting-full-backlog.md`:
- line 67, "the forming-credit and certificate proofs (bc-5a715b19)", keep only what feeds a pin;
- line 68, the monotonicity lemma, queued, and Daniel decides.

`S` below is the old Project's store, `/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b`. The Lean package is
`S/lean/submissions/pouw`.

## 1. Branches and PRs

None. I have no verity branch and no PR, and this file is my only research-notes commit. My work reached the store
through the merger (bc-3cdbf3c1) or through guarded writes of my own.

## 2. Runs and jobs in flight

- None. No research runs, no fill jobs, nothing on node 2, and nothing of mine on the VM's `lean-heavy.sh` queue.
- I closed my last tmux sessions (`mem-watch`, `g-pipe`, `g2-gen`, `m4-scaledecode`). All four were idle except
  `mem-watch`, a memory logger.
- Nothing needs custody or preserving by hand.

## 3. State, and what was only on my VM

**In the store, done** (`S/lean/submissions/pouw/Pouw/PearlC/`):
- **`Fp4Skip.dead` at 90:** `Fp4Skip.lean` `b4041ddd…` and `Fp4Freeze.lean` `7ddc8dfe…`. Written about 7:47 AM PDT
  Sep 30, after a green `check.sh` (inbox 14:56Z).
- **The F2 `SaltDead` fix:** `SaltDead.lean` `b37fcba3…`, `Forming.lean` `0721b95a…`, `AtomErr.lean` `ac785b56…` and
  `FormingP.lean` `03bb4260…`. They landed with M1, whose write-back ran at 9:19 AM PDT Sep 30. RowSeed's 11 `SaltDead`
  readers carry the post-M1 digest `a37bdcc5…`.
- **M4, the FP4 scale decode:** `scaleDyadic .ue4m3` reads the low 7 bits, as the card does. NVFP4 only.
  - Files: `Fp4.lean` `07258f8e…`, `Fp4Vectors.lean` `efb0b211…` and `Fp4Checks.lean` `80812c89…`.
  - Merged 11:37 AM PDT Sep 30 as `art:2d6d7cb40e8672cf7771569b6b05fce3df2104c328009f9504d32e9af670b786`. `check.sh`
    passed, and `lean-audit.json` became `7baf34fe…`.
  - The only moved record was the read `Pouw.PearlC.Fp4` (`scaleDyadic`), for four TileBound pins. bc-22298e90
    reviewed it.
  - The coordinator copied the generator and its coverage record into `S/internal/pouw-fp8/pearl-c-scripts/`:
    `pearlc_fp4_vectors.py` `3e8f57cd…` and `pearlc_fp4_vectors.json` `fac1a3a9…`.

**My documents in the store:**
- `S/internal/pouw-fp8/pearl-c4-atom.md`: the FP4 atom, conformance, `Fp4Skip` and `Fp4Freeze`. §3.1 covers the scale
  decode.
- `S/internal/pouw-fp8/pearl-c-forming.md`: the forming credit (β folding `√32/(256·16)`, §7).
- `S/internal/pouw-fp8/pearl-c4-scale-decode/`: M4's staging, now merged. It holds the review packet
  `statement-review-scale-dyadic.md`, `M4.json`, `SpecialsControl.lean`, `ScaleDyadicReview.lean` and `discriminate.py`.
  These are review aids, and nothing there lands again.

**VM-only material, copied now** to `S/internal/pouw-fp8/vm-5a715b19/` (new): 51 files, 1.2 MB, checked against
`sha256.txt` (`3baa689f…`).
- **`g1/`, task G's driver:**
  - the scripts `drive.sh`, `step.sh`, `pipeline.sh`, `store_write.py` and `WitnessG.lean`;
  - the six files before the change (`base/`) and as landed (`new-f2/`, `new-fp4/`);
  - the forming-doc drafts (`doc/`), the store and mirror snapshots, and the logs.
- **`tools/`:**
  - `guarded.py` does store writes guarded by a base hash (replace, append, create, remove), with retries on
    `BlockingIOError`.
  - `moved_records.py` compares two `lean-audit.json` files: moved pins, reads, assumptions and layers.
- **Not copied:**
  - `/tmp/g2/verity`, a verity checkout at `29f691be`. Re-clone it.
  - `/tmp/m4`, M4's private build, which the merged store supersedes.
  - The other drafts under `/tmp/g2`.

## 4. Next steps

- **`Fp4Skip` 90 and F2 `SaltDead`:** done. Nothing is left; stop.
- **M4's follow-up**, asked for at 10:55 AM PDT Sep 30: bump the generator's pin from verity `29f691be` to #534's merge
  commit, and drop the override.
  - It's blocked on verity PR #534, which is OPEN at head `b466fd9e`. It's in the next merge train with #449, #548, #556
    and #602.
  - When #534 is on `main`, work in a copy of `pearl-c-scripts/`, never in the store:
    1. Set `COMMIT` (line 53) and the usage line to the merge commit.
    2. Delete `_model_scale_dyadic`, `_sm120_scale_dyadic`, and the `models._scale_dyadic = …` line with its comment.
    3. Reword the module docstring's override sentence if needed.
    4. Run with `PYTHONPATH=<verity at that commit>/packages/verity/src`, and keep
       `--captures internal/pouw/rtx-pro/handoffs/scale-dyadic-bit7-words.json`.
  - **What to expect** (see the first trap):
    - `Fp4Checks.lean` stays byte-identical (`80812c89…`).
    - `Fp4Vectors.lean` and the coverage record differ only in the commit string.
    - Any other differing byte means stop and find out why.
  - **Landing:**
    - The script and its record replace the two files in `pearl-c-scripts/`, guarded by `3e8f57cd…` and `fac1a3a9…`.
    - The new `Fp4Vectors.lean` header changes only a module docstring, so no audit read moves. It rides with the next
      Lean merge.
- **Monotonicity lemma** (line 68): not started, and no files exist. It's queued after TT_OUT rev2, and Daniel decides.
  I'd stop it unless a pin needs it.
- **Stop:** nothing else of mine is open.

## 5. Traps

- **"Byte-identical" can't hold literally for two of the outputs.** The generator writes `COMMIT` into
  `Fp4Vectors.lean`'s header (line 3, `` from `verity.ml.tc` at `29f691be` ``) and into the coverage record's `models`.
  So after the bump, those two files differ in exactly that string. `Fp4Checks.lean` has no commit in it.
- **verity `main` is 443 commits past `29f691be`, and `models.py` changed in that range.** #534 touches `models.py`,
  `kernels.py` and `pearl_c4.py`, and not only `_scale_dyadic`.
  - The generator asserts both atoms' parameters, so a parameter change fails loudly.
  - A changed word shows up only in the diff, so read it.
- **The four specials rows 12, 19, 21 and 23 carry the card's words.** The Python model refuses them even after #534 (a
  NaN accumulator raises `InvalidArtifact`). Keep `--captures`, which also checks the 13 in-model words against the card.
- **The generator doesn't create its output directory.** Create `<out>/Pouw/PearlC/` first.
- **Don't run Python inside the store.** It leaves `__pycache__` there (`pearl-c-scripts/` already has one). Copy the
  script out first.
- **Store reads and writes sometimes fail with `BlockingIOError` (EAGAIN).** Retry, and guard every write by its base
  hash (`tools/guarded.py`).
- **Old-VM habits that won't carry over:**
  - `check.sh` never ran in the store.
  - Heavy Lean steps went through `/home/ubuntu/lean-heavy.sh <label>`, whose label sets the priority (`fp4-const*` is
    3).
  - A new VM won't have that script.
- **Any change to `Fp4.lean`'s definitions moves the `Pouw.PearlC.Fp4` read** of the four TileBound pins
  (`realizesAt_nonvacuous`, `realizes_out_at`, `tile_chain_satisfiable`, `tile_cost_ge_of_gates`). That needs a named
  statement reviewer.
- **M4 makes `e4m3(β)` for β < 0 decode as |β|.** At β = −1/4096 the byte `0x80` is a zero scale.
  - The D-NF rule `0 ≤ β ∧ 8 ≤ v ∧ v < 128` closes this. It was GO'd at 1:49 PM PDT Sep 30 for `RowAdmit4`,
    `RowRules4` and `RowRules4At` (bc-ae19a858's staging).
  - Anyone touching FP4 row admission must keep it.
- **`git grep` over research-notes `origin/main` takes about 9 minutes** in the sparse checkout. Use
  `git show origin/main:<path>`.
