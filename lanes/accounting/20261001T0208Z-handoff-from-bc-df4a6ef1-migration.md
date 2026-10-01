---
id: 20261001T0208Z-handoff-from-bc-df4a6ef1-migration
campaign: pouw
lane: accounting
kind: handoff
status: open
repo: danielreuter/verity
origin: bc-df4a6ef1 (the harness-split helper under bc-2aa33ad8, node 2 vy-nebius-2); under note:20261001T0157Z-order-from-compute-accounting-all-migration-handoff
---

# Migration handoff from bc-df4a6ef1: FP8's cuBLASLt enumeration split (`hsplit`), withdrawn (7:08 PM PDT, 30 Sep)

What I did: I split the harness's sequential FP8 cuBLASLt enumeration (`harness-fp8-enum-b-af2d27e0.sh`, bc-0de2d624) across
node 2's idle dies, as workers `hsplit-w0`…`w7` with one shared ledger. The rest of it was dropped by compute-accounting's cut
(3:16 PM PDT), and I withdrew every worker at 3:35 PM PDT. Nothing of mine is kept as live work, and nothing of mine is in flight.
bc-2aa33ad8's handoff lists `hsplit` under "I'd stop" (note:20261001T0215Z-handoff-from-2aa33ad8-migration).

## 1. Branches and PRs

None. I made no commits. The PR branches listed on my run are bc-2aa33ad8's lanes', which its handoff covers.

## 2. Runs and jobs in flight

- **Nothing of mine is on node 2's fill queue or running** (checked 7:06 PM PDT). I launched no research runs.
- **All ten split jobs are in `/workspace/pouw/fill/withdrawn/`:** `hsplit-w0.sh`…`hsplit-w7.sh`, plus the two merges
  `hsplit-merge-llama3.1-70b-qkv-decode.sh` and `hsplit-merge-qwen2.5-7b-down-decode.sh`. The merges were stuck behind the
  pous CPU slots, so I ran both by hand at 3:57 PM PDT and withdrew their queued copies.
- **Output dir (node 2):** `/workspace/pouw/fill-out/harness-split/`, 1.9 GB.
  - `split.py` (sha256 `836d8169…`) is the tool (`plan`, `record`, `merge`, `table`, `queue`, `withdraw`, `status`, `compare`).
  - `state/ledger.json`: workers, claims and shapes. All 8 workers are `stopped` and 4 shapes are `dropped`.
  - `state/w<k>/<shape>/s<START>-<STOP>/`: each slice's `bench.json`, `bench.log`, `exit` and `wall_s`.
  - `state/merged/<shape>/`: `table.tsv` (the screen ranking), `table.sha256`, `names.txt`, `names.max`, `final/`, and `s*` symlinks to the slices.
  - **`state/merged/final-table.tsv`**, sha256 `7a1ff61802c3d5538a445421c032701469e9a117d4aab5327365045e5bbf7d4d`.
  - `state/verify/` holds the one-slice check, and `jobs/` the job scripts as queued.
- **Custody:** none. This is fill output, not a research run, so nothing is in the evidence store. Node 2's hourly backup of
  `/workspace/pouw/` is all that preserves it. I staged a store copy of the final table (see 3).

**What the final table holds:**
- **Finals for 17 shapes:**
  - 8,192³ and 4,096³, from the sequential job's dir `fill-out/harness/fp8-enum-485a6466/`, linked;
  - 16,384³, 32,768³, 2,048³ and m32-n8192-k8192;
  - all 8 Qwen2.5-7B and Llama-3.1-70B prefill shapes;
  - Qwen2.5-7B's qkv, o and gate_up decode.
- **Dropped, with no final:**
  - Qwen2.5-7B down decode and Llama-3.1-70B qkv decode are fully screened and merged; their `table.tsv` hashes are `58155882…` and `772b0462…`;
  - Llama-3.1-70B gate_up decode is screened 1,280 of 8,940;
  - Llama-3.1-70B down decode is not started.

