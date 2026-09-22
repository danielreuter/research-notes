---
id: r20-proof/gate4-h100/20260922T0954Z-handoff-handoff
campaign: r20-proof
lane: gate4-h100
kind: handoff
status: closed
repo: verity-main@f96fc53
origin: verity-main@f96fc53:backends/numerical/reports/gate4/HANDOFF.md
---

# gate4-h100 lane -- HANDOFF

Branch `lane/gate4-h100` (worktree `/Users/danielreuter/projects/verity-gate4`), pod `vy-g4` (H100 80GB, id uktx6i8dejuunk,
ssh helper `/tmp/g4.sh` on the laptop = `ssh -i ~/.runpod/ssh/runpodctl-ssh-key -p 11461 root@64.247.201.61`).
Ledger `backends/numerical/reports/ledger/gate4-h100.jsonl`, track `shared`.  Deliverable: `note:r20-proof/gate4-h100/20260922T0954Z-report-gate4-h100 / notes-asset:campaigns/r20-proof/assets/gate4-h100/reports/GATE4_H100.json`; raw results under `backends/numerical/reports/gate4/`.

## Pod state

* `/workspace/venv312` (torch 2.6 cu124, Triton 3.2); `cupy-cuda12x` + `blake3` were NOT installed on this pod (the brief said
  they were) -- installed by this lane's setup step.
* `/workspace/gate4/src` = `git archive HEAD` of this branch (tar-synced); `/workspace/gate4/setup.log` = deps + instance build.
* `/workspace/bench-instances/v1` = `verity_numerical.bench.instances build --procs 48` (persistent; every prover takes `--root`).
* BabyBear export for the a-gpu prover: `/workspace/bb/pos4096`, `/workspace/bb/neg` (built by this lane; see step 1).

## Rows: measured / next

(kept current after every row; see the table in note:r20-proof/gate4-h100/20260922T0954Z-report-gate4-h100)

| row | status | run id |
|---|---|---|
| A end-to-end (a-gpu v2e, main 38757ed) | DONE: 5.02 s median of 5 warm (1.23 ms/VU, 1.24e8), verified 4096/4096; cold run r20260922-090931-b5be (rep0 316 s compile) | r20260922-091718-45c3 |
| A end-to-end (a-gpu2 head f87b096) | FAILED at B=4096: `logup_packed._walk_fs: LogUp: fractional sum is not zero (a query is not in its table)` -- the lane's packed LogUp (tested at 64 VUs) does not prove the 4096 batch; not fixed here (measurement lane) | r20260922-091947-822f |
| A end-to-end (a-gpu2 pre-graph merge 179d509) | FAILED, same error in `logup_packed._walk` | r20260922-092252-3ebd |
| A buckets v1 / v2 (a-fusion `bench_fused` 2^26/2^28 k=3 + `logup_graph_bench` v1 v2 level/round + v2 concurrent) | DONE: v1 0.285 s = 7.07e6 (sumcheck 100.5, logUp 88.3 level); v2 0.184 s = 4.55e6 (sumcheck 36.4, logUp 10 streams 81.2); raw + reprice under `gate4/a_buckets/` | r20260922-092450-5b79 |
| B end-to-end non-ZK / HVZK (b-ligero2, 25 x 170, batch 16384, reps 3) | DONE: non-ZK 2.386 s = 0.583 ms/VU (5.92e7), union 2^-128.25; HVZK 2.911 s = 0.711 ms/VU (7.22e7), union 2^-128.05; verifier 0.82/0.88 s; envelopes under `gate4/b_e2e/` | r20260922-092841-94ac |
| B buckets v1 (commit_bench blake3 B + buckets_bench + lintest_structured M1-4 lazy) and v2 (v2_bench) | DONE: v1 111.8 ms = 2.77e6 (87% measured); v2 45.5 ms = 1.13e6 (93%); `gate4/b_buckets/b_measured_h100_gate4.json` | r20260922-093147-3d6c |
| SP1 / C cited rows in the ledger (labelled CITED) | done | -- |
| `plots/gate4_h100.png` (`plot_gate4`) + test | done | -- |
| H100 kernel column for section (b) (microbench, hash_gpu, encode.bench, fused.bench, bench_logup) | DONE: raw under `gate4/kernel_column/`; table in note:r20-proof/gate4-h100/20260922T0954Z-report-gate4-h100 (b) and `notes-asset:campaigns/r20-proof/assets/gate4-h100/reports/GATE4_H100.json[kernel_column]` | r20260922-093941-aebe |
| note:r20-proof/gate4-h100/20260922T0954Z-report-gate4-h100 / notes-asset:campaigns/r20-proof/assets/gate4-h100/reports/GATE4_H100.json | DONE (`gate4/build_gate4.py` regenerates the JSON) | -- |
| SP1, C | cited only | -- |

## Next steps

Lane complete; vy-g4 can be terminated.  Nothing is running on the pod.  If resumed: (1) a-gpu2 at B=4096 once that lane fixes the LogUp fractional-sum failure, labelled by commit; (2) B v2 end-to-end when a v2 prover exists; (3) SP1 on the H100 only if a pre-built CUDA prover image is available (do not rebuild).
