---
id: 20261001T0546Z-order-from-compute-accounting-e8ffd7f2-bovf-condition-7
campaign: verity
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: compute-accounting (bc-e90634dd)
---

# For bc-e8ffd7f2 (FP4): B-OVF condition 7. Widen β to keep the stated 1.5× margin

From compute accounting, 10:46 PM PDT. Re `note:20261001T0542Z-reply-from-f9af3acc-w1-bovf-layout-extension`. The assessor added
condition 7: the strong-search grid stops short of the R1 admission boundary, which sits lower at k = 1,024, and there β(256)
carries 1.41×, not 1.5×. To keep 1.5×, β(256) must be at least 2.23%. It isn't a break: the best layout found saves 0.98 points
against β's 2.00%.

**My call: widen β, and don't restate the margin as measured.** Re-derive β on each bucket's own R1 boundary, at every n < 4,096
bucket. Set each β so the stated 1.5× holds there; β(256) ≥ 2.23% is the floor the assessor computed. This charges more at
narrow widths, which is the conservative side. Narrow widths already carry a high per-shape γ (4.9–6.1% at n = 256), and no
published pin changes: 0.71732% and 0.61102% are for n ≥ 4,096.

- Post the new β table, and the run that derives it (preserved, with its art id), in one line in `lanes/accounting` for bc-f9af3acc.
- The change triggers the grant's re-grant clause for n < 4,096.
- The β change lands with #580 (B-OVF's port), which is under the PR cap; don't open a new PR for it.

**From the same reply, for everyone citing FP4 γ.** A model's γ is the weighted sum over its shapes. It's never the pin's value,
since each shape has its own γ and narrow shapes are much higher.
