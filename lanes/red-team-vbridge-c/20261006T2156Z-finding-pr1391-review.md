---
id: red-team-vbridge-c/20261006T2156Z-finding-pr1391-review
campaign: proofs
lane: red-team-vbridge-c
kind: finding
status: final
repo: verity
origin: pr:1391@a284f14cda1483ec8aeab85a7c8fae37375aa20a
---

# Red team on #1391 (the verifier's `rec-open` net check, for VBridge G): GRANT

**#1391 at `a284f14cd`: GRANT.** Nothing blocks. The grant label is under `red-team-vbridge-c` with ref this note, and
it is "1 on both" (local and `s3://verity-dev`). One non-blocking finding is worth a follow-up: a file can make the
verifier build an unbounded net before it refuses (section 6).

## 1. Refusal only: holds

- `HmRow.parse` gains one bind, `RecOpen.check c`, after `HmNets.check c` and before `return c`. Since `V` is
  `Except String`, an added bind can only turn an `.ok` into an `.error`; it never changes the circuit returned.
- `check` returns `pure ()` for every unit whose name doesn't start with `rec-open/`. `params` returns `some (L, H)`
  only when the name is exactly `unitName L H`, so a name outside `rec-open/` always reaches the `none` arm and passes.
- Records: all 1678 of `verity/Security`'s guarantee records are unchanged, and the verifier package's 7 old records
  are byte-identical. The verifier gains exactly one guarantee (`Flock.RecOpen.check_ok`). The lock changes are a new
  `Flock.RecOpen` reads group (59 definitions), the `name`/`unit`/`unitNet` projections in `Flock.Circuit`'s group, new
  readers in existing groups, and in Security the digests of `Flock.HmRow` (`parse`) and `ExecCircuit` (`ParseFacts`).

## 2. `check_ok` and `check_congr`: hold

- `check_ok`: from `check c = .ok ()` and `params c.unit.name = some (L, H)` it gives `valid L H = true` and
  `netOf (unitName L H) (unitLaid L H) = .ok c.unit`. That is G's `hl` at `net = c.unit`, nothing weaker, and `valid`
  supplies `H ≤ 16`. The proof splits each arm of the irreducible `check`; no case is closed by anything but `cases h`
  on a `throw` or by the equality the arm tested.
- `check_congr` (name and unit equal implies `check` equal) is proved by unfolding and rewriting. Its two uses,
  `setupH_flatLayout` in `ExecFlatClass` and `setupH_flatFacts` in `ExecFlatCopies`, pass `rfl rfl`, so the kernel
  itself checks that the rebuilt circuit keeps `name` and `unit`.
- `ParseFacts.recNet` and the six soundness proofs' extra `except_bind_ok` step are the mechanical consequence of the one
  bind, and nothing in them weakens a hypothesis.

## 3. The builder is a move: holds

