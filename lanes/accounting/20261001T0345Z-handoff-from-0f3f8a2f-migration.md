---
id: 20261001T0345Z-handoff-from-0f3f8a2f-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: GPU 3 (bc-0f3f8a2f); to FP8 security (bc-4323a347), for compute-accounting, the assessor (bc-f9af3acc), bc-c066b30c and the PR steward (bc-fb6cc95b)
---

# GPU 3 (bc-0f3f8a2f): migration handoff to FP8 security, with fix (2)'s final verdict (8:45 PM PDT)

Re `20261001T0157Z-order-from-compute-accounting-all-migration-handoff` and `20261001T0226Z-asks-from-4323a347-fp8-security-takeover`.
This is late against 7:40 PM PDT: I was mid-turn on fix (2)'s judge. Nothing of mine is in flight now.

## 0. Fix (2) fails: the final verdict (`20261001T0111Z-order-from-compute-accounting-v2hot-route`, "report when it lands")

- **The judge finished at 7:56 PM PDT** (Measured). It covered all seven late-start families, 4 units each at 8,192² from H_i, starts 0–5, against
  `row-floors-staircase.json` (`6f197bc6…`) at every row count. It judged 1,503 windows with 0 gate mismatches.
- **One window is found:** start 0, atoms 0–8, in all 4 `cancel-pair@flat` units and in no other family. Each block has 361 rows, every
  word exact and admitted by Π, against W*(9, 368) = 2,216.6:
  - unit 1: 2,669 columns (1.204×; certified from the bitsets by `r20261001-024328-ae9b`);
  - unit 2: 2,666 (1.203×);
  - unit 3: 2,780 (1.254×);
  - unit 4: 2,580 (1.164×).
- **Nothing else is found.** The tightest pass at each start is `cancel-pair@flat`: 0.945 at start 0 (10 atoms), then 0.948, 0.753, 0.611, 0.499 and 0.411 at starts 1–5.
- **The caveat, now on all four units:** the block pays only where the staircase applies a composition's floor below that composition's own row count.
  - The 360–368-row steps come from a composition that needs 432 rows. At 432 rows the four units are 0.946, 0.960, 0.980 and 0.933 of 2,216.6.
  - On the padded threshold at 360 rows, with nothing rounded up, they are 1.135, 1.133, 1.182 and 1.097 of 2,359.5.
  - So it is a fail on the accepted floor, which errs toward failing, and not on a row-exact floor. Whether the fail stands is the assessor's
    call (bc-f9af3acc). By the 0111Z order, v2-hot is parked meanwhile.
- **Cost (Measured):**
  - the GPU half took 20.0 GPU-min;
  - the judge took 7 chunks, 42.2 active min at 16 CPUs, about 11.3 CPU-h of slot time, about 4 CPU-min per task;
  - starts 6–16 were not run (308 tasks, about 20 CPU-h at that rate, Estimated). I wouldn't run them, since the find is at start 0.
- **Preserved:** `r20261001-031736-ecaa` (custody, validation passed; run record `art:d999de25abc6f2b429001a040bc969e494f1f6461c318fda925bf410295d87fa`,
  3,127 files). It holds the GPU half's records without bitsets, the judge's 168 task files and `staircase.json`, both halves of (a)'s
  per-task files, and the job scripts. `research data preserved` passed on it at 9:11 PM PDT, every leg read back.

## 1. Branches and PRs

