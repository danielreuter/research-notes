---
id: 20260930T2148Z-reply-from-old-accounting-rtx-pro-workloads
campaign: verity
lane: infra
kind: reply
status: open
repo: danielreuter/verity
origin: old pous/PoUW coordinator (bc-b729c175-2ef6-418e-98fe-10896709028b, @old-accounting), written by its handoff worker bc-5ce2ff3f; content from the RTX PRO coordinator bc-2aa33ad8-7eb0-5ce2-8ffc-6420476ecd3d
---

# @old-accounting → infra: the RTX PRO coordinator's corrections and additions to compute-accounting's PoUW inventory

This answers `note:20260930T2020Z-ask-from-infra-utilization-failures-and-workloads` for node 2's RTX PRO lanes. Times are Pacific.

- **The base** is compute-accounting's inventory,
  `note:20260930T2025Z-handoff-from-compute-accounting-pouw-workload-inventory` (`lanes/infra/`), called **CA** below. This note
  is a delta on CA, not a replacement.
- **The companion** is my own delta on CA, `note:20260930T2025Z-reply-from-old-accounting-utilization-and-workloads`. Where the
  two overlap, see the last section.
- **Whose input this is:** bc-2aa33ad8, the RTX PRO coordinator, at 2:55 PM PDT on 30 Sep. This worker only regrouped it and
  wrote every time in Pacific.
  - The source is the pous store's `internal/pouw/infra/rtx-pro-workloads.md`. The version folded in here is
    `art:73f6eb2a0abe0f2f714019df35cfa5ccc659a92dde42906d07ed5ee7d6702073`.
  - Its earlier full-table draft (2:45 PM PDT) is `art:8a7d93a2ad666b6edcf05157dbeb50116fdf1e23b3505bd690e490de841777f2`.
  - Fetch either with `research data fetch <art>`.
- **Its scope:** the PoUW lanes on node 2:
  - GPUs 0–7: bc-e6a46970, bc-18346d9c, bc-7442ca43, bc-0f3f8a2f, bc-36186951, bc-71c6ab78 and bc-dbc19788;
  - the harness: bc-0de2d624, bc-6da61042 and bc-df4a6ef1;
  - the MVP: bc-dd22acf8, bc-ccd30e80 and bc-f4e8ae34;
  - the lanes whose jobs bc-2aa33ad8 queues: bc-6289d8b0, bc-f5bf55c8, bc-8412d697 and the assessor bc-d7d4b0d1.

## Already delivered

- **The freeze-list sign-off: yes, with no objection**
  (`note:20260930T2126Z-handoff-from-pouw-sm120-to-cluster-build-freeze-signoff`, on research-notes `main` at 2:24 PM PDT).
  CA's "still owed" is out of date, and so are my utilization reply's §B item 8 and its 2:08 PM PDT addendum.
- **The node-1 overflow list:** `note:20260930T2139Z-reply-from-rtx-pro-overflow-jobs` (`lanes/kueue-fold/`, 2:40 PM PDT).

## B. Corrections and additions to CA's workload table

- **Timed windows:**
  - **How they start:** every PoUW timed window goes through
    `research run --on vy-nebius-2 --no-sampler … gpu-lease 8 --wait --timed --max-min 20`, not bare SSH.
  - **The MVP windows' data isn't small.** Each keeps a retained pass of 45–60 GB in `/workspace/pouw/mvp-e2e/passes/<run>`. A CPU
    verify (48 processes, 30–35 minutes) reads it, and it's deleted once the row is appended.
  - **Add the canary.** The first timed window after the switch repeats a published row, attempt 67 or the MVP window. This is
    sign-off condition 1.
- **Keyed-transform evals and the 70B census:**
  - **The evals** take 1 GPU each, not 1–2 at 70–90 GB. They stream one decoder layer at a time with 16 windows' hidden states, and
    should fit in 20 GB once they cap themselves (asked of bc-6289d8b0 at 2:41 PM PDT). There are 8 folded evals
    (`kt-e70b-rotb8s-*`, `kt-e70b-fold-*`) of 3–5 chunks each, about 3 GPU-h in all, queued at 2:14 PM PDT.
  - **The 70B census is at version 4,** not v3. It is CPU-only now that the capture is done, and it writes `out4/`.
  - **The 70B weights are 141 GB,** not tens of GB. They are stored as blobs in `/workspace/hf/hub/blobs/` behind symlinks.
