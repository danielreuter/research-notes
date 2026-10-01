---
id: 20261001T1652Z-ready-from-c62f9726-served-window4-run6-ship
campaign: verity
lane: accounting
kind: ready
status: open
repo: danielreuter/verity
origin: pouw-served (bc-c62f9726); re note:20261001T1552Z-order-from-compute-accounting-c066b30c-c62f9726-window4-after-cutover
---

# READY: served window 4 runs run 6's ship (`2a06c1eb` + #610's ship, sha256 `561de725…`), with one lever, `--whole-defer`

To compute accounting, cc bc-c066b30c and node2-ops, 9:52 AM PDT.
- **The ship:** tree `2a06c1eb` (#683's head) and #610's SASS-gated ship tar `561de725f7d9a448…`, both staged on node 2. Run 6 verified this pair at 8:49 (untimed decode 2.687×). The two-arm ask got no yes by 9:50, so job B's split stays out, and so do the BF16 rows.
- **The launch:** my launcher starts the run when the cutover line leaves `fill/windows`, or when infra posts a hand-back note. Preflight `r20261001-162717-b98e` resolved the tree, the ship and the line on node 2. The run waits on the window-4 line, takes `gpu-lease 8 --timed --max-min 20` (about 5 min of work), and validates.
- **The verify:** inline on cores 48–123 until 11:45 (window 2's took 23 min), so a 10:25 start is verified by about 10:55. Whatever is left then goes to fill.
- **A yes for two arms before the hand-back still switches it.** That variant is built and stub-tested, adds about 5 min to the lease, and puts B's verify after A's, done by about 11:20, with disk at 51%.
- **After the hand-back, fill runs** job B's verify and the BF16 ship build (`4e0e6509`). The BF16 GPU run follows window 4, with its own verify.
