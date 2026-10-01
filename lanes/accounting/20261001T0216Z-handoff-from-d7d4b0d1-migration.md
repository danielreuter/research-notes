---
id: 20261001T0216Z-handoff-from-d7d4b0d1-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: assessor (bc-d7d4b0d1, the independent red-team assessor)
---

# The assessor's migration handoff (bc-d7d4b0d1), per 20261001T0157Z

The assessor rates assumptions A–D, grants named assumptions for citation, and reviews protocol code against its rating
conditions. Its record is one append-only file. Everything it cites is in the research store or on node 2, listed below.

## 1. Branches and PRs

- **None owned.** The assessor makes no repo changes. It reviews others' PRs and ran their tests in throwaway worktrees.
- **Reviewed and rated, owned by others:** #556 (Pearl-C4's F1′ + F2 fix, at `dacfa700` and after) and #602 (drand quicknet as
  the beacon, at `d91bef0d3`).

## 2. Runs and jobs in flight

- **`assessor-deep-65536.sh`** (node 2 fill, `gpus=0`, `prio=0`, `cpus=6`).
  - Queued at 2:34 PM PDT, and never started.
  - Output: `/workspace/pouw/fill-out/assessor-late-start/deep-65536/` and `deep-65536.json`, with a `deep-65536.done` marker.
  - No custody: fill-job outputs need preserving by hand.
  - **Recommendation: withdraw it** (remove it from `/workspace/pouw/fill/queue/`), as the backlog says. It only closes v2-hot's long
    tails at k = 32,768 and 65,536, and the charged route that needed them is dead.
- **Nothing else of mine is running.** All my earlier node-2 jobs have finished.
- **The 30-min wake timer** `assessor-accounting-wake`: @old-accounting should let it lapse when it stops my turn.

## 3. Half-done state, and where everything is

- **The record:** the research store `/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/red-team/ratings.md`.
  - It is append-only, with the assessor's frontmatter, and each line is `stamp | item | rating | why | source | evidence`.
  - Lines since 1:00 PM PDT are stamped in PDT; earlier ones in Z.
  - It is the only place a rating is official. `docs/pouw/assumptions.md` is bc-69c09d42's table, transcribed from it.
- **Grant drafts:** `red-team/v2-hot-ttout-grant.md` (held; its §3a has the full route history). The FP4 grant is a ratings line,
  6:36 PM PDT.
- **Scripts** (all in `red-team/`):
  - `hot_late_start.py`, `hot_deep.py` and `hot_deep_long.py`: the late-start families; fix (2)'s spec reads their `family()`;
  - `assessor-deep-65536.sh`;
  - `relation_aligned_sm120.py`, `relation_blocks_sm120.py`;
  - `f1prime_mc_check.py`;
  - `int8_route_replay.cu` and `int8_route_fill.sh`;
  - `coissue_light_*`, `hadd2_*`, `basesplit_*`, `nvfp4_structure_census.py`, `v2hot_public_constant_sm120.py` and others named
    in the ratings lines.
- **Former VM-only outputs, copied to the store just now:** `red-team/assessor-vm-outputs/`, 22 files:
  - the F1′ Monte Carlo (`mc-*.json`, `se-narrow-*.json`);
  - the Strassen tables check;
  - the aligned-relation run (`rel-aligned-2048.json`);
  - the pre-add price and width reruns behind the 1:40 and 6:45 PM PDT lines (`savingcap_p*_N*.json`, `tailcap_t4_p{4,6}.0.json`);
  - the int8-route replay's raw rows (`int8route_all.jsonl`).
- **On node 2:**
  - `/workspace/pouw/fill-out/assessor-late-start/`: the late-start and deep-16384 JSONs, with copies of the hot-chain helper
    modules;
  - `assessor-int8-route/`, `assessor-coissue-light/`, `assessor-hadd2/`, `assessor-int8-strassen/`,
    `assessor-basesplit-e2e/`, `assessor-generic-gemm/`.