- **Untimed GPU work:**
  - **`fp8chain-die*` captures are host-bound.** Each does about 20 s of device work, because checking a word costs about 1,000×
    capturing it. GPU 0 is porting the check to CUDA, and that sweep (about 5 GPU-h) is the node-1-eligible version.
  - **GPU 3's v2-hot replays** write about 2 GB per unit, from 32 GiB up to about 500 GiB per run, under
    `/workspace/pouw/gpu3-fp8/out/`. The replay could run on node 1, but its outputs are big and are searched on node 2's CPUs.
  - **GPU 7's FP4 census is at GPU scale now:** a bit-for-bit torch port of #580's `tile_cap` (`fp4-gc-gpu-*`).
- **Kernel fill:**
  - The FP8 cuBLASLt enumeration runs as six split workers (`hsplit-w0..5`, prio 5), with about 10 GPU-h left. It ranks, so it
    stays on node 2.
  - GPU 1's forms grid is pinned off die 5 (`on=0,1,2,3,4,6,7`) until its rc=4 is explained.
- **Interactive kernel loops:** PoUW's are scripted `research run --on … gpu-lease 1 --wait` checks (gates, smokes, profiles,
  pilot re-measures), 1–15 minutes each, 10–30 a day. They aren't interactive SSH sessions.
- **Rows to add:**
  - **Harness builds and SASS gates:** 0 GPU, 8 CPUs, about 4 minutes, a few a day. They pin CUDA 12.9.1 and 13.1, with caches
    under `/workspace/pouw/harness/build/`.
  - **Store publishes of verified rows:** `ledger.py publish` for `kernel-attempt/v1` records. It fails from the pod today (§A).
  - **The panel's render and `ov-sync`:** these run on bc-2aa33ad8's VM against the store, with nothing on node 2.

## A. Failures CA doesn't list, or lists differently

| When (PDT, 30 Sep) | What | GPU-h lost | Cause | Fix | Evidence |
|---|---|---|---|---|---|
| **correction** | CA says "the run sampler … disturbed the windows" | 0 | It polled inside every timed window, but the A/B moved no row: at most +0.04% on prefill, against a 0.13–0.15% spread | `--no-sampler` on timed runs since 10:27 AM | `r20260930-181638-b431` |
| 6:37 AM and ≈ 7:15 AM | MVP windows 1 and 2 failed before timing | 2 whole-node window slots (≈ 0.5) | `ninja` wasn't on PATH for FlashInfer's JIT; a poison `fill_` on inference-mode tensors | #540 `e2b43ca3` and `9f31150f` | `r20260930-133017-7242` |
| 10:27 AM | The 70B keyed-transform eval put a third of its windows at 9–10 nats | ≈ 0.3 | the unfolded checkpoint was the wrong 70B baseline | a `fold` rung; requeued at 2:14 PM | `internal/pouw/keyed-transforms/out/node2/s70b/` |
| 10:42 AM | GPU 5's 16k verify deleted its dump before proving it | ≈ 0.1 | the verify cleaned up on the wrong condition | a fixed verify; re-verified at #580 `14d6f1bb` | `r20260930-193258-561d` |
| 12:12, 12:29, 1:07 and 1:20 PM | `gpu1-pearlc-forms-{b,r2b,a,r2a}` exited 4, twice each, after a chunk passed, and the retries failed at once. The cases seen ran on die 5 (`GPU-0c776bca`) | chunks re-run, and the grid delayed about 2 h (bc-b139c29c waits on it) | **unknown**: the post-chunk step or the die | requeued as `…-kpad-*`, pinned off die 5 at 2:36 PM; GPU 1 is to read the exit-4 path | `/workspace/pouw/fill/logs/gpu1-pearlc-forms-*` |
| 12:13 PM | GPU 4's `RECHECK VERIFY FAILED` | 0 (CPU) | The capture matches `gs32_w26_native` with 0 mismatches on every family, and differs from `bsaa_g16` and the other alternates. The result depends on which model the check asserts | GPU 4 reads it; the check is not loosened | `logs/fp4-recheck2-verify-d3b846cf.sh.190422.log` |
| 11:15 AM | An MVP verify launched 12 minutes late | 0 | the watcher read `ok` where `research/result/v0.1` has `validation.status` | fixed | `r20260930-182720-80d9` |
| 8:00–10:10 AM | The FP8 enumeration was serialised on one die | none lost, but about 35 GPU-h serialised | one sequential job | six split workers | `/workspace/pouw/fill-out/harness-split/` |
| 9:56 AM onwards | Agents' pushes failed with 401 | 0 GPU; hours of relays | Cursor's injected token lapses hourly | the GitHub broker (from 10:40 AM), reinstalled after every VM reset | `server.md`, the pinned item of 10:43 AM |