- I diffed `Flock/RecOpen.lean` against D′'s `FlockVBridge` at `b77238f52` (`VBridge/{Sha,Climb,Karatsuba,Residuals,
  RecOpen,Net,Open}.lean`). After normalizing `ℕ` to `Nat`, whitespace, and the renames `bitL`→`byteBit`,
  `lenBytes`→`lenBE`, `zeroPad`→`padZeros`, `preCv [] 0`→`ivW` and `Flock.HmNets.and`→`HmNets.and`, these 33
  definitions are identical: `bitsOf`, `padTail`, `shaMsg`, `blockAt`, `shaBlock`, `shaBlocks`, `shaFrom`, `swap`,
  `climbFrom`, `addL`, `shiftL`, `mulS`, `foldG`, `reduceG`, `Term`, `Res`, `GfS`, `termForms`, `xorL`, `xorAll`,
  `opForms`, `leaves`, `recomb`, `leafSums`, `residual`, `residualsGo`, `residualForms`, `consStructure`, `recOpen`,
  `Ports`, `Ports.bits`, `recOpenNet` and `recOpenOuts`. `sibForms` and `climbRow` equal D′'s `Open.lean`.
- The copies `byteBit`, `lenBE` and `padZeros` equal `Hm.bitL`, `lenBytes` and `zeroPad` up to name. `ivW` differs from
  `preCv [] 0` only in form; `chainV_zero` is `rfl`, so equating them is a short lemma.
- What is new is `ports`, `wordPorts`, `unitLaid`, `unitName`, `params`, `valid`, `unitNet`, `check` and the two
  theorems.

## 4. The replay: passes

`r20261006-205917-caf6`, on vy-nebius-1: `research run --cwd clone --source <worktree at a284f14cd>` of
`tools/lean/audit.py --build --no-runs backends/flock/verifier/lean verity/Security`, in compare mode with replay, from
the run's own clone and `.lake`. It ran 1:59–2:52 PM PDT (53 minutes), rc 0, on source commit `a284f14cd` (clean).

- `backends/flock/verifier/lean` passes: 5723 declarations in 48 modules, 8 guarantees, and the axioms are only
  `propext`, `Classical.choice` and `Quot.sound`. There are no failures. The replay sent 5648 constants through the
  kernel and skipped 75 compiled ones. Its 25 escapes (opaque definitions) are exactly the lock's list, which is
  unchanged from main's; none is in `Flock.RecOpen`.
- `verity/Security` passes: 6860 declarations in 217 modules, 1678 guarantees, the same three axioms, no failures and
  no escapes. The replay sent 6781 constants and skipped 79, the same counts as F′'s audit.
- `verity/Security/Proofs` passes: 57846 declarations in 884 modules, the same three axioms, no failures and no
  escapes. The replay sent 57275 constants and skipped 300.
- Each report equals the lock committed at `a284f14cd`: the verifier's 8 guarantees and 17 reads groups, and
  Security's 1678 guarantees and 513 reads groups. `Flock.RecOpen.check_ok` is recorded with owner `@proofs`, no
  assumptions, and the statement in section 2.
- This replay is not redundant: the author's recorded audit (`r20261006-182350-2e8a`, of `0e6733bd1`) ran with
  `--no-replay`, so this is the first kernel replay of the PR.

## 5. The #1261 claim: confirmed

- Tip 72 (`4464be6cb`, "Merge #1354", which holds #1261 at `878988ce6`) and #1391 merge cleanly
  (`git merge-tree --write-tree` tree `8c5309f37`, as the body says). #1391 onto today's main `d21be99ba`, which lacks
  #1261, is also clean (tree `1ffc394ab`).
- In the merged tree, `verity/Security/lean-audit.json` takes #1391's `Flock.HmRow` digest and `parse` hash. The only
  guarantee tip 72 adds that reads `Flock.HmRow` is `Flock.SecurityProofs.RecursiveSound`, and it is missing from the
  new `Flock.RecOpen` group's readers, so the compare audit needs exactly one `audit.py --update` of `verity/Security`.
  Tip 72's other new guarantees (`RecursiveZK` among them) don't read `HmRow`, and tip 72 adds no reader of
  `ParseFacts`.
- No build break: tip 72 doesn't touch the verifier package or any of the 12 files that step through `parse` or build
  `ParseFacts` (TagsJ, Exec/Merkle, Hidden/Rows, Hm/Accept, Hm/Copy, ExecCircuit, ExecFlatClass, ExecFlatCopies,
  ExecSetup, ExecTemplate, ExecTemplateSetup, Refine/Setup). Its Recursive files take `HmRow.parse … = .ok c` only as a
  hypothesis, nothing else names `RecOpen.`, and there is no namespace clash.

## 6. Cost: non-blocking, with one availability finding

- At real shapes the cost is acceptable: one net build per `rec-open` statement (the body's 7–9 s and about 3 GB for
  2.6M gates), next to parsing the file's own copy of the unit, which is the same size.
- **Finding.** `check` builds `unitNet L H` as soon as `valid L H` holds, and `L` comes from the file's unit name. Nothing
  bounds `L` before `parse` returns: `valid` has no upper bound on `LANES`, and the `kLog > 27` refusal sits in
  `Stmt.setupH`, after `parse`. So a few-byte unit named `rec-open/l<huge>-h16` makes the verifier start building a net
  of about 4374·L rows. It never accepts (the comparison fails or memory runs out first), so soundness is unaffected,
  but one file can exhaust the verifier's memory.
- **Suggested fix.** Before building, refuse unless the file unit's input width equals `(ports L H).bits` summed (or its
  `useful`/`unitLog` matches). Equal nets have equal input groups, so the pre-check refuses nothing the comparison would
  accept, and `check_ok` needs one more `split`. A cap such as `L ≤ 2^20` would also do but is a new policy number.

## Non-blocking notes for G

- G has to get `params c.unit.name = some (L, H)` from something pinned (the statement's shape or the lowering), not
  from the file: a forged unit renamed to something outside `rec-open/` passes `check`.
- G may need the round trip `params (unitName L H) = some (L, H)` (`toString` then `splitOn` and `toNat?`), which this
  PR doesn't prove.
- The agreement test against M0's lowering is not done here, as the body says; the evidence that the copy matches M0 is
  the author's probes plus the D′ move in section 3.
- PROTOCOL §16.10's new bullet ("The nets the verifier builds") and §17.1's D12 agree with the code.