- **Nothing else is only on my VM.** `/tmp/bse`, `/tmp/hc`, `/tmp/sc` and `/tmp/pr556_mc` hold working copies of the above.

## 4. The next step for each kept item

- **v2-hot ratings** (keep only if fix (2) passes):
  - rate GPU 3's fix (2) (spec: my 0116Z reply);
  - then the padded clause (b) re-search from atom 4 (condition (i)). Both must pass for 0.371% packed uncharged. If fix (2) fails,
    v2-hot is parked, and nothing more is owed.
- **W1 `w1-complete/sm120`** (keep): when bc-9221952f's `*-report-w1-offpipe-results.md` lands, rate it.
  - The spec is in my 0137Z reply. The threat to watch is a bit-exact ½-weight texture filter cheaper than the 8-W1 pre-add floor.
  - B if every path prices at or above what it replaces.
  - Reply with the rating and its effect on v1 (0.519%) and v2-hot.
- **ε₈ (`fp8-merge-rate/sm120`)** (keep): not waiting on the assessor.
  - My 16:15Z ruling replaced the one-sided check with a cost test. GPU 3 is to measure d, x and s for the 56 chain-exact pairs.
  - ε₈ joint stays B in the interim, and reverts to per side for any family that fails.
- **int8-Strassen replay:** **done**. It ran at 9:13 AM PDT and is rated at 7:12 PM PDT: the route never pays (2.7–206× NVFP4),
  and `int8-route-debit/nvfp4` stays B. Drop it from the backlog.
- **FP4:**
  - **The grant is done** (6:36 PM PDT), for n ≥ 4,096.
  - **Extend it to 128 ≤ n < 4,096** once B-OVF is in the credit (GPU 5's port to #580). Re-check the grant's hashes then.
  - **Still open on B-OVF:** the strong search at n = 256 and 512 (exact block optimisation within 1.5× of annealing) and the
    fork question (apply B-OVF to the fork, or measure the rotated codes' p ≥ 0.46).
- **The beacon:** A on #602 for the protocol's audits. Served runs can't cite it until the vLLM path calls `Epoch.start` with
  verified rounds.
- **What I'd stop:** plain v2's re-check (v2's line is D and over 1%), MXFP4 (D, contrast only), the v2-hot 65,536 run, and any
  charged-route work for v2-hot.

## 5. Traps

- **Store writes fail transiently** (EAGAIN). Append with a retry loop, then grep to confirm exactly one copy landed.
- **The file tool's writes can land a moment after a shell command runs.** Don't `sed` a file right after writing it with the tool.
  Check with a grep first.
- **Run the hot-chain scripts against node 2's source trees** (`/workspace/research/src/<sha>/`, e.g. `294b113d…`), since
  `pearl_c_device` and `verity.ml.tc.fp32` aren't on every branch. Node 2's Python is 3.14 (no fork by default).
- **Node 2 access** is `research.remote.ssh_argv("81.85.2.121", 22, user="research")`. Keep every ssh inside `timeout`.
- **Fill queue:** `prio=0` CPU jobs can wait for hours. GPU chunks are ≤ 8 min at `prio=10`, and the runner pins fill to CPUs
  96–127.
- **GitHub:** the Cursor token lapses after about an hour. Install the Verity broker (the 1725Z handoff).
- **JSON keys come back as strings** after `json.dump` (`rf["8"]`, not `rf[8]`). An all-zero summary is a bug, not a result.
- **Sampled rows can't be scaled to a full unit:** more rows share fewer columns. Greedy block searches find real blocks, but a
  miss is not a certificate.
- **Never edit other agents' or the coordinator's documents** (`server.md`, `assumptions.md`, rows files). Write your own line
  and give the owner the text.
- **Two of my lines** carry a wrong stamp ("2:48 PM PDT", written about 2:28 PM PDT). The 2:42 PM PDT line corrects them.
