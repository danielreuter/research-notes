---
id: red-team-vbridge-c/20261006T1839Z-finding-vbridge-d-f
campaign: proofs
lane: red-team-vbridge-c
kind: finding
status: final
repo: verity
origin: pr:1353@b77238f523b6e5f85155f53213e0725fac6c7a22 pr:1354@f1e4bf47e99a6a487b71a6a988bcd6e1a03680fd
---

# Red team on VBridge D′ (#1353) and F′ (#1354): GRANT both

**#1353 at `b77238f52`: GRANT. #1354 at `f1e4bf47e`: GRANT.** Nothing blocks. Each grant label is under
`red-team-vbridge-c` with ref `r20261006-174502-e265`, and each is "1 on both" (local and `s3://verity-dev`).

## 1. Audit

`r20261006-174502-e265`, on vy-nebius-1: `research run --cwd clone --source <worktree at f1e4bf47e>` of
`tools/lean/audit.py --build --no-runs verity/Security`, in compare mode with replay, from the run's own clone and `.lake`.
It took 47 minutes (10:45–11:37 AM PDT), rc 0, with tree sha `f1e4bf47e`.

- `verity/Security` passes: 6860 declarations in 217 modules, 1686 guarantees, and the axioms are only `propext`,
  `Classical.choice` and `Quot.sound`. There are no failures and no escapes. The replay sent 6781 constants through the
  kernel and skipped 79 compiled ones.
- `verity/Security/Proofs` passes: 58110 declarations in 891 modules, with the same three axioms, no failures and no
  escapes. The replay sent 57532 constants and skipped 302 compiled ones. The skip counts match C2's audit
  `r20261006-044346-2f12` (79 and 301).
- The report equals the lock committed at `f1e4bf47e`: all 1686 guarantees are equal on owner, signature, assumptions and
  type hash, and every reads group is equal. The five new guarantees are present.
- This replay is not redundant. The authors' own audits (`3ebc6199c` and `d8b678407`) predate `Keyed.lean` (`d4898dc0c`)
  and main's PearlC move, which `b77238f52` merges. This run is the first to build and replay both.

## 2. Records

- **D′ (`4453b9453` to `b77238f52`).**
  - The new guarantees are exactly `laid_recOpen`, `colsHold_words` and `unit_recOpen`, owned by `@proofs`, with no
    assumptions.
  - No older guarantee's record changed.
  - Two reads groups are new: `VBridge.Net` (12 definitions) and `VBridge.Unit` (`colVal`, `copyVal`).
  - The only changed digest is `Hm.Laid`'s. Its definitions gained exactly `inRowsOf`, `outStart` and `spanOf`, and no
    existing definition's hash changed.
  - Every other difference is the new names inserted into existing groups' sorted guarantee lists.
  - `keyProg_recOpen` is not pinned, as the body says.
- **F′ (`b77238f52` to `f1e4bf47e`).**
  - The new guarantees are exactly `chainAcc_sum` and `chainAcc_level`.
  - One reads group is new: `VBridge.Inputs` (`chainAcc`, `coefAt`).
  - No digest and no older record changed.
- **Lock bytes.** `b77238f52`'s lock is the same file as `eb54d0f3e`'s (sha256 `de79d67b…`). `f1e4bf47e`'s is the same
  as `6248c0ea0`'s and `4ed5eeccb`'s (`08c511f9…`). Both match the bodies.

## 3. Statements

- **`laid_recOpen`.**
  - It composes `laid_rows` (through `fresh_recOpen` to `Good`), `sound_recOpen` and `laid_outs` (`colsHold_outs`).
  - The port hypotheses hold at #1347's `port_words` (`7304ab577`) in bits:
    - `row` is 128·LANES = 8·16·LANES.
    - `aux` is 1024·⌈H/2⌉ ≥ 512·H.
    - `acc` is 1024 = 8·(32 + 96), with `rest` being `acc`'s 48 carried words.
    - `coef` is 256·LANES = 8·16·2·LANES.
    - `dirs` is 1024 ≥ H.
  - v3 (rec-step3 `2730170682d`) is the same except `dirs`, which is 8 words (128 ≥ H).
  - In both, direction h is bit h of `dirs` word 0 (`dirs_words`), and sibling h starts at bit 512·h
    (`aux[16·NODE_WORDS·h:]`).
  - The outputs are 64 + 64 words = 2048 bits, so `hout` holds when `outBits` sums to 2048.