## 3. Half-done state, and what was only on my VM

- **Copied, sha256-checked:** to node 2's `harness-split/dev/` and to the store's `internal/pouw-fp8/harness-split/`.
  - The copies are `split.py`, the simulator `sim.py` with its fixtures `orig_plan.py`, `seq_heredoc.py` and `seq_job.sh` (the sequential job's planner, as copied), and the scans `nvfp4_enum_scan*.py` and `hsplit_rate.py`.
  - The store copy also has `final-table.tsv` and its sha256.
  - `SHA256SUMS` lists them all.
- **Left on the VM, regenerable:** `/tmp/hsplit/simroot*`, the simulator's scratch trees.
- **This VM is bc-2aa33ad8's.** I run on it as its helper. Its `/tmp`, `~/.research/runs`, the terminals and `/tmp/a67src` are the coordinator's, and its handoff covers them.
- **Token broker:** I installed it in `/workspace` at 10:43 AM PDT, with its `export PATH=/workspace/.git/verity-auth/bin:"$PATH"` line in `~/.bashrc`. A successor installs its own.

## 4. Next step per item, and what I'd stop

- **Keep:** preserve the final table. From a host with the store remote, run `research data put --preserve` on
  `state/merged/final-table.tsv`. Add each finished shape's `table.tsv`, `names.txt` and `final/bench.json` if anyone wants the
  rankings. It is screening evidence, not a panel row: the headline FP8 divisor comes from #570's plain GEMM and the 8,192³
  enumeration.
- **Stop:** everything else in the split. That covers the 3 Llama-3.1-70B decode shapes and Qwen2.5-7B down decode's final, which is one GPU chunk of about 5 min, worth running only if someone wants that divisor.
- **NVFP4 needs no split.** Its cuBLASLt space is 3 accepted configurations per library at every panel shape, all timed, in
  `fill-out/harness/fp4-sweep-36df5171/`. Its CUTLASS tile orders are in `cutlass-sched-73339a27/` and `fp4-sched-af2d27e0/`, all 21 shapes with exit 0.

## 5. Traps

- **Every split job's header says `owner=bc-2aa33ad8`,** not me. Find them by name, `hsplit-*`.
- **Reviving the split:** there's no undrop command.
  - Under `state/.lock`, edit `ledger.json`: remove the shape from `dropped`, set the workers back from `stopped`, delete `state/w<k>/stopped`, then run `split.py queue N`.
  - `queue` skips stopped workers.
  - Any change to the sequential job's dir `fill-out/harness/fp8-enum-485a6466/` stops every worker (the guard).
- **`merge` requeues workers.** When no worker is alive, it requeues every idle worker that isn't stopped, to run finals. So a worker you un-stop comes back by itself.
- **`table` only queues itself when every shape's final ran.** With dropped shapes it never fires, so run `python3 split.py table` by hand (CPU, seconds).
- **pous CPU fill has 4 slots,** and prio-10 jobs that requeue themselves held them. A prio-0 CPU job waited over an hour.
- **`research pods ssh vy-nebius-2` stopped working here about 3:56 PM PDT:** `~/.runpod/ssh/runpodctl-ssh-key` vanished.
  `ssh -i ~/.ssh/research_key research@81.85.2.121` works.
- **`merged/<shape>/s*` are symlinks** to the worker slices. Copy with `-L` (large) or without them (just the tables).
- **Llama-3.1-70B decode screens at 16–38 indices/s per die** (Qwen2.5-7B: 36–54). The 14 GPU-h estimated for the 3 shapes measured at about 4 GPU-h.
- **The one-slice check passed (9:57 AM PDT, `state/verify/`).** Enumeration, tried list, gates and negative controls were identical to the sequential job's. The screen-time median moved 0.11% across dies at 4,096³, inside that job's own ~1% spread.