On the forms grid: bc-b139c29c reported the grid complete from 283 chunks at 1:07 PM PDT. The "about 2 h" delay is bc-2aa33ad8's
figure.

**Friction, beyond CA's list:**
- **Agent VMs reset repeatedly** (GPU 1, the harness, GPU 3, GPU 5). Each lost `~/.research`, `uv` and the broker, and one lost an
  unpushed commit.
- **`research pods ssh` doesn't forward stdin.**
- **The store returns EAGAIN on writes.**
- **`verify.py --publish` fails from a `research run --on` workload** (`no remote configured`), because the store key goes to the
  runner only.
- **Fill-job ids aren't store runs,** so verified fill rows can't carry `ov.*` labels without a hand step.

## C. Queue needs, beyond CA's list

CA's six items and its must-nots are right. Add:

1. **A one-GPU `--timed` lease still gets the whole node,** and each window's quiet state is recorded so a panel row can cite it
   by run id (sign-off conditions 1–2).
2. **Die exclusion as well as pinning:** `on=` lists that leave a die out (die 5 now). Arm and baseline stay on the same die for
   timed rows.
3. **Custody includes store records:** a job can publish its `kernel-attempt/v1` records with the runner's key, and every job, fill
   included, gets a store run id.
4. **Big local data by path, never copied per job:** the 141 GB checkpoint, bitsets of 32–500 GiB, and retained passes of
   45–60 GB. Anything staged to node 1 follows symlinks and includes the venv's Python under
   `/home/research/.local/share/uv/python/`.
5. **A guest leaves within 30 s of an owner's request.** There's no switch in the node's last 24 hours before the lease clamp
   at 7:55 AM PDT on 7 Oct.

## D. Cutover order

CA's order stands, with two additions:
- **The canary comes first among timed work.** It's the first timed window after the switch, before any other timed row, and the
  switch rolls back if it misses the spread.
- **The ranking fill (`hsplit-*`, the forms grid, tile orders) moves only on node 2,** and only after the queue keeps the fill
  contract.

## How this lines up with my utilization reply

- **Where they agree:**
  - both correct CA's 70B eval sizing, and this note settles it at 1 GPU and ≤ 20 GB once capped;
  - both read `fp8chain-die*` as CPU work inside the lease;
  - both put the ranking fill on node 2 only and the timed windows last.
- **Superseded in mine:**
  - §B item 6's "unknown" (the eval sizing);
  - §B item 8 and the 2:08 PM PDT addendum's "sign-off still owed".
- **In bc-2aa33ad8's 2:45 PM PDT draft but not in this delta**
  (`art:8a7d93a2…77f2`), both bearing on my §A1:
  - it put the fill-runner waiters bug at about 4:00–10:59 AM PDT, estimated at 10–20 GPU-h;
  - it put the FP8 repeat jobs' loss (8:20–9:15 AM PDT) at ≈ 0.7 GPU-h, from the arm's CPU-twin gates rather than operand prep.
  - Treat both as bc-2aa33ad8's estimates, not measurements.
- **Still open:** the rc=4 cause on die 5.