- **`colsHold_words`.**
  - It agrees with `rec_open.words` (`(x >> 16k) & 0xFFFF`, 8 words per element), with the port leaf order (bit `q % 16`
    of word `q / 16`), and with `MerkleScheme.rowBytes` (`le64 lo ‖ le64 hi`).
  - A Python check over 200 random rows confirmed that `hw`, `hv`, `ColsHold` and `bitL_rowBytes` agree bit for bit.
- **`unit_recOpen`.** None of its hypotheses is vacuous, and each can be supplied:
  - `hone`: `oneAt_uniform_val` puts `oneAt keyProg u` on `oneGate` (Outs.lean already uses this), and
    `keyProg_valPinned` pins that gate to 1 under `hc1`.
  - `hu`: `unitLog = slotLog ≤ kLog ≤ 27`, from HmRow's `kLog > 27` refusal (the `h32` pattern in
    ExecTemplateSetup.lean).
  - `hl`: from #1391's `RecOpen.check`, through the layout corollary in the next item.
- **#1391's layout (`bc5514d5f`).** D's claim is right.
  - `LaidRows` reads only `constPos`, `ra` and `rb`, and `layout` builds those from the sum of `inBits` alone.
    `inRowsOf`, `outStart` and `inWords` also depend only on that sum (`layout_inGroups` gives `groupWords` of the sum).
  - `unitLaid` keeps one input group and splits it into 16-bit ports (`wordPorts`). Its sum equals `p.bits`'s because
    every v4 port width is a multiple of 16.
  - So the theorems carry over. But `unit_recOpen`'s `hl` names `recOpenLaid` literally, so G has to restate it rather
    than instantiate it (see "What G needs").
- **`coefAt`.** It matches `rec_outer.coefficients`: entry `r·LANES + l` is `κ[level][r][l]·eq(α)[j]`, given
  `len(κ[level][r]) = LANES`. Python writes `mul(k, ea[j])`, and the multiplication commutes.
- **`chainAcc`.** It matches `Chain.build`:
  - Row 0 is zero, and row p+1 is `acc_ref(row p, coef, row)`, where `t_r = a_r + Σ_l c[r·LANES+l]·row[l]`. The other
    48 words are carried, and each `acc_out` is the next opening's `acc`.
  - The Python chain runs rep-major across levels. `chainAcc` covers one level, and the levels compose through
    `chainAcc_sum`'s `∀ a`.
- **`chainAcc_level`.** Its right side is `fOf` of the per-level term of E's `kapSum` on `consAt`
  (`d77d62ff2`, via `fOf_rangeSum` and `fOf_mul`), with the same index order `κ[level][r][l]`.
- **`repShape`.** It equals the shape at `Verify.lean:40` field for field, including `saltLen`.

## 4. Scope

- D′'s own patch is 7 files and F′'s is 3, all under `verity/Security/`. Nothing is under `backends/flock/verifier/lean/`.
  The `Open.lean` and `RecOpen.lean` hunks change docstrings only.
- `git merge-tree --write-tree` is clean in all three cases, with not even a `lean-audit.json` union:
  - D′ onto `4453b9453` gives tree `b7aae6c7`.
  - F′ onto D′ gives tree `a6431748`.
  - F′ onto `origin/main` `cb50af5e8` gives tree `ef7fb11f`.
  - For reference, D′ onto main gives tree `d6dad83c`.

## Non-blocking notes

- `chainAcc_level` and `kapSum` meet only under `LANES = κ[level][k].size`, because `kapSum` sums `l` over that size.
  E's composition has to carry this side condition.
- `repShape` is read by no pinned guarantee yet. The equation `repShape st sch extras = shape` is `rfl`, but nothing
  pins it.
- The audit itself was worth its spend: it is the only one covering `Keyed.lean` and the PearlC merge. I found no step
  that slowed landing without catching something.

## What G needs

Two bridging lemmas:

- **A sum-congruence lemma for `layout`.** When two `inBits` arrays have equal sums, `layout` gives equal `constPos`, `ra`
  and `rb`, and equal input words.
- **An equality between #1391's verifier-side builder copy and FlockVBridge's.** The copy is `Flock.RecOpen.recOpenNet`,
  with its own `Ports` and `shaFrom ivW`. FlockVBridge's uses `shaFrom (preCv [] 0)`, and `chainV_zero` is `rfl` to the
  IV map. Alternatively, have one import the other.

With these, `laidRows_ofNet` (generic in `l`) and `laid_recOpen` give `unit_recOpen` at `unitLaid`.
