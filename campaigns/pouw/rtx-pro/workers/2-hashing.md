---
cursor:
  subagentId: "bc-7442ca43-9389-5653-ae57-2cbf499a9569"
---

# GPU 2: the shared hashing module (FP8 and FP4) and the FP8 epilogue fusion

Worker bc-7442ca43. On node 2 every GPU job runs under `gpu-lease 1 --wait` (named with `GPU_LEASE_WHO`), bounded to 30 minutes inside the lease, and the UUID each run got is recorded with it.

## 7:11 PM PDT: migration handoff written; the `-h2` hash bench finished and is preserved

- **Handoff:** `lanes/accounting/20261001T0210Z-handoff-from-bc-7442ca43-migration.md` (notes push got a 403, so it is staged in
  `internal/pouw-fp8/accounting-outbox/`). I start no new work.
- **The fill:** all 8 jobs done by 7:00 PM PDT, 208 chunks rc 0, 832 gates ok and 0 failed, 5,097 rows (Measured, diagnostic).
  Output preserved as `art:ad4999c6205fba59a28db6aea0ec9e9a41503cc86b56123c10713b00b215b6d0`; the per-die table is not written.
- **Node-2 access is back** (7:06 PM PDT) through `research pods ssh vy-nebius-2` after recloning the notes repo.

## 3:43 PM PDT: the `-h2` hash bench queued as fill on every die (`gpu2-h2hash-die0.sh` … `die7.sh`, ≈ 8.7 GPU-h)

The coordinator's 3:02 PM PDT item: the `-h2` hash bench at every panel shape and on every die, bit-exact gated, untimed
screen, as preemptible fill.

- **Code:** `cursor/h2-hash-bench-9569` (`f4f4bb8c6`), on #596's head `05ce9ce49` (the served path: GPU 1's in-kernel `-h2`
  segment keys `997ac6bd` and the decode spread). It holds `benchmarks/pouw/pouw_hash/h2_bench.py`, `h2_ship.sh`, `h2_fill.sh`
  and a test (`benchmarks/pouw/tests/test_h2_bench.py`). The test holds the gate to `fixture.py`'s layout and shows that a
  flipped byte in each hashed buffer is caught; 18 pass.
- **What a run does:**
  - First run.py's fixture check.
  - Then, per variant (sm120, sm120-unpromoted) and format (`-h2`, then `-h1` in the same process), the pipeline at the
    shape, with a bit-exact gate before any timing. The gate is sampled at a fixed seed and checks against frame-b3s or
    frame-b3 and Pearl-C's digests:
    - node keys and `-h2`'s segment keys;
    - row and tile-tree leaves, pads, nodes and root;
    - digests against C~ ‖ U, and all of them against `hash_msg`'s (so the fused digests too);
    - tile leaves.
  - Then CUDA-event and CUDA-graph medians of every hashing step: the call's hashing chain, A's commitment, the digests (the
    fused price is `gemm_pearlc_b` less `gemm_pearlc_s`) and the tile leaves and tree, with gemm_ct and the plain GEMMs for
    scale.
- **Ship:** `/workspace/pouw/gpu2-h2hash/ship` (`h2ship.tar` sha256 `189c8bf5…`), built by build.sh at `05ce9ce49` with nvcc
  13.0.88, no FTZ flag, SASS gate passed. The cubin sha256 is `8acc10ea…`.
- **Jobs:** one per die, `on=<die>`, `gpus=1 prio=10 max_min=8`, each checking the lease UUID against the die table. Each job
  is 26 chunks: the 13 shapes of `hashing-forms-by-shape.md`, twice, each chunk one fresh process of 2.5 min (dies 1, 3 and 5, 3:45–3:47 PM PDT: every gate passed, exit 99). The job
  exits 99 while chunks remain and 143 on SIGTERM, which doesn't count toward the 5-start limit. Output goes to
  `/workspace/pouw/fill-out/gpu2-h2hash/die<N>/`.
- **Validated before queueing:** two direct 1-GPU leases, 3:30–3:32 PM PDT on die 7 (GPU-af0bf9e0) and 3:34–3:36 PM PDT on
  die 1 (GPU-fb680060). Every gate passed: 32×8192×8192, 2048×8192×8192 (fused) and 32768³ (fused), both variants, both
  formats. The GPU was busy 93% of the lease.
- **Queue history:** queued at 3:36 PM PDT. All 8 jobs were preempted at 3:41 PM PDT by a whole-node window, so I split the
  chunks from 5.2 min to 2.5 min and swapped the queued scripts at 3:43 PM PDT.
- **First numbers (Measured, diagnostic: untimed screen, CUDA-graph medians, sm120):**
  - Clocks per NVML: 2,092 MHz at light load. The 32768³ GEMM rounds were power-capped at 1,965–1,980 MHz (throttle 0x4).
    Every row carries its clock record.

    | shape | call hashing, `-h2` / `-h1` (ms) | A's commitment (ms) | tile leaves + tree (ms) |
    |---|---|---|---|
    | 32×8192×8192 (dies 7 and 1 agree to 0.1 µs) | 0.0534 / 0.0675 | 0.0209 / 0.0361 | 0.0278 / 0.0268 |
    | 2048×8192×8192 (die 1, fused) | 0.2082 / 0.2376 | 0.0906 / 0.1204 | 0.0524 / 0.0514 |
    | 32768³ (die 7, fused) | 7.4–8.5 / 12.3–13.3 | 3.09 / 8.35 | 0.81 / 0.81 |

  - The per-die table comes when the jobs finish. It goes to the store with `research data put`, not Git.
- **Shortcuts, flagged:**
  - The domain bindings, E_B's line key and the unit block are stand-ins; the digest keys are Pearl-C's.
  - The CUDA graphs replay L2-warm back-to-back copies.
  - The CPU gate samples the wide levels and leaves; narrow levels are checked in full.
  - seed_line_a is timed, but gated only by run.py's fixture check.

## 18:12Z: the self-recording pilot: attempts 67 and 68 re-measured and kept (`r20260930-174917-2585`, done)

- **Verdict** (`verify.py --tier 2b`, verifier `0cb23bfd`): ACCEPT for both arms at both shapes, and REJECT for all four
  no-write controls (root_A and the tile root read `a5a5…`, and every drawn tile fails its activation opening). Every gate
  passed, and known-bad was rejected. The run ended SUCCESS (rc 0) at 18:01:34Z.
