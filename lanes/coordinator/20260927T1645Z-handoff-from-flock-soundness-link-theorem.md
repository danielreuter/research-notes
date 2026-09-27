---
cursor:
  subagentId: "bc-9e538dc5-64c5-5aad-b845-7ae98c178569"
---

lane: coordinator · kind: handoff · from: flock-soundness · created: 2026-09-27T16:45Z · re: your 16:02Z message (continue with the link theorem; hand #163 over when final)

# #163 is ready for audit: the link theorem is proved

[#163](https://github.com/danielreuter/verity/pull/163) is at head `7516258b`, stacked on [#127](https://github.com/danielreuter/verity/pull/127) (ready, `f117f52b`), so the merge order is #127 then #163.

**What it proves.** `flock_batched_linkSoundE` (`Audit/FlockLink.lean`) discharges `LinkSound` for the batched audit with the expected-time extractor (`analysisBE`) and the plurality value layer:

$$\delta_{\rm link}\le\frac{Q_s}{1-\rho}\Big(\frac{2(1+k)t'}{2^{256.5}}+\frac{1}{eM}+\frac{k}{eR_w}\Big).$$

- The reruns are conditioned on the whole session accepting.
- The finder is an explicit game, one per commit string, with expected cost `2t'(1+k)`.
- The `4N₀/e` averaging variant is recorded as a one-bit refinement for later, as you asked.
- Standard axioms only; 223 entries in `Check.lean`.

**Its hypotheses.**
- **A2 for each explicit finder** (`hCR`). A prover that hard-codes a collision makes it false, and then the theorem says nothing about that prover.
- **The wire-to-commit-string binding** (`ValueBinding`), named as you asked. It is data plus specifications, since the finder calls its `opening` and `collide`. M0's `hm96-sha512` layout discharges it.

**What to check in the audit.**
- `t'` has to count every SHA-512 evaluation of one session run, the prover's and the verifier's.
- `trialG` draws uniformly among draws that read the target string, which is legitimate for a reduction: the prover's strategy is defined for every draw.
- The test fix: `test_audit_layer_is_abstract` now lists `FlockBatchedAcc.lean` and `FlockLink.lean`. The first was already missing from it on #163's S3 commit, so the test would have failed there.

**One decision for Daniel: `Q_s` instead of `N_s`.**
- **What the proof gives.** The bound is `Q_s`, the expected number of commit strings the drawn units read, which is at most `N_s`, because the finder draws only unit sets that read its target. So the proof gives the record with room to spare.
- **The numbers.** Audit B is `t·2^-209.9`, against the record's `t·2^-205.6`, and `N·t ≤ 2^81.9` over a lifetime at `2^-128`. The gains are 3.7, 4.3, 10.3 and 13 bits for audits A–D.
- **The choice.** The record could be restated with `Q_s`. That costs a docs change in `DESIGN.md` §3, `ASSUMPTIONS.md` A2 and the lifetime doc, and no Lean.

**The buy-back list for Daniel** is in my lane report, `internal/lanes/flock-soundness/20260926T1950Z-report-flock-soundness.md`, section "Buying back lifetime budget on the link term". It is a short table:
- `N_s → Q_s`: analysis only, now proved.
- The first-recovery variant: 1 bit.
- A smaller `N₀`: about a bit per step of m.
- Row leaves instead of value leaves: 9 bits.
- A wider leaf hash: the term vanishes.
- An extractable or clear value layer: the term goes.

**Documents.**
- **Created:** this note.
- **Updated:**
  - my lane report: the section above, and checkpoints `7516258b` and `0ab7224d`;
  - `internal/lanes/flock-soundness/20260927T1510Z-draft-expected-time-link-plan.md`: marked done, with the changes from the plan;
  - `internal/lanes/audit-lean/20260927T1535Z-handoff-from-flock-soundness-expected-time-link.md`: the final names.
- **Directories:** no changes.
