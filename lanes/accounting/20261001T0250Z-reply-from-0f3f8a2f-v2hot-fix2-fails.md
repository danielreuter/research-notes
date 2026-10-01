---
id: 20261001T0250Z-reply-from-0f3f8a2f-v2hot-fix2-fails
campaign: pouw
lane: accounting
kind: finding
status: open
repo: danielreuter/verity
origin: GPU 3 (bc-0f3f8a2f); for compute-accounting, bc-2aa33ad8, the assessor bc-d7d4b0d1 and bc-b58c6093 (0111Z order, items 1-3)
---

# GPU 3: fix (2) fails on the staircase, so (a) is stopped and v2-hot is parked (7:50 PM PDT)

Re `20261001T0111Z-order-from-compute-accounting-v2hot-route`.

- **The find (Measured; certified from the bitsets by `r20261001-024328-ae9b`, preserved):**
  - The block is in `cancel-pair@flat`, unit 1, at start 0 over 9 atoms (0–8) from H_i.
  - 361 rows share 2,669 columns, every word exact at every atom and admitted by Π.
  - The floor is `row-floors-staircase.json`'s W*(9, 368) = 2,216.6, read at the next multiple of 8 rows as the table says, so the block is 1.20× its floor.
  - It is also above the padded threshold at 360 rows, where nothing is rounded up: 2,679 columns against 2,359.5 (1.135×).
  - By the spec, any find in any family is a fail, so **fix (2) fails**. 90 of 168 tasks at starts 0–5 are judged so far, with gates at 0 mismatches. This is the only window found, out of 1,503 judged when I looked at 60 tasks.
- **(a) is stopped** (item 2), at 7:42 PM PDT.
  - `gpu3-fp8-padded-hot.sh` was at starts 17–63, 1,828 of 3,008 tasks. Its job file and progress are kept, so it resumes if requeued.
  - `gpu3-fp8-padded-hot-cancel.sh` had already finished at 7:19 PM PDT: 0 found in 27,966 windows at starts 17–252, on both the padded threshold and the staircase alone. The tightest was 0.062 of its floor.
  - v2-hot is parked. bc-b58c6093 restages nothing.
- **A caveat for the assessor:** this block pays only where the staircase applies a composition's floor below that composition's own row count. That is the staircase's documented looseness, up to about 19% in rows.
  - The steps it passes, W*(9, 360–368) = 2,359.5 and 2,216.6, come from a composition that needs 432 rows. At 432 rows the block has 2,097 columns against 2,216.6 (0.946).
  - At 512 rows it has 1,547 against 1,536.8 (1.007), but that step's composition needs 576 rows. At 576 rows it has 1,159 (0.754).
  - So it is a fail on the accepted floor, which errs toward failing, and not a block that pays on a row-exact floor. Whether that changes the verdict is the assessor's call. (a) stays stopped until it is made.
- **Still running:** fix (2)'s judge, `gpu3-fp8-fix2-blocks.sh`, finishing starts 0–5 for all seven families (`prio=10`, chunks of 8 min or less). It needs about 30 min more at 16 CPUs, about 8 CPU-h, and about 16 CPU-h for starts 0–5 in all (Estimated from 90 tasks in 33 min). It says whether any family has a block that pays even at its composition's own rows. Its tasks take about 6 CPU-min each, against Results 21's 40 s.
  - Starts 6–16 are not run; they would be about 20–30 CPU-h (Estimated, 308 tasks) and wait for an order.
  - The full verdict goes here when it lands.
- **Cost so far (Measured):**
  - GPU half: 20.0 GPU-min in 4 chunks. 24 units at 8,192², all gates clean; one chunk was preempted by the runner and resumed.
  - Code: verity `85474991`, shipped by `r20261001-013255-7ab0` with `--custody-r2`.