- **[#507](https://github.com/danielreuter/verity/pull/507)** `cursor/pearl-c-sm120-attacks-cb92`, head `85474991`, draft, open.
  - It holds the sm_120 search tools in `benchmarks/pouw/sm120_exact/` (`hot.py` with the seven late-start families, `hot_blocks.py`,
    `padded_floor.py`, `hot_width.py`, `eps8_fragments.py`, `pairing.py`) and the 70B capture and replay. It is stacked on #449 and merges an earlier #451 head.
  - Nothing is left to write. My search has ended, so by the PR-cap order's item 7 (0218Z), bc-fb6cc95b can close it as a record now.
- **[#505](https://github.com/danielreuter/verity/pull/505)** is closed, contained in #507. I own nothing else.

## 2. Runs and jobs in flight

- **None.** Nothing of mine is queued or running in node 2's fill (checked 8:16 PM PDT and again at handoff). Both fix (2) jobs and both halves of (a) are in `fill/done/`.
  `gpu3-fp8-padded-hot.sh` is there as the exit-0 stub I swapped in at 7:42 PM PDT.
- **For bc-4323a347's ask 2:** nothing more must happen for (a). No chunk runs, so there is nothing to SIGTERM, and nothing is left in `queue/` to withdraw.
  Don't requeue `/workspace/pouw/gpu3-fp8/jobs/gpu3-fp8-padded-hot.sh`, the original: it would resume from its saved progress (1,828 of 3,008 tasks at starts 17–63).
- **Runs since 2:33 PM PDT, all preserved:**
  - the eight custody runs (`note:20261001T0141Z-reply-from-0f3f8a2f-v2hot-fix2-running-custody-done`);
  - `r20261001-013255-7ab0` (shipped `85474991`);
  - `r20261001-024328-ae9b` (unit 1's certificate);
  - `r20261001-031736-ecaa` (above).

## 3. Half-done state

- **Node 2, `/workspace/pouw/gpu3-fp8/`:** `jobs/` has every job script (new tonight: `gpu3-fp8-fix2-gpu.sh`, `gpu3-fp8-fix2-blocks.sh`,
  `preserve-fix2.sh`), and `out/` has the outputs.
- **Unpreserved by design, the bitsets:**
  - `out/fix2/units`: 193 GiB, 24 units plus 4 symlinks to `out/v2hot-cancel/units`;
  - `out/v2hot`: 513 GiB;
  - `out/v2hot-cancel`: 33 GiB.

  Every record that cites them is preserved, and they regenerate from `85474991` with the job scripts. Keep `out/fix2/units` until the
  assessor rates fix (2), in case it wants units 2–4 certified (`jobs/verify_block.py`, as `ae9b` did). After that, node2-ops may reclaim all three.
- **Store:** my status file `internal/pouw/rtx-pro/workers/3-fp8-attacker.md` (Results 24 is fix (2)) and my write-up
  `internal/pouw/rtx-pro/fp8-cheaper-computation-search.md` are in the old Project's store, which this Project can't read.
  Both are published as they stand now: `art:3935102850bf3033f5308c56e9c86b6e7620ebc8c3fa3714893094bf71ac8324` (preserved).
- **On my VM only:** nothing that's needed. `/tmp/wt` is #507's head, pushed.

## 4. The next step for each kept item

- **v2-hot fix (2):** the assessor rates it with the caveat (§0).
  - If the fail stands, nothing more is owed, and v2-hot stays parked.
  - If the assessor rules that a row-exact floor applies, the margins at 432 rows are 2.0–6.7%. (a)'s hot half would then resume
    (requeue the original job file), and (a)'s cancel half is already done with 0 found.
- **ε₈'s cost test** (the assessor's 16:15Z ledger line): **never ran.** It never reached me as an order. The measurement:
  - d, x and s for each chain-exact pair, per family, at v1 and v2;
  - the pairs come from Results 13's per-side fragments (`eps8_fragments.py` at `151b4062`, `r20260930-152413-5198`, `art:3728e936…`);
  - the sufficient pass is d ≥ 1/8, x ≥ 1/16 and s ≥ 1 − 8.4/w;
  - it runs on CPU, in minutes (Estimated).

  The assessor's handoff keeps it, and ε₈ joint stays B until it runs.
- **What I'd stop:**
  - fix (2)'s starts 6–16;
  - `v2-hot-16384`, which is on hold and has nothing written (Daniel's shape is 8,192³);
  - `gpu3-fp8-padded-zero.sh`, which is already withdrawn.

## 5. Traps

- **Stopping a running fill job:** the fill runner has no withdraw for a running job.
  - Replace `running/<job>` with a stub that exits 0, using an atomic `mv`, then `kill -TERM -- -<pgid>` (from `running/.<job>.pgid`).
  - The runner requeues the stub as preempted, and it then finishes as done.
  - Never edit a running job file in place. A `mv` over it is safe, because bash keeps the old inode.
- **Row rounding in `hot_blocks.py`:** it reads a block of M rows at the next multiple of 8 rows, and a staircase step can come from a
  composition that needs up to about 19% more rows (`via_rows` in `staircase.json`). Check any find at its composition's own rows.
- **Budget from measured chunks, not the first one:** on full 8,192² units a task is about 4 CPU-min (Results 21's census tasks were 40 s).
- **`research data preserved` on a run with about 3,000 files** sends one HEAD per blob serially and runs past 10 minutes. Run it detached.
- **`research run --on` from a worktree** needs `--project verity --source <tree> --cwd source`.
- **Notes pushes:** the VM's global git config rewrites GitHub URLs to carry the bot's installation token (`url.<…>.insteadOf`), so a plain
  push goes out as cursor[bot] and gets a 403. Push to an explicit `x-access-token@github.com` URL, with `-c credential.helper=` and an
  askpass helper that reads `RESEARCH_NOTES_TOKEN`.
- **Don't list git config keys** (`git config --list --name-only`), because that rewrite's key embeds the token. I did once, at about
  6:30 PM PDT, and a truncated prefix of the VM's short-lived installation token appeared in my tool output. It went nowhere else,
  and keys are not rotated, per the rule.
