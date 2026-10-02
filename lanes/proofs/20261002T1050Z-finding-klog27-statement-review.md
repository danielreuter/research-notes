---
id: 20261002T1050Z-finding-klog27-statement-review
campaign: e2e-guarantees
lane: proofs
kind: finding
status: final
repo: verity
origin: proofs (bc-8416bc72), statement reviewer for zk-k32k's k_log 27 branch
---

# Statement review: k_log ≤ 27 (#814, `cursor/flock-klog27-95d4` @ `b6b4bf029`): APPROVE

Read: zk-k32k's `audit.py --update` output (`internal/proofs/klog27-audit-update.txt`, proofs' store: the verifier
package verbatim, soundness and level3 PASS lines), its addendum, and the branch's Lean diff against `b8c9dd478`
(`Flock/Statement.lean`, `Flock/HmRow.lean`, the verifier `lean-audit.json`, and the four soundness files).

## The one changed record

`Flock.checkInRange_ok (kLog nRegions mPts : Nat) : checkInRange kLog nRegions mPts = .ok () ↔ kLog ≤ 27 ∧ nRegions ≤ 1024 ∧ mPts ≤ 64`
(was `kLog ≤ 26`; type hash `d5dcd808…` → `7f9f16bb…`). The definition changes the same constant, in the test, the
docstring and the message, and nothing else. The proof is the same case split.

- **It matches the proved range exactly.** The soundness package's `Stmt.InRange` (`FlockSoundness/Accounting/Fast100.lean`,
  unchanged on the branch) is `kLog ≤ 27 ∧ nRegions ≤ 1024 ∧ mPts ≤ 64`, and the pinned table-soundness theorems take it as
  their hypothesis. Before this change the verifier refused statements the proved bound already covered (k_log = 27). Now it
  accepts exactly `InRange`, which is what the pin's docstring claims, so the change makes the pin tighter against its
  purpose, not weaker.
- **Call sites unchanged:** `Stmt.setup` and `Stmt.setupH` both call `checkInRange c.kLog regions.size (PT_LOCAL + nbl)`.
- **Schedule guards** (unpinned, both setups): `c.kLog > 27 || m > 35` refuses. m ≤ 35, where a Fast100 schedule exists, is
  unchanged.

## Nothing else moved

- Soundness (214 pins) and level3 (53 pins): no record changed; their `lean-audit.json` files are unchanged.
- No definition under any package's `reads` changed.
- The four restated soundness theorems (`setupH_spec`, `setupH_spec_typed`, `layout_of`, `templateLayout_of`) are unpinned.
  The first two conclude, and the last two assume, `kLog ≤ 27`, which is what `setupH` now establishes. The pinned
  `Refine.setupH_wf` is unchanged (`StmtWF` bounds k_log by m, not by a constant), and so is its record.
- Consistency with `--zk`: #812's red team computed that the live M1 layout meets `TabZK.M1` up to m = 27, kLog = 27
  (s ≤ 312 of 320 pads per rep, N = 4096), so k_log 27 stays inside that scope as well.

## Limits a citation must carry

- The design owner's conditions (Slack `1790921509.803229`) still apply: the CUDA audit of 2^27-bit blocks by a second
  agent (red-team-proofs, pending), a train with agreement, and BF16 K = 32768 numbers only with both modes accepted and
  zkaudit passing (`klog27-unlanded` until then).
- The branch is off `b8c9dd478`. Its main merge conflicts only in two pod scripts (`74-gemm-hill.sh`, `gemm_hill.py`). If
  the merged `lean-audit.json` is the per-key union, this review carries; if a record moves, it needs a re-read.

Grant: `pr:814@b6b4bf0290a71c5a9d6397bbe35a60abb8c54f72 grant statement-reviewer` ([#814](https://github.com/danielreuter/verity/pull/814)).

**Carried to `cedf5ceae` (4:10 AM PDT).** Main merge of `5f08b1ab2` (main `9699b2f28` + #812). Every `lean-audit.json` at the head equals the per-key union of `b6b4bf029` and `5f08b1ab2` over base `b8c9dd478` (checked key by key: verifier 2 + 42 changed keys, level3 0 + 12, soundness 0 + 376, no conflict), and the branch's `.lean` delta over main is line for line its delta over the base. Plain audits pass on the verifier (17 pins) and `soundness/` (244 pins); no record moved. Red team granted the CUDA audit at `b6b4bf029` (`note:proofs/20261002T1059Z-reply-from-red-team-proofs-554-pr814-pr815`). Label at `pr:814@cedf5ceaee7a560ddde24e62955d22c54ed13f99`.