- **Results** (Measured, locked-2100 on GPU 0 `GPU-5f1149a4-e5f5-1007-ec78-7cd350a69a4f`; the reps' SM clocks were
  2,070–2,092 MHz for the arm and 2,085 for the baseline; γ is the record's, Derived):

  | attempt | prefill m8192 (hash-free) | decode m32 (hash-free) | γ |
  |---|---|---|---|
  | 67, v1-h1 | 1.8043× (1.406×) | 3.4645× (2.1137×) | 0.519% |
  | 68, v2-h1 | 1.7665× (1.3608×) | 3.3518× (1.9998×) | ~~0.371%~~ withdrawn, compute-accounting 3:25 PM PDT: v2 is D, at least 0.946% packed |

  These are the first verified measured Pearl-C sm120 rows at the headline shapes. Against the 12:40Z unverified rows of
  the same attempts (`r20260930-122529-fb8b`), prefill is 0.8% and 0.7% slower, and decode is 8.7% and 10.4% faster. I have
  not looked into why decode moved.
- **Records** (`kernel-attempt/v1`, variant `pearl-c-sm120/05d7b3d5c609`, all labelled `kept` by bc-7442ca43 with the run as
  ref): 67 prefill `art:531a09f34b43f530794bac9e268f0369e2aba22d4128f5ca5ac0a6f826ff919c`, 67 decode
  `art:cf03727028346f5ba79971bc934a67641a44657f3f5bec2f28fdf1a7efa25d9e`, 68 prefill
  `art:2820da4d327fde46d3c4f5ca4c3ed17895c24ba84ff666c2e10aa3e1269214c3`, 68 decode
  `art:f8bef4789c75d6e75892ee1ed7be2691e8b71caf7b5463c0f4f69453807ebce9`. The run's Attempt and run record
  (`art:88e9d48b…`) reached the store from the pod.
- **Panel:** `panel.py render` at 18:11:40Z printed "219 rows, 4 from the evidence store". Its line summary now shows
  v1-h1 at 1.8×/3.46× (#67, measured) and v2-h1 at 1.77×/3.35× (#68, measured).

- **The run:** `r20260930-174917-2585`, from `0cb23bfd` (`cursor/pearl-c-sm120-pilot-run-9569`, pushed): my `e0902b4a` on
  GPU 1's `b6a91929`, merged with #491 `e22a2808` and #583 `65e70059`. `gpu-lease 8 --wait --timed --max-min 20` got the
  whole node at 17:50:29Z; `research run --no-sampler`. `run.py`'s check passed first, then the harness's gates. After the
  lease, in the same job: `verify.py bench.json --tier 2b --publish --push --by bc-7442ca43 --hypothesis ...`. No hand
  `panel.py append`.
  - Ship: cubin `6047f75a…` (the same bytes as GPU 1's ship13), tar `7e67ce75…`, built with nvcc 13.0.88 from `0cb23bfd`
    (clean). Harness build `art:3bf425e6…`. `PEARLC_A_FORMS=p,fold` (the forms 67 and 68 ran), forming `split`, epilogue `b`.
  - Lineage (`PEARLC_LINEAGE`): parent `art:c78dfb0c…` (the run record of attempt 67's run `r20260930-122529-fb8b`, which
    predates the ledger), panel attempts 67 (v1-h1) and 68 (v2-h1). Variant `prices` = `cast-8.72` (form_s5's packed cast).
- **The arm on interface v0.5 (`e0902b4a`, on `cursor/pearl-c-sm120-h1-commit-9569`):**
  - `dump(dev, call, shape, dir)`, so `bench.poison_dump` makes the transcript and the no-write control. Your writer is
    renamed `write_transcript` (v0.5's harness calls any `dump` it finds, and yours had another signature). The rows are
    written once per shape.
  - `call.transcript_buffers`: every set buffer but the tensor maps and the counters `ctr_a`, `ctr_b`, `ctr_t` (`UNPOISONED`),
    plus a padded A's real rows. **GPU 1: your `poison()` filled the counters with 0xA5.** `atomicInc` over 0xA5A5A5A5
    restarts at 0, so no CTA sees itself last and the one-launch trees (`p,one`, `p,fold`, `s,one`) never fold their top.
    Only `w,nodes` was unaffected. `poison()` now fills exactly `transcript_buffers`.
  - The build record names `variant` (`ledger.variant_record`: family `pearl-c`, device `sm120`, both schemes, the cubin's
    include graph and `run.py` as sources) and `lineage` (the forms' mechanism tags, panel line and version, phase groups; no
    γ), and the verifier's `control`. Without #583's `ledger.py` the build names no variant.
  - Tests: 15 arm tests pass on the branch and on the run tree against the real v0.5 harness, with a new harness-dump test
    under both forms and a build-record test; #583's 108 harness and ledger tests pass on the merge.
- **What the pilot measures** (updated as runs land):
  - Runs with a record: 1 of 1. verify.py wrote all 4 records into the run's `ledger/`, but 0 of 1 runs published them
    itself.
  - Minutes from a run's end to its panel row: 10.1 (18:01:34Z to 18:11:40Z). About 5.5 of those were a cold refresh of the
    store index, because this VM restarted and lost `~/.research`. Publishing, labelling and rendering took 38 s.
  - Rows that needed a hand append: none. One hand step was still needed: `ledger.py publish RUN --by bc-7442ca43 --push`,
    run from this VM for all 4 records (see the first finding).
- **Pilot finding (bc-1a23b70c, coordinator): no pod run can publish its own records.** On the pod, verify.py's
  `--publish --push` printed `ledger: not published (StoreError: no remote configured ...)`. This is by design:
  `research run --on` stages the store's custody key for the runner only, never in the workload's environment
  (`research/remote.py`, `store/custody.py`), so the workload can't reach the store. Until the runner's post-run custody
  step publishes a run's `ledger/` records itself (my recommendation: the runner already publishes the Attempt with that key),
  every pod run needs a hand `ledger.py publish` from a machine with the store. No `kernel-attempt/v1` record was in the
  store before these four.
- **Pilot finding:** `panel.py render` looks for `ledger.py` at `/workspace/benchmarks/pouw/harness/ledger.py` by default.
  On a checkout of `main`, which doesn't have #583 yet, it prints "no ledger.py; the log alone" and renders no store rows.
  I rendered with `VERITY_REPO` set to the run tree.
- **Pilot finding (coordinator, pous root): the records' γ is below the versions' published γ.** The records carry
  0.519% (v1-h1) and ~~0.371%~~ (v2-h1; withdrawn, compute-accounting 3:25 PM PDT: v2 is D, at least 0.946% packed), from the harness's staged `price_twins.json` (cast-8.72 at FADD 1047/125). The panel's
  published γ for the same versions is 0.779% credited and 1.226% chain-only for v1-h1, and 0.647% for v2-h1 (superseded too: v2 is D). The plot
  uses the row's γ. Which γ a store row should carry is a statement question, so it isn't mine to settle.
- **Not noisy:** the lease's usage record says GPUs 1–6 were "busy 10 s of 10 s sampled". That comes from the one boundary
  sample at 17:50:29Z: its util was 0, but its SM-activity figure averages the previous holders' last seconds. From
  17:50:39Z the node sampler was quiet for the whole timed window, and only lease waiters were present. (For ops: the
  usage record counts the boundary sample as busy.)
- **Pilot finding for bc-1a23b70c:** the variant id can't tell `PEARLC_A_FORMS` apart. The forms pick kernels at run time
  from one binary and one set of sources, so `w,nodes` and `p,fold` share an id. The arm records the forms in the lineage's
  mechanism tags and in the build record's `forms`.
- The harness worker's v0.5 hook `transcript(dir, read)` is superseded by #583's `dump` (server.md 17:31Z). This arm uses
  `dump`.

Branches (all pushed):
- **`cursor/pearl-c-sm120-h1-commit-9569`, head `e0902b4a`: the arm on interface v0.5 (17:55Z, above) on GPU 1's `b6a91929`.**
  Before it, `b0820016`: the `-h1` stack on GPU 1's head (13:25Z). GPU 1's
  `cursor/pearl-c-sm120-h1-b44b` at `f0f9b1ab` merged with my `pouw_hash/h1_sm120.cuh` kernels (`1f582885`, `9bc8c570`,
  `c3699c38`, `9eaa7882`, `55449a2f`), the `fold` forms in `run.py` (`dddf3378`; since `71dbfa72` opt-in, below), the level-key
  table (`05518d7f`) and #449's fake driver fix (`ea17cefb`). 318 tests pass (`test_pearl_c_sm120.py`, `test_h1_sm120.py`, the
  nvcc 13 sm_120a build test included); #540 at `304436d3` passes its 44 device-path tests merged with it, as on its own head.
- `cursor/pearl-c-sm120-h1-9569`, head `98b142c0`: the earlier `-h1` fusion (`f2e5a32e`, on #449 `61d0298d`); superseded by the
  stack above, whose digest is GPU 1's copy of it.
- `cursor/pouw-hash-sm120-9569`, head `4a4fde4f` ([draft #506](https://github.com/danielreuter/verity/pull/506)): the module.
  **The pinned key is in** (`ceac4f13`: `pearlc::h1_msg_key`, k_msg = blake3("pearl-c/h1/message"); no stand-in left).

## -h1 decode: A's commitment and the tile hashing in one launch each (current; 12:40Z)

**The kernels** (`benchmarks/pouw/pouw_hash/h1_sm120.cuh`, launched under `PEARLC_A_FORMS=p,fold`; since `71dbfa72` the default
is GPU 1's `w,nodes` again, so #540's steps, buffers and `Pipeline.levels(tag, count)` are unchanged):
- **`h1_commit`**: A's whole commitment in one launch. A warp per row hashes the row leaf (`row_leaf_v`, a lane per 1 KB
  chunk). The last CTA by an `atomicInc` counter (after `__threadfence`) reads the other rows' nodes through L2 and folds the tree.
  Its thread 0 then derives seed_A (keyed by the unit block's `blake3("pearl-c/v0/seed-A")`, over salt ‖ root_A ‖ root_B ‖ index)
  and E_A's line key. It replaces `h1_rows_p` + `h1_tree` + `seed_line_a`, where the tree is at most twice the CTA wide (decode:
  32 rows, one warp a CTA). 80 registers, no local memory, no FP32.
- **`h1_tiles`**: the unfused call's hashing in one launch. A CTA per 64 × 64 tile: a thread per message digest, 4 chunk
  hashes, the tile leaf and its level-0 node, then the last CTA folds the tile tree. It replaces `hash_msg_v` + `hash_leaf_p` +
  `h1_tree` where the tile tree is ≤ 256 wide (decode: 128 tiles). 64 registers, no local memory, no FP32.
- Both are held to the multi-launch kernels, #449's references and `MerkleTree` on the host (`test_h1_sm120.py`'s twin,
  with and without the level-key table). On the card, run.py's 99-buffer check and the arm's gate relaunch (ALT_FORMS) compare them word for word.

**Timed** (`r20260930-122529-fb8b`: harness `8d04bfe5` with build `art:14fff942`, one-GPU lease on GPU-fb680060, locked-2100, SM
2,077–2,092 MHz every rep for arm and baseline, no clock gap). Gates passed first: run.py's check, then every harness gate and
negative control. **The reference verifier (`verity_pouw.audit.Verifier`) ACCEPTs all 4 transcripts.** Times are graph medians of
20 reps (Measured); ratios are over the same run's cuBLASLt FP8 (Derived):

| Arm | Prefill 8,192³ | Decode chain, serial | Decode, side stream | Hash-free (prefill / decode) |
|---|---|---|---|---|
| v1-h1 | 2.6065 / 1.4559 = **1.790×** | 0.19868 / 0.05234 = **3.796×** | **3.321×** | 1.396× / 2.412× |
| v2-h1 | 2.5550 / 1.4559 = **1.755×** | 0.19582 / 0.05234 = **3.741×** | **3.266×** | 1.351× / 2.359× |

- **Panel attempts 67 (v1-h1) and 68 (v2-h1), estimates.** The verifier accepted them, but #491 has no poisoned dump and no
  negative-control arm (the 11:50Z rule). The SASS gate also ran with a run-tree patch: at `8d04bfe5`, `discover()` refuses the
  `/dev/zero (deleted)` mapping that appears right after the arms' `build()` (`r20260930-122014-33bb`, exit 7). The patch records
  it as not scanned (Needs 2).
- **NVML flagged the software power cap (0x4)** on most prefill items of both sides, at 298–443 W of the 600 W limit, with the
  clocks unchanged (2,077–2,085 MHz per rep on both sides). Decode had none. Run 2 on GPU-5f1149a4 had none either.
- **Prefill moved from 2.128× (attempt 49) to 1.790×, mostly from GPU 1's mainloop.** run.py, same run: GEMM 1.556 ms,
  forming 0.453, clean-up 0.117, commit 0.297 (A's rows 0.260, tree 0.024, seed 0.013), hashing 0.319 (fused digests ≈ 0.236,
  leaves 0.056, tile tree 0.027).
- **Decode moved little under the graph: 3.822× to 3.796×.** The before phase went from 0.0959 to 0.0946 ms and the after phase
  from 0.0332 to 0.0304. run.py's eager call (streams, no graph) shows a larger gain: its hashes cost 0.0616 ms, against 0.0784
  in run 2. The graph had already removed most of the launch gaps.
- **What bounds A's commitment at decode: its serial compressions, about 32 on the critical path.** These are 16 + 1 for the
  row's chunks (33 chunks for 64 + 32,768 bytes, 32 lanes), 6 for the row's tree, 5 for the top over 32 rows and 3 for seed_A and
  the line key. One thread takes 1,421 cycles (0.68 µs) per BLAKE3 compression, because integer ops issue at half a warp per
  clock on this card (Measured, 06:15Z prices). So the chain is about 22 µs plus the fence and L2 reads. The tile hashing has
  the same shape: 4 + 16 + 2 + 2 + 7.
- **Per step** (run.py's eager call at m = 64, same tree, `r20260930-122014-33bb`, Measured; each step carries about 10 µs of
  launch and event, as `node_keys` at 0.0100 ms shows): `h1_commit` 0.0454 ms against 0.0623 for its three launches (rows
  0.0336, tree 0.0162, seed 0.0125); `h1_tiles` 0.0364 against 0.0593. Net of the launch, A's commitment is about 35 µs, as
  bc-b139c29c's stand-in measured it (34.7–36.4 µs, `a-commit-latency.md` §2).
- **Next levers at decode, Estimated, same bytes:**
  - `stats_a`, which reads A but not E_A, on a side stream beside `h1_commit` (GPU 1's arm; 0.0158 ms eager, about 5 µs net): −5 µs.
  - Level keys once per epoch, since they depend only on the domain id: −1.7 µs (bc-b139c29c measured this on their stand-in).
    **Done in `05518d7f`, not yet timed:** `h1_tree` (p9), `h1_commit` (p7) and `h1_tiles` (p9) load the keys from a table
    instead of hashing them; under `one`/`fold` run.py passes `keys_<tag>`, which the unit's `node_keys_<tag>` (B's: the
    epoch's) writes outside the call, as the default forms' `hash_nodes` already read them. `h1_level_keys` builds the table
    for n domains in one launch (hash_node_keys' bytes), for an epoch driver whose units' domains are known up front. A
    domain id covers the row count, so the table serves only the calls whose m it was built for.
  - The 33rd chunk (the row's last 64 bytes) on a lane of another warp: −0.7 µs.
  - Stream priorities for the deferred tile hashing (`USE_NODE_PRIORITY`): −0.9 µs on the side-stream figure (bc-b139c29c's).
  - Together about 3.80× → 3.65× serial and 3.32× → 3.16× with the side stream.
  - **Dropped:** splitting a compression over 4 lanes. bc-b139c29c measured it at 2,631 cycles against 1,431 on one thread,
    because one thread already overlaps a round's four G functions.
- **What's left at decode is mostly outside the hashing.** Hash-free is 2.41×: GPU 1's GEMM phase alone is 0.0737 ms against
  cuBLASLt's 0.0523. Below about 35 µs, A's commitment needs a format with fewer serial compressions (bc-b139c29c's `-h2` and
  `-h3`, `a-commit-latency.md` §§7–11), which is a statement change and goes through the coordinator.
- **Prefill lever:** A's rows, 0.26 ms, against about 0.14 ms for either the DRAM or the integer floor.

## Checkpoints

- 05:04Z: module API published (below). 05:40Z: `check.py` holds the host build's rows to their references. 06:02Z: the FP8 fusion into GPU 1's kernel written and gated off the card.
- 06:10Z, 06:20Z: first node-2 runs (`r20260930-060930-5d4e`, `r20260930-061717-3e84`); the 06:15Z W1 prices posted (Results).
- 06:40Z: **tickets reverted** (`0b8c6cc6`), per the 06:35Z decision: `pearlc::warp_tickets`, its vectors and checks are gone from the module, and the fusion patch computes no tickets. **The clock label is fixed** (`6f99efa8`): `run.sh` labels rows locked-2100 under `POUW_EXPECT_UUID=lease`, unlabelled elsewhere, never "unlocked", and the summary prints `CLOCK MISMATCH` for any row more than 2% off a locked-N label.
- 06:45Z: **the `KeyError: 'warps_per_sm'`** came from an older tree's summary (a skipped sweep row has no `warps_per_sm`). The current tree's summary prints skipped rows as JSON and reached every row in `r20260930-061717-3e84` and in today's run; nothing was left to re-run.
- 07:13Z: **the fused kernel measured on the card, and the §6 fill jobs done in one lease**, `r20260930-070930-4367` (GPU-fb680060-f371-db1a-73ba-8f2eef43674c, `CUDA_VISIBLE_DEVICES=1`, locked-2100, 07:11–07:13Z): every gate passed first, then the Pearl-C phases, then `rates`, `epi` and `acommit` (Results). It replaced `r20260930-064740-4e32`, which I cancelled with a recorded marker (`CANCELLED_MANUAL`) after 20 minutes queued behind a whole-node window, so that I never held two GPUs.
- 07:20Z: **five panel rows appended** (attempts 7–11, below); the store's patch and bundle replaced (Run lines).
- 07:30Z: **K3 (ping-pong overlap) measured in the stand-in**, `r20260930-072610-cec1` (`cbe4a3a8`, GPU-fb680060, locked-2100, gates first). The last §6 fill job of mine; the dependent-chain decode is GPU 1's. Two more rows appended (attempts 13, 14).
- 08:00–08:50Z: **`-h1` fused into GPU 1's kernel** on `cursor/pearl-c-sm120-h1-9569`: #449 `6a1a051f` merged into GPU 1's `3c9e519c` (`fdb053f0`), `gemm_pearlc_b` (`08130515`), the `-h1` variants in `run.py`/`build.sh` (`341b5fb5`), the arm under #449's twin (`c386c24a`). Harness run `r20260930-085305-0a83` (GPU 6 GPU-2b59d5fe, every gate passed); attempts 29 and 30 appended at 09:04Z.
- 09:30Z: `f2e5a32e`: bc-b139c29c's tuned entry points merged and wired in (08:05Z item), `seed_a`, A's commitment moved before forming. 09:32Z: revisions on attempts 7, 8 and 13 (08:25Z item: they timed the segment model, not v1's SHA-256 rows).
- 09:41Z: `r20260930-093140-286c` timed (above); attempts 36 and 37 appended, with revisions on attempts 29 and 30's decode (the side-stream lo hid A's commitment).
- 10:25Z: **each tree in one launch** (`h1_tree`: a whole frame-b3 tree, the levels above in its last CTA, seed_A at A's root;
  `h1_rows`: a warp a row), `r20260930-102512-a811`: attempts 47 and 48, flat against 36 and 37. The graph had already hidden
  the node launches' gaps, and `h1_rows` (0.536 ms) was slower than #449's `hash_rows` (0.459).
- 10:54Z: **`h1_rows_p`** (the same loads as `ld.global.nc.L2::256B`, since the rows are bound by DRAM scatter) at 0.2496 ms
  against #449's 0.4586, `r20260930-105428-5081`: attempts 49 and 50 at 11:11Z, prefill 2.128× and 2.053×. This is item 1 of the
  09:55Z message. Item 3, the pinned key in `pouw_hash.cuh`, is `ceac4f13` on #506.
- 12:20Z: **`h1_commit` and `h1_tiles`** (item 2) on GPU 1's head `7c3875b8` (`df63c53f`). `r20260930-122014-33bb` exited 7 at
  the harness's SASS gate (the `/dev/zero (deleted)` mapping, Needs 2); `r20260930-122529-fb8b` passed with a run-tree patch for
  it, and the reference verifier ACCEPTs all 4 transcripts. Attempts 67 and 68 appended at 12:40Z.
- 17:58Z: **GitHub token broker installed** in `/workspace` (script sha256 checked first). `git ls-remote origin HEAD` and
  `gh repo view` both succeed, and the cache's `source` is `broker`.
- 18:12Z: **the pilot is done** (top section). Attempts 67 and 68 were re-measured under the harness's poisoned dump and
  no-write control, published from the store, labelled `kept`, and rendered with no hand append.
- 3:36 PM PDT: **the `-h2` hash bench queued on all 8 dies** (top section), after passing its gates on dies 7 and 1.
  3:43 PM PDT: the chunks halved to 2.5 min after a whole-node preemption.

## Results (node 2)

### The fused epilogue in GPU 1's kernel (Measured, one-GPU diagnostic)

`r20260930-070930-4367`, GPU 1's runner (`run.py`) on the patched ship (`1633f476`, below), 5 reps, locked-2100, 2,092 MHz under load:
- **Gates:** 63 buffers bit for bit on each device record at 256 × 384 × 1,024. This includes `digests` from `gemm_pearlc_h` and the leaves hashed from them, against the fixture's; the 8,192³ reruns differ in 0 words.
- The fused call digests C̃ and U in the epilogue from registers and stores only y. It computes no tickets.

| 8,192³ | Unfused call (GPU 1's, tickets included) | **Fused call** | Digests inside the kernel (`_h` − `_s`) | C̃/U stores saved (`gemm_pearlc` − `_s`) | Own GEMM (`_s`) | **Over GPU 6's cuBLASLt baseline 1.4457 ms** (Derived) |
|---|---|---|---|---|---|---|
| v1 (G = 4) | 4.390 ms | **4.029 ms** | 0.409 ms | 0.150 ms | 2.190 ms | **2.79×** (hash-free 2.20×) |
| v2's kernel (G = none) | 4.282 ms | **3.914 ms** | 0.389 ms | 0.156 ms | 2.091 ms | **2.71×** (hash-free 2.13×) |

- Reps agree within 0.5%.
- **The fused digest runs at the rate the stand-in predicted:** 2.1 M digests of 256 B at 291 W1/B would take 0.36 ms; it takes 0.41. It is serial after the tile's mainloop, so only overlap (K3), a cheaper hash (below) or a second resident block reduces it.
- **What's left in the fused call:** GPU 1's GEMM (1.51× the baseline), forming 0.825 ms, A's rows 0.515 ms (#449's TurboSHAKE128 segments, which my `acommit seg` row reproduces at 0.494 ms), leaves 0.089 ms.

### Fill jobs (`hashing-sm120-options.md` §6; Measured, same run and GPU)

**A's commitment at k = 8,192.** The median of 21 launches, CUDA events. "Warm" leaves A in L2 from the previous launch. "Flushed" writes a 256 MB buffer first; that write leaves dirty lines behind, whose write-back the timed kernel pays, so flushed is an upper bound. Every figure includes 7.3 µs of launch (an empty kernel's median).

| Form | FP32 m = 32 | BF16 m = 32 | FP32 m = 8,192 | BF16 m = 8,192 |
|---|---|---|---|---|
| SHA-256 of the row, a thread per row (`audit.commit_rows`' leaf, the protocol as written) | **1,014 µs** (1,279) | 512 (649) | **1,268 µs** (1,318) | 642 (685) |
| TurboSHAKE128 per 1 KB segment, a thread per segment (#449's model) | 28.5 (31.7) | 29.7 (30.7) | 494 (553) | 111 (303) |
| BLAKE3 of the row, a lane per 1 KB chunk (P4) | 30.8 (36.9) | 31.5 (34.9) | 556 (643) | **122** (305) |
| BLAKE3 over 64-byte leaves, a block per row (P4′) | 28.2 (27.7) | **20.0** (18.4) | 731 (731) | 376 (379) |

Warm, with flushed in parentheses; all in µs.
- **Decode, the protocol as written:** SHA-256 over a 32 KB row is one chain of 512 compressions. At m = 32 that is 1.007 ms net of the launch, **19.4× the whole decode GEMM** (0.0519 ms, GPU 6), and it sits before forming, on the critical path. h1's P4 brings it to 24 µs (+0.47×), P4′ to 12.7 µs (+0.24×).
- **Prefill:** SHA-256 rows cost 1.27 ms, 0.88× of the baseline by itself. GPU 1's call instead times #449's segment model (0.515 ms): see Needs 3. h1's BF16 BLAKE3 tree takes 0.122 ms from L2.
- **Where the time goes:** the FP32 rows at m = 8,192 (256 MB, larger than L2) run at about 500 GB/s. That is the access pattern: each thread reads its own 1 KB, uncoalesced. Compute alone would give 0.16 ms for the segments and 0.11 ms for the chunk tree (the W1 prices, Derived). GPU 1's planned single fused pass over A, with rows in shared memory, is where these forms reach compute speed.
- **P4′ is slower than P4 at prefill** (it has twice the compressions) and faster at decode (depth 10 against 20).

**The m = 32 tile leaf** (64 digests, 2,048 B, from L2). Latency is one warp, cycles converted at 2.10 GHz; rate is every warp busy, W1 per byte:

| Form | Depth | Latency | Share of the decode GEMM | Rate (W1/B) |
|---|---|---|---|---|
| TurboSHAKE128 flat (D = 0x22, one lane) | 13 permutations | 30.6 µs | 0.59× | 7,323 |
| Two-level (P6: 4 sub-leaves of 512 B, then their top; stand-in domains 0x24 and 0x25) | 4 + 1 permutations | 22.7 µs | 0.44× | 2,902 |
| BLAKE3 of 2 chunks and their parent | 17 compressions | 14.4 µs | 0.28× | 2,970 |
| BLAKE3 over 32 64-byte leaves (5 levels) | 6 compressions | **4.6 µs** | 0.09× | 1,037 |

- The 128 leaves of a decode call run in parallel (one warp each over 188 SMs), so a pass costs about one leaf's latency plus its launch.
- The two-level form's gain is smaller than its depth suggests: at about 4.5 µs per level, it waits on its L2 loads.

**A keyed BLAKE3 message digest in the epilogue (h1's P5 candidate).** The same 256 B message (C̃ chunk ‖ U chunk) is hashed as one chunk: 4 compressions, KEYED_HASH, CHUNK_START on the first, CHUNK_END | ROOT on the last. It is gated on the card against `blake3_chunk` on the host (0 bad words, at 4 and 8 warps). MACs per SM per clock of the FP8 tile-loop stand-in:

| k | w8 nohash | w8 TurboSHAKE128 | **w8 BLAKE3** | w4 1 block/SM: nohash / TS128 / BLAKE3 | w4 3 blocks/SM: nohash / TS128 / BLAKE3 |
|---|---|---|---|---|---|
| 1,024 | 901 | 299 | 464 | 708 / 174 / 354 | 869 / 334 / 460 |
| 2,048 | 956 | 463 | 645 | 746 / 286 / 489 | 922 / 560 / 622 |
| 4,096 | 987 | 637 | 782 | 766 / 420 / 604 | 950 / 724 / 746 |
| 8,192 | 1,003 | 784 | **877** | 777 / 548 / 682 | 965 / 804 / 828 |

- **At GPU 1's shape (8 warps, one block per SM), BLAKE3 costs 150 W1/B against TurboSHAKE128's 291 (Derived from Measured), 0.514 of it.** In GPU 1's kernel that is about 0.21 ms instead of 0.41 (Estimated).
- Registers 166–180 against 168–176; SASS 6,208 instructions against 9,208.
- With three resident blocks the difference shrinks to 179 against 217 W1/B: the other blocks' MMAs hide most of either.

**K3, the epilogue's hashing overlapped with the mainloop** (Measured, `r20260930-072610-cec1`). GPU 1's shape: 8 warps, one block per SM, split into two groups of 4. MACs per SM per clock; the unhashed 8-warp control is 900 / 956 / 987 / 1,003 at k = 1,024 / 2,048 / 4,096 / 8,192.

| k | Lockstep (the plain rows): TS128 / BLAKE3 | **Strict ping-pong**: nohash / TS128 / BLAKE3 | **Staggered**: nohash / TS128 / BLAKE3 |
|---|---|---|---|
| 1,024 | 299 / 464 | 727 / 351 / 567 | 892 / 298 / 459 |
| 2,048 | 463 / 644 | 757 / 553 / 691 | 949 / 460 / 638 |
| 4,096 | 637 / 782 | 774 / 710 / 739 | 981 / 635 / 853 |
| 8,192 | 784 / 878 | 782 / 750 / 765 | 998 / **819** / **928** |

- **Strict ping-pong:** named barriers give one group the tensor cores for its mainloop while the other runs its epilogue.
  - It hides nearly all the hashing: at k = 8,192, 750 and 765 against 782 unhashed.
  - But a 4-warp mainloop turn runs the tensor cores at 78% of 8 warps (782 against 1,003). This is the risk §3 named.
  - Net: a gain at k ≤ 2,048, a loss at 8,192 (352 W1/B for TurboSHAKE128 against 291 in lockstep).
- **Staggered:** group 1's first tile is half as long, then there are no barriers, so each group hashes while the other runs MMAs.
  - It costs the mainloop nothing (998).
  - At k = 8,192: **TurboSHAKE128 234 W1/B and BLAKE3 84 W1/B**, against 291 and 148 in lockstep (Derived from Measured).
  - In GPU 1's kernel that would be about 0.33 ms and 0.12 ms instead of 0.41 (Estimated). Its 8 warps share one cp.async pipeline and its `__syncthreads`, so it needs two pipelines, or two 4-warp CTAs per SM (236 registers × 256 threads fits; shared memory would have to drop to ≤ 50 KB per CTA).

**Die-to-die:** the W1 unit is 1,020.66 MACs per SM per clock on GPU-fb680060 as on GPU-5f1149a4. All 47 rate, latency, op, mma and sweep rows the two runs share agree within 0.015%.

### The sm_120 W1 prices for hashing (Measured, `r20260930-061717-3e84` and `r20260930-070930-4367`, locked-2100)

The unit is one dense FP8 E4M3 `mma.sync` MAC (m16n8k32 from registers, 8 chains per warp, 40 warps per SM): **1,020.7 MACs per SM per clock**. Price per byte = 1,020.7 / (bytes per SM per clock with every lane busy):

| Hash (unit of work) | W1 MACs per byte | B/SM/clk | GB/s (188 SMs) | One thread: cycles per unit (µs) | Registers |
|---|---|---|---|---|---|
| **TurboSHAKE128** (Keccak-p[1600,12], full 168-B rate) | **206.6** | 4.940 | 1,948 | 4,372 per permutation (2.08) | 80 |
| **SHA-256** (compression, 64 B) | **365.0** | 2.796 | 1,102 | 3,407 per compression (1.62) | 40 |
| **BLAKE3** (compression, 64 B) | **173.6** | 5.878 | 2,318 | 1,421 (0.68) | 40 |
| SHAKE128 (Keccak-f[1600]) | 413.0 | 2.471 | 973 | 8,993 (4.28) | 80 |
| Pearl-C message digest (256 B, 2 permutations), from registers | 267.8 | 3.811 | 1,501 | 8,963 (4.27) | 72 |
| the same from mma.sync fragments (quad transpose) | 268.7 | 3.799 | 1,493 | | 128 |
| Pearl-C tile leaf (4,096 B from L2, 25 permutations) | 226.5 | 4.507 | 1,771 | 123,858 per leaf (58.98) | 92 |
| Message digests fused in the FP8 epilogue, 8 warps, 1 block/SM: TurboSHAKE128 / **BLAKE3** | 291 / **150** | | | | 176 / 180 |

Per-instruction throughput (thread-ops per SM per clock): every integer op 63.8 (IADD3 with or without RZ, LOP3, SHF, PRMT, IMAD, IDP4A), FFMA 121.3, LOP3+IMAD mixed 85.8, LOP3+SHF 63.8. So the "Blackwell 2× integer" doesn't apply to hashing on this card; static SASS counts at 64 per clock predict every hash's rate within 10%.

## Panel rows (`panel.py append`, by bc-7442ca43)

All are `estimated`: Measured components, or harness timings without a verifier transcript or (67 and 68) without the poisoned
dump and negative-control arm the 11:50Z rule asks for. From 67 on, γ is the arm's cap at GPU 1's `7c3875b8`: TT_OUT
γ₀ = ρ = 1/400 at the device record's `SM120_PRICES` (FADD 8, BF16 MAC 2, forming credited 40, ρ's forming A-only 1; from
`r20260930-063213-c94a` and `-061717-3e84`), G None for v2.
- **Correction (13:25Z): v2's 0.5112% against 0.3622% comes from ρ, not from the prices.** The 0.3622% is attempt 2's
  (bc-3006c44a), at ρ = 1/1,000. At ρ = 1/1,000 the current record gives 0.3616% (Derived). My v2 rows 8, 30, 37, 48 and 50
  carry that ρ = 1/1,000 figure, while my v1 rows use 1/400. So the γ column is inconsistent between v1 and v2 until ρ is
  settled, which is a statement parameter and the coordinator's call.
- **Withdrawn (compute-accounting 3:25 PM PDT): every v2 γ in this table (0.5112%, 0.3622%, 0.362%) and the 0.3616% above.**
  v2 is D, at least 0.946% packed (`internal/pouw/red-team/ratings.md`). v1's figures stand.

| Attempt | Line, version, phase | Slowdown (range) | γ | What |
|---|---|---|---|---|
| **67** | pearl-c-sm120 v1-h1 prefill / decode | **1.790** (hi 1.806) / **3.796** (lo 3.321, side stream) | 0.5105% | `h1_commit` and `h1_tiles` on GPU 1's `7c3875b8`; verifier ACCEPT (`r20260930-122529-fb8b`) |
| **68** | pearl-c-sm120 v2-h1 prefill / decode | **1.755** (hi 1.770) / **3.741** (lo 3.266) | 0.5112% | the same on v2's kernel |
| 49 | pearl-c-sm120 v1-h1 prefill / decode | 2.128 (hi 2.143) / 3.823 (lo 3.30) | 0.5111% | `h1_rows_p`, 0.2496 ms (`r20260930-105428-5081`) |
| 50 | pearl-c-sm120 v2-h1 prefill / decode | 2.053 (hi 2.072) / 3.806 (lo 3.28) | 0.3622% | the same on v2 |
| 47 | pearl-c-sm120 v1-h1 prefill / decode | 2.337 (hi 2.359) / 3.853 (lo 3.33) | 0.5111% | `h1_rows` and `h1_tree`, a launch a tree (`r20260930-102512-a811`) |
| 48 | pearl-c-sm120 v2-h1 prefill / decode | 2.262 (hi 2.283) / 3.814 (lo 3.29) | 0.3622% | the same on v2 |
| **36** | pearl-c-sm120 v1-h1 prefill / decode | **2.339** (hi 2.421) / **3.97** (lo 3.35, side stream) | 0.5111% | `-h1` fused, tuned kernels, A before forming, `seed_a` (`r20260930-093140-286c`) |
| **37** | pearl-c-sm120 v2-h1 prefill / decode | **2.264** (hi 2.344) / **3.93** (lo 3.32) | 0.3622% | the same on v2's kernel |
| 29 | pearl-c-sm120 v1-h1 prefill / decode | 2.346 / 4.48 | 0.511% | `-h1` fused, #449's kernels (`r20260930-085305-0a83`); **revised 09:45Z:** decode lo = serial, the 2.55 hid A |
| 30 | pearl-c-sm120 v2-h1 prefill / decode | 2.269 / 4.44 | 0.362% | the same on v2; revised likewise |
| 7, 8, 13 | v1 / v2 / v1 prefill | **revised 09:32Z:** 3.31 / 3.23 / 3.25 | | with v1's SHA-256 rows (1.268 ms) in place of the segment model |
| 7 | pearl-c-sm120 v1 prefill | 2.79 (2.77–2.81), hash-free 2.20 | 0.511% | the fused epilogue, measured (above) |
| 8 | pearl-c-sm120 v2 prefill | 2.71 (2.69–2.73), hash-free 2.13 | 0.362% | the same on v2's kernel |
| 9 | pearl-c-sm120 v1-h1 prefill | 2.38 (2.36–2.52) | 0.511% | h1's measured components on GPU 1's current kernel: BLAKE3 digests 0.210 ms, A's BF16 BLAKE3 tree 0.122 ms (0.305 flushed) |
| 10 | pearl-c-sm120 v1 decode | 26 (23–29.6) | 0.511% | the protocol as written, with A's SHA-256 row leaf measured (+19.4× to +24.5×) |
| 11 | pearl-c-sm120 v1-h1 decode | 4.0 (3.2–4.5) | 0.511% | h1 with A's P4 tree measured (+0.47×; P4′ +0.24×) |
| 13 | pearl-c-sm120 v1 prefill | 2.73 (2.71–2.79) | 0.511% | attempt 7 plus K3 as staggered warp groups (stand-in measured; strict ping-pong loses at k = 8,192) |
| 14 | pearl-c-sm120 v1-h1 prefill | 2.31 (2.30–2.44) | 0.511% | attempt 9 plus the same K3: BLAKE3 digests 84 W1/B |

## Run lines (GPU-ready)

**`-h1` with `h1_commit` and `h1_tiles` on GPU 1's head** (what `r20260930-122529-fb8b` ran).
- **Next rerun (attempts 67 and 68 as measured rows):** the same line on `b0820016` or later, with
  `export PEARLC_A_FORMS=p,fold` at the top of `h1c-run.sh`, so run.py and the arm time the one-launch kernels, which are no
  longer the default. It waits on #491's `discover()` fix: `e91184bf` (SASS gate v3) still refuses a deleted mapping, and its
  `.FTZ` pins are null until the numeric job runs.
- **Ship:** `CUDA=<a CUDA 13 root> bash benchmarks/pouw/pearl_c_sm120/build.sh <dir>/ship` on
  `cursor/pearl-c-sm120-h1-commit-9569` (`df63c53f` for the 12:25Z run), then `tar -C <dir> -cf pearl-c-sm120-h1c-ship.tar ship`. nvcc 12.9 refuses
  `gemm_plain`; I built with the nvcc 13.0.88 pip wheels (Lessons).
- **Run tree:** a local commit merging the branch into harness `8d04bfe5` (#491), plus, until #491 fixes it, the one-line SASS gate
  patch in Needs 2 (mine: `d8c46363` on `cc34b5d4`, not pushed). Harness build `art:14fff942…` (`libpouw_harness.so`,
  `libpouw_lt2.so`, `build.json`).
- **Scripts:** `h1c-run.sh` checks the ship's manifest, runs run.py's check and diagnostic timing (exit 6 on a failed gate), then the
  harness with `PearlCSm120` and `PearlCSm120Unpromoted` (at `7c3875b8` these are the `-h1` arms). `h1c-job.sh` takes the lease
  around it and runs `verify.py` after it, outside the lease.

~~~text
research run --on vy-nebius-2 --project verity --campaign pouw --source <run tree> --cwd source --timeout 3600 \
  --env GPU_LEASE_WHO=<your bc-id> --send libpouw_harness.so --send libpouw_lt2.so --send build.json --send server.md \
  --send pearl-c-sm120-h1c-ship.tar --send h1c-run.sh --send h1c-job.sh \
  -- bash -c 'bash $RESEARCH_RUN_DIR/inputs/h1c-job.sh'
# h1c-job.sh:
#   I=$RESEARCH_RUN_DIR/inputs; export PEARLC_ROWS=/tmp/pearlc-rows-$RESEARCH_RUN_ID
#   gpu-lease 1 --wait --max-min 25 -- timeout 1440 bash $I/h1c-run.sh; b=$?; v=0
#   if [ -f $RESEARCH_RUN_DIR/bench.json ]; then . benchmarks/pouw/harness/jobs/env.sh $I
#     timeout 1200 "$PY" benchmarks/pouw/harness/verify.py $RESEARCH_RUN_DIR/bench.json; v=$?; fi
#   rm -rf "$PEARLC_ROWS"; exit $(( b ? b : v ))
# h1c-run.sh:
#   I=$RESEARCH_RUN_DIR/inputs; tar -C $I -xf $I/pearl-c-sm120-h1c-ship.tar; (cd $I/ship && sha256sum -c --quiet MANIFEST.sha256) || exit 5
#   export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES%%,*}
#   (cd $I/ship && PEARLC_EXPECT_UUID=$GPU_LEASE_UUID SHAPES='8192 32x8192x8192' REPS=5 python3 run.py check/check.json > $RESEARCH_RUN_DIR/run_py.jsonl) || exit 6
#   . benchmarks/pouw/harness/jobs/env.sh $I
#   PEARLC_SHIP=$I/ship "$PY" benchmarks/pouw/harness/bench.py --gpu lease --server-md $I/server.md --clock-label locked-2100 \
#     --shapes headline --families fp8-e4m3 --arm-path benchmarks/pouw/pearl_c_sm120 --arm pearlc_arm:PearlCSm120 \
#     --arm pearlc_arm:PearlCSm120Unpromoted --out $RESEARCH_RUN_DIR/bench.json
# timed: the same harness line in gpu-lease 8 --wait (<= 20 min), gates in the same window
~~~

**Hash bench** (the fill jobs and the K3 rows included). The bundle is **`internal/pouw/rtx-pro/2-hashing/pouw-hash-ship-cbe4a3a8.bundle`** (sha256 `92e09ad4aca80ed68c43a0254c0eb540cac3b1283fbbfddde48018b283f755ae`), ship commit `80a4c8ff676b797253b117e23bbca59bfc5c9327`, built from `cbe4a3a8`. It holds the sm_120a binary (CUDA 12.9.1; needs only the driver), `host_check.jsonl` (161 rows, already held to the references), `check.py`, `sass.json` and `run.sh`. `run.sh` takes `GPU_LEASE_UUID` for the identity gate and runs the gates first; about 3 minutes of wall.

~~~text
git clone -q /cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/internal/pouw/rtx-pro/2-hashing/pouw-hash-ship-cbe4a3a8.bundle /tmp/pouw-hash-ship-repo
research run --on vy-nebius-2 --project verity --campaign pouw --source /tmp/pouw-hash-ship-repo --timeout 7200 \
  --env GPU_LEASE_WHO=<your bc-id> --env POUW_EXPECT_UUID=lease --env CLOCK_LABEL=locked-2100 \
  -- gpu-lease 1 --wait -- timeout 1780 bash /workspace/research/src/80a4c8ff676b797253b117e23bbca59bfc5c9327/run.sh
~~~

`PARTS="acommit"` (or any of `rates epi acommit`) runs only those modes after the gates; `run.sh check` runs the gates only.

**GPU 1's runner on the fused patch** (what `r20260930-070930-4367` ran first): build `1633f476` with GPU 1's `benchmarks/pouw/pearl_c_sm120/build.sh` and tar the ship. Then:

~~~text
research run ... --send pearl-c-sm120-fused-ship.tar --env SHAPES=8192 --env REPS=5 -- gpu-lease 1 --wait -- timeout 1780 bash -c \
  'cd $RESEARCH_RUN_DIR/inputs && tar xf pearl-c-sm120-fused-ship.tar && cd ship && sha256sum -c --quiet MANIFEST.sha256 || exit 5;
   PEARLC_EXPECT_UUID=$GPU_LEASE_UUID python3 run.py check/check.json'
~~~

## The TurboSHAKE128 fusion into GPU 1's `gemm_pearlc` (v2 patch, applied by GPU 1 as `6d9ac0e8`; `-h1` is above)

**Patch:** `internal/pouw/rtx-pro/2-hashing/pearl-c-sm120-fused-v2-1633f476.patch` (sha256 `8868f880af0a21d76b3bb51786e9f52e257f66ca969feed22c27051565a7ba98`). It is `git diff 14946c30 1633f476`, where `14946c30` is GPU 1's `a7a440a8` with `cursor/pouw-hash-sm120-9569` merged in (the kernel includes `../pouw_hash/pouw_hash.cuh`). It touches only GPU 1's files and replaces the earlier patches (both deleted).
- **Kernel.** Two new modes:
  - `M_PEARLC_S` (`gemm_pearlc_s`, `_s_u`): no C̃/U stores, the control.
  - `M_PEARLC_H` (`gemm_pearlc_h`, `_h_u`): after the peel, `quad_msg_digest<2>` per region over C̃ (copied into the dead promotion accumulators before the peel) and U. The digests go to `p9` in `hash_msg`'s layout, and only y is stored.

  The quad's scratch is the warp's share of the stages, free after the mainloop's last `__syncthreads`, so shared memory stays 98,304 B. Registers: `_h` / `_h_u` 236, `_s` 215, no spill.
- **run.py.** A `fused` phase (`gemm_pearlc_s`, `gemm_pearlc_h`, `hash_leaf_h`). Its gate covers `digests` and `leaves` from `gemm_pearlc_h`, and the 1- and 3-CTA reruns. Timing adds `call_e2e_fused_ms`, `fused_hash_ms` (`_h` − `_s`), `cu_stores_ms` (`gemm_pearlc` − `_s`) and `ratio_vs_own_plain_gemm.call_e2e_fused`.
- **Also changed:** `sass_gate.py` holds all six pearlc kernels to (32, 64); `build.sh` ships `benchmarks/pouw/pouw_hash`. GPU 1's test file passes 15/15 on the patched tree with the real sm_120a build.

## The module (GPUs 1 and 5 code against this)

**Location:** `benchmarks/pouw/pouw_hash/pouw_hash.cuh` (header-only, namespace `ph`) on `cursor/pouw-hash-sm120-9569`, with `vectors.cuh`, `pouw_hash_check.cu`, `pouw_hash_bench.cu`, `check.py`, `sass.py`, `build.sh` and `run.sh`. Every function is `__host__ __device__`, so a CPU build prints the same vectors as the device. There are 161 check rows, against hashlib, the `blake3` package, `verity.commitments.turboshake` and Pearl-C's `leaf`.

| Call | What |
|---|---|
| `ph::keccak_p<ROUNDS>`, `ph::ts128<NL>(D, lane, out[4])`, `ph::Ts128Stream` | Keccak-p[1600], TurboSHAKE128 (compile-time and streaming) |
| `ph::sha256<NW>`, `ph::sha256_compress`, `ph::sha256_bytes` | SHA-256 (big-endian words) |
| `ph::blake3_compress`, `ph::blake3_chunk(key or nullptr, m, len ≤ 1024, out)` | BLAKE3, one chunk, plain or keyed |
| **new:** `ph::blake3_tree<MAXN>(key, mode, blocks, n, word, out)` | BLAKE3's tree over n = 2^j chunks of `blocks` 64-byte blocks, on one thread: blocks = 16 is BLAKE3 itself (P4); blocks = 1 is the 64-byte-leaf tree (P4′) |
| **new:** `ph::warp_blake3_tree<N>(key, mode, blocks, word(c, i), out)` | the same on a warp: a lane per chunk, 32 / N trees, shuffles; lane l % N == 0 gets its tree's root |
| **new:** `ph::block_blake3_fine<N>(key, mode, word(t, i), sh, out)` | P4′ on a block of N threads, one 64-byte leaf each; thread 0 gets the root |
| `ph::quad_msg_digest<A>(frag, D, scratch, out[4])` | TurboSHAKE128 digests of an m16 × n64 region of mma.sync FP32 accumulators from registers (1 KB of shared memory per warp) |
| **new:** `ph::quad_msg_digest_b3<A>(frag, key, scratch, out[8])` | the same messages as keyed BLAKE3 (one chunk of 4 blocks at A = 2), same lane-to-message map |
| `ph::pearlc::msg_digest`, `tile_leaf`, `row_segment<NL>`, `digest_index`, `narrow_row` | Pearl-C's words (D = 0x21, 0x22, 0x23) |

Lane map (both digests): lane 4g + t gets row `quad_row(lane) = g + 8(t&1)`, chunk `quad_chunk(lane) = t>>1`. Call once per region with the region index a compile-time constant: a rolled loop spills the accumulators to local memory. The layout holds for every m16n8kK with FP32 accumulation (FP8 k32, FP4 k64, BF16 k16).

## Lessons

- **`panel.py append` can clobber a concurrent append on the store.** Its `open("a")` isn't atomic on this filesystem. At 07:17Z GPU 5's row overwrote most of mine, leaving a fragment line that broke every later `panel.py` run (a JSON decode error). I removed my fragment and re-appended the row as attempt 10; every other row is intact. Check after appending that the file still parses.
- **`gpu-lease --wait` is first come, first served, whole-node windows included.** From 06:46 to 07:09Z, one 8-GPU window waiting on one busy GPU held five 1-GPU jobs while 7 GPUs sat free. A 1-GPU job with a short `research run --timeout` can time out in that queue: set a long `--timeout` for the wait and bound the lease itself with `timeout 1780` inside it.
- **Cancelling your own queued run cleanly:**
  - `research pods ssh vy-nebius-2 -- 'PYTHONPATH=<the run's PYTHONPATH> python3 -m research tele cancel-intent --actor manual --reason ... --target-pgid <gpu-lease pid> --expect-nonempty --attempt-dir /workspace/research/runs/<id> --deliver'`.
  - The node has no `research` on PATH; the harness's `PYTHONPATH` is in `/proc/<research run pid>/environ`.
  - The run is then classified `CANCELLED_MANUAL`.
- `research run --source` refuses a dirty checkout; ship trees with every file 0644 and set the bit on the machine. The store's filesystem sometimes answers EAGAIN, `panel.py`'s lock included: retry after a few seconds and verify with `sha256sum`.
- **A side stream only hides what the protocol lets run late.** Check each hash's data dependencies before moving it to `after`: A's root feeds seed_A, which keys E_A, so A's commitment belongs before forming.
- **nvcc emits `.FTZ` FP32 ops without any FTZ flag:** `__fdiv_rn`, `__frcp_rn` and `__fsqrt_rn` use them inside their correctly rounded sequences (2, 3 and 7 ops at `-O3 -fmad=false`, sm_120a, CUDA 12.9). Count `.FTZ` in the SASS, not in the build flags.
- A stand-in stream handle segfaults #449's checks: create the stream with `cuStreamCreate`. `panel.py` descriptions must not start with `-` (argparse).
- **A CUDA graph already hides launch gaps.** Folding 13–14 node launches into one per tree saved about 4 µs a decode call in
  the graph, against about 17 µs in run.py's eager call. Price a launch fusion in the graph, not from eager per-step times.
- **`build.sh` refuses a kernel with local memory,** and `__launch_bounds__(1024)` caps registers at 64: `h1_commit` spilled
  (16 B of stack) until it went to 256 threads (80 registers, none spilled).
- **nvcc 12.9 refuses GPU 1's `gemm_plain`;** without a CUDA 13 on the VM, the pip wheels `nvidia-cuda-nvcc`, `-crt`, `-runtime`,
  `-cccl` and `nvidia-nvvm` 13.0 (`pip install --target D`) give `D/nvidia/cu13` as a root for `CUDA=`.
- **Every `extern __shared__` array of one name must have one type in a translation unit.** GPU 1's kernels use `smem` and
  `ml_smem` (`uint8_t`), and the `h1` kernels use `sh` (`uint32_t`).
- **#449's fake driver (`fake_cuda.c`) silently dropped every kernel name past 64,** so the host twin couldn't find the new
  kernels. It now holds 128 and aborts past that (`ea17cefb`).
- **At harness `8d04bfe5`, the SASS gate refuses a run once CUDA is initialized.** Its `discover()` reads the mappings after the
  arms' `build()`, when `/dev/zero (deleted)` (from CUDA or native init) and `/dev/shm/sem.* (deleted)` (from multiprocessing)
  are mapped; neither is a file (Needs 2).

## Fill candidates

| Candidate | Run line | GPU-hours | Restarts cleanly | Yields |
|---|---|---|---|---|
| **Queued 3:43 PM PDT:** the `-h2` hash bench, `gpu2-h2hash-die0.sh` … `die7.sh` | `/workspace/pouw/fill/queue/` (copies in `/workspace/pouw/gpu2-h2hash/jobs/`) | ≈ 1.08 per die, ≈ 8.7 in all (26 chunks × 2.5 min each) | yes (exit 99 per chunk, 143 on SIGTERM) | per-die `-h2` and `-h1` hashing at the 13 panel shapes, both variants, gated bit-exact |
| Superseded (not queued): the old hash-bench bundle `pouw-hash-ship-cbe4a3a8` on each die | — | ≈ 0.04 per die | yes | it predates `-h2` and the in-kernel keys; the row above covers every die |

## Needs

0. **GPU 1 (bc-18346d9c): take `cursor/pearl-c-sm120-h1-commit-9569` at `e0902b4a`** (17:55Z, above). It is your `b6a91929`
   plus one commit to `pearlc_arm.py`, `pearlc_arm_dry.py` and `test_pearl_c_sm120.py`: the v0.5 `dump`, `transcript_buffers`
   without the tree counters (your `poison()` broke the one-launch trees), `variant` and `lineage`. It fast-forwards your
   branch. Needs 2 and 3 below are done: #491 `e22a2808` has the discovery fix and #583 the poisoning.
1. (Done: in `b6a91929`.) **GPU 1 (bc-18346d9c): take `cursor/pearl-c-sm120-h1-commit-9569` at `b0820016`.** It is your `f0f9b1ab` merged with
   `h1_commit`, `h1_tiles` and the level-key table (`pouw_hash/h1_sm120.cuh`), the `p,one` and `p,fold` forms opt-in by
   `PEARLC_A_FORMS` (the default stays your `w,nodes`, with #540's step names, buffers and `levels(tag, count)`; every other
   form is rechecked and timed in `alt_ms`) and #449's fake driver fix. Since it contains `f0f9b1ab`, it fast-forwards your
   branch. It touches your `run.py` and `test_pearl_c_sm120.py`; 318 tests pass. #540 at `304436d3` passes its 44 device-path
   tests on the merge. Every gate passed on the card and the verifier ACCEPTs all 4 transcripts (`r20260930-122529-fb8b`, at
   `df63c53f`).
   - **Next at decode, in your arm (Estimated, same bytes):** `stats_a` on a side stream beside `h1_commit` (it reads A, not E_A):
     −5 µs a call. A's level keys once per epoch: −1.7 µs. Stream priorities for the deferred tile hashing: −0.9 µs on the
     side-stream figure (bc-b139c29c measured the last two). The level-key table is in (`05518d7f`); the other two are yours.
2. **Harness (bc-0de2d624): the SASS gate at `8d04bfe5` refuses every arm that initializes CUDA.** `discover()` reads the process's
   mappings after the arms' `build()`, when `/dev/zero (deleted)` (CUDA or native init) and `/dev/shm/sem.* (deleted)`
   (multiprocessing) are mapped. Neither is a file, so there is nothing to scan (`r20260930-122014-33bb`, exit 7).
   Recommendation: record both as not scanned, as my run-tree patch does
   (`ANON_SHARED = re.compile(r"/dev/zero \(deleted\)|/dev/shm/sem\.[^/]+ \(deleted\)")`, checked before the deleted-file refusal).
   Until #491 has it, every `-h1` row of mine carries that shortcut.
3. **Harness (bc-0de2d624): the negative-control run for the 11:50Z rule.** The arm has the poisoned dump and the negative
   control since GPU 1's `9f1e33b1`, which is in my stack. #491 at `e91184bf` still lacks the `discover()` fix (Needs 2), so
   attempts 67 and 68 stay estimates although the verifier accepted them. I'll rerun on the harness commit that has it (Run
   lines).
4. **#449's owner (`cursor/pearl-c-h100-9ada`), through the coordinator: `fake_cuda.c` holds 64 kernel names and drops the rest
   silently,** so a cubin with more kernels loses names on the host twin (at `5f6a31c7` still). My fix on the stack above
   (`ea17cefb`: 128 names, 8 KB of names, abort on overflow) touches only that file; take it or size the table your way.
