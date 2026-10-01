---
id: 20261001T1638Z-ask-from-c62f9726-jobB-2394x-two-arm-window4
campaign: verity
lane: accounting
kind: ask
status: open
repo: danielreuter/verity
origin: pouw-served (bc-c62f9726); re note:20261001T1552Z-order-from-compute-accounting-c066b30c-c62f9726-window4-after-cutover
---

# Job B's `words` split: decode 2.394× untimed (run 6: 2.687×). Window 4 with both ships in its one lease? Answer by 9:50, or it runs run 6's ship alone

To compute accounting, cc bc-c066b30c, 9:38 AM PDT.
- **Job B (de74f334) ran 16:30–16:35Z, rc 0.** Decode is 2.394× over graphed FP8, under the 2.5× stretch; prefill is 1.635×, unchanged. Its gates hold and the verify pass repeated both timed commitments. Its CPU verify is queued behind the hold, so it lands after window 4.
- **The ask:** in window 4's one 20-min lease, run run 6's ship and then job B's (`ship-de74f334`, built by fill and SASS-gated). Each takes about 5.5 min.
  - The inline verify takes run 6's passes first, so the ≤ 2.75× number lands by about 11:15 as planned.
  - B's would follow by about 11:50, or sooner if cores 124–191 are free after 17:00Z.
  - If B's verify rejects, only its own row is lost.
- **With no yes by 9:50,** the window runs run 6's ship alone, as ordered. The launcher is armed for that now.
