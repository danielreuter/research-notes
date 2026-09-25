---
id: r21-live-verifier/live-verifier/20260923T0630Z-report-live-verifier
campaign: r21-live-verifier
lane: live-verifier
kind: report (working; updated at every checkpoint)
status: superseded
repo: verity-main-wt/live-verifier, branch lane/live-verifier (forked from main 6babe27)
machines: vy-live-verifier = RunPod d4maiikv32zn56 (CPU cpu3m 8 vCPU / 64 GB, 50 GB, $0.44/h, EU-RO-1, created 05:57Z; TCP 7000 -> public 213.173.105.69:30899; ssh -p 30898)
          vy-live-4090 = RunPod gh0vlgpq7st5s3 (RTX 4090 SECURE reference part, EUR-IS-2, $0.74/h, 06:25Z -> TERMINATED 08:29Z; the prover side of the tests)
decision: a live, independent verifier on a separate machine is the verification story for the interactive (8c) Table 2 cells
---

CHECKPOINT 0b40ae8a (05:54Z) [superseded] closed by coordinator 2026-09-25 05:55Z for the cloud switch-over: no sign of life >24 h; branch lane/live-verifier pushed to origin; uncommitted work (if any) saved in evidence/uncommitted-0554Z*
CHECKPOINT c595383 -- mergeable, all of it: `backends/direct/ligero/live.py` (server, prover coin source, probe, negatives,
record), `live_test.py` (5 tests; green on the CPU pod with the Rust core and with the Python core), the runner hooks
(`vu.py`, `relchain.py`, `fp4/chain.py`, `run.py --verifier`), two one-line `vu.py bench-vu` fixes (`--out`/`--dump-dir` expand
`$RESEARCH_RUN_DIR`; the result's `run_id` falls back to `$RESEARCH_RUN_ID` -- as relchain/fp4 already did; without them a bf16
result launched by `research run` needs `--run-id` and a literal path), `contract.py` additive fields + test (58 passed),
DISCREPANCIES.md D7 paragraph, `research pods create --expose-port`. `protocol.py`, `serialize.py`, Rust: untouched.
Tests: full `pytest backends/direct/ligero` **63 passed on the 4090 at c595383** (device tests included) and 59 passed + 4 skipped
on the CPU pod at 83d1de3; live_test 5/5 with both cores; contract 58/58. `git status --short` empty; no conflict markers; commits
on lane/live-verifier only (d55c9c3 8ebb4d3 7286523 511a86b 675c1b8 663b52b 47c84f9 83d1de3 32b460e c595383).

# live-verifier: an independent verifier on another machine plays 8c against the prover

## RUNBOOK (copy these)

The verifier is UP now; the device lanes only need (b) and (c). One process serves every relation and >= 4 sessions at once
(4 concurrent 4096-VU sessions measured: every one accepted, each at the same `t.total_live` as alone).

**(a) start the verifier for any relation on machine Y** (relation-agnostic: the prover's HELLO carries the system; the pod must
expose the port: `research pods create ... --expose-port 7000`; `research pods list` shows the public mapping)

~~~bash
# on the verifier machine (vy-live-verifier: /workspace/venv312 = torch-cpu + numpy + blake3; /workspace/bin/ligero-verify built from the lane tree)
export PYTHONPATH="$SRC/packages/verity/src:$SRC/backends/numerical/python:$SRC/tools/research/src:$SRC"   # SRC = the source tree (lane/live-verifier)
export RESEARCH_GIT_COMMIT=<sha of SRC>                       # -> verifier identity live-verifier@<sha> in every verdict
/workspace/venv312/bin/python -m backends.direct.ligero.live serve --listen 0.0.0.0:7000 --out /workspace/live/sessions \
    --ligero-verify /workspace/bin/ligero-verify --jobs 6 --threads 1 --target-bits 128
# what runs now: /workspace/live/start.sh = the line above in a restart loop (RESEARCH_GIT_COMMIT from /workspace/lv-src/COMMIT),
#   log /workspace/live/serve.out; per-session lines in /workspace/live/sessions/serve.log; one line per finished session in
#   /workspace/live/sessions/index.jsonl; the session trees in /workspace/live/sessions/<session id>/
bash /tmp/lv/ssh_cpu.sh 'tail -f /workspace/live/sessions/serve.log'      # laptop: watch it  (= ssh -p 30898 root@213.173.105.69)
bash /tmp/lv/ship_cpu.sh && bash /tmp/lv/restart_verifier.sh             # laptop: ship the lane tree + restart (ONLY between sessions)
~~~

**(b) run the prover with `--verifier`** (any bench-vu runner; interactive mode only; the warm-up rep keeps local coins, every
recorded rep is one live session of `n_proofs` sub-batches). fp8-ada int-ZK, K=1536, 4096 VUs:

~~~bash
cd <a tree that contains lane/live-verifier at c595383>     # the device lanes' trees need it merged (live.py + run.py --verifier + the vu.py --out fix)
uv run -q research run --on <gpu machine> --project verity --campaign <campaign> --source . --tool bench_vu_fp8 --scratch triton \
   --exclusive --require-result --stage live-fp8-ada --env PYTHONPATH=packages/verity/src:backends/numerical/python:. -- \
   /workspace/venv312/bin/python -m backends.direct.ligero.run --relation fp8-ada bench-vu --zk --mode interactive \
   --batch 4096 --total-vus 4096 --reps 3 --device cuda --verifier tcp://213.173.105.69:30899 \
   --instances-cache /workspace/instances-cache --dump-dir '$RESEARCH_RUN_DIR/proofs' --out '$RESEARCH_RUN_DIR/result.json'
# bf16-ampere (--tool bench_vu): ... run --relation bf16 bench-vu --zk --mode interactive --batch 4096 --total-vus 4096 --reps 3 --device cuda --verifier tcp://...
# bf16-hopper/fp8-hopper: ... run --relation bf16-hopper|fp8-hopper bench-vu ...   fp4-nvf4: ... run --relation fp4-nvf4 bench-vu ...
# before a run, from the GPU pod (2 s): the path's RTT and one-flow throughput to the verifier
PYTHONPATH=packages/verity/src:backends/numerical/python:. /workspace/venv312/bin/python -m backends.direct.ligero.live probe --verifier tcp://213.173.105.69:30899 --mb 0.5 --repeat 6
~~~

The result gains `t.total_live`, `net.rtt_ms`, `net.messages`, `net.bytes_out`, `net.bytes_in`, `net.wait_seconds`,
`verify.wall_s`, `verify.cpu_s`; the stdout has one `rep N: live verifier ACCEPTED k/n ...; median rtt; t.total_live` line per
rep; `validation.evidence.live_verifier` holds the verdicts as the prover received them (NOT the independent record -- (c) is).
A REJECT makes the rep fail loudly (`LiveError`), the session dir on the verifier keeps the evidence.

**(c) pull the verifier's session dump into the store and record the verdict** (laptop, no torch needed; the sessions are indexed
by the prover's run id -- `RESEARCH_RUN_ID` travels in the HELLO):

~~~bash
cd ~/projects/verity-main-wt/live-verifier && set -a; source ~/.config/verity/r2.env; set +a
df -h / | tail -1     # < 4 GB free -> ~/projects/verity-main-wt/main/.venv/bin/python /tmp/store_evict.py --target-free-gb 6
uv run -q research data pull <prover run> --from <gpu machine> --project verity            # the prover's result + dumps, as usual -> result=art:...
uv run -q python -m backends.direct.ligero.live record --machine vy-live-verifier --remote-out /workspace/live/sessions \
   --run <prover run> --result <art:... of its bench-result/v1> --preserve
# -> run-files/v1 (the session trees: system.bin, sub_NN.{stmt,proof,coins}, rust_*.json, session.json, verdict.json; ~221 MB per
#    4096-VU session), verification-verdict/v1 (meta.independent=true, verifier="live-verifier@<sha>", mode="interactive"), and on
#    the result:  verified=accepted|rejected --by live-verifier --ref <verdict art>  (+ verifier, verifier_seconds, note)
# reproduce a verdict from the dump alone:  ligero-verify batch --system system.bin --dir <session dir> --target-bits 128 --jobs 8
~~~

**(d) when RTT / t.total_live is bad.** Per sub-batch the critical path is 2 openings (2 x RTT) + the 0.5 MB test message's wire
time + the prover's own work; the proofs (3.7 MB each) travel on a second connection off the critical path. Expected
`net.wait_seconds` ~ n_proofs x (2 x RTT + ~20 ms): 49 x 0.16 s = 7.8 s here. Check, in this order:
1. `live probe --mb 0.5 --repeat 6` from the GPU pod: RTT (HELLO->WELCOME) and the 0.5 MB burst's ack time. Healthy: ack = RTT +
   a few ms after the first (slow-start) frame. Ack ~ 1.5-2 x RTT = the connection is being paced (see 2). Throughput < 200 Mbps
   = the path itself; the 221 MB session then costs bytes/throughput (transfer-bound; a same-DC verifier is the fix).
2. `LIVE_TCP_CC` must be `cubic` (the default) on the prover; the sockets are configured BEFORE connect (47c84f9+). Under the pods'
   default bbr every connection is paced for life and each opening cost ~2 RTTs (138 ms for a 70 ms path). Symptom in the result:
   `net.rtt_ms` ~ 2 x the probe's RTT.
3. DCs: `RUNPOD_DC_ID` in `/proc/1/environ` (this verifier: **EU-RO-1**; the 4090 of this lane: **EUR-IS-2**, 70 ms). A second
   verifier next to the GPU pods is `pods create --name vy-live-verifier-2 --cpu cpu3m --vcpu 8 --disk 50 --expose-port 7000
   --data-center <id>` + `/tmp/lv/bootstrap_cpu.sh` (3 min) + (a); `--verifier` is per run, so lanes point at whichever is closer.
   Nothing else changes (the transcript does not depend on where the coins came from).
4. Verifier side: `tail /workspace/live/sessions/serve.log` (per sub-batch `ACCEPT ... wall 0.09s`), `uptime` (8 vCPU; 4 sessions
   at once used ~6 s CPU per session instead of 4.8), `df -h /workspace` (221 MB per session; 45 GB free at 07:40Z).

## 1. What was built (d55c9c3 .. 83d1de3)

- **Protocol on the wire** (`live.py` docstring): length-prefixed frames on two TCP connections per session. Control: HELLO
  (relation, mode, zk, n_proofs, target_bits, run id, system.bin) / WELCOME; then per sub-batch COMMIT i (c1, c2 of FRESH coins,
  before any prover message of i) -> STMT i (statement bytes, at step 0) -> ROOT i -> OPEN1 (r1, s1) -> TESTS (w, h, q, v) ->
  OPEN2 (r2, s2) + COMMIT i+1 in the same write. Data connection: PROOF i (ligero-proof/v1 bytes) from a sender thread; END;
  VERDICT. The protocol is 8c unchanged -- only the SOURCE of the coins moved from the runner's `os.urandom` to the verifier.
- **Hook** (runner level, smallest diff): `protocol.prove` already takes a `coins` object with `commitments()/open1(root)/open2(root,
  w, h, q, v)`; `live.LiveCoins` implements it over the network, `live.set_statement` hands the statement bytes to it before `prove`,
  and `live.BenchLive` wraps the three bench loops (`begin_rep / coins / proved / end_rep / fields`). `protocol.py` untouched.
  Byte-identity: `live_test.test_live_hook_does_not_change_the_transcript` (same coins -> identical proof bytes); on the real machines
  the prover's `--dump-dir` files and the verifier's session files of run bf7d are identical (147 proofs + 147 coins, sha256).
- **Pipelining** (what overlaps): COMMIT i+1 rides with OPEN2 i (no round trip for step 0 after the first sub-batch); STMT i is sent
  before the prover's work on i, so its transfer overlaps witness/encode/Merkle; PROOF i is sent on the data connection while i+1 is
  proved; Rust verification of i runs on the server's pool while i+1..i+6 arrive. NOT overlapped: the two openings of a sub-batch
  (the prover cannot know r1 before its root, nor r2 before its test message) and the test message's wire time.
- **Timing model**: `net_wait` = seconds `prove` was blocked in commit / open1 / open2, taken back out of the phase clocks they fell
  into, so `t.total` is the prover's own time (comparable to the local-coins numbers); `t.total_live = t.total + net_wait`
  (contract: validated >= `t.total`); `net.rtt_ms` = median of the 2 x n_proofs open1/open2 round trips; `net.messages`,
  `net.bytes_out/in`, `net.wait_seconds`; `verify.wall_s / cpu_s` = the verifier's clocks (`os.wait4` CPU of every ligero-verify).
- **Verifier checks per sub-batch**, before any cryptography: the transcript's coin commitments/openings are exactly the ones IT
  generated for i; the proof's root is the ROOT it received before it opened slot 1; the proof's (w, h, q, v) are the TESTS it
  received before it opened slot 2. Then `ligero-verify verify --coins <own>` on the files it wrote, and at END `ligero-verify batch
  --target-bits` on the session directory (the union bound). The Python file verifier is a test-only fallback (`independent=false`).
- **Session dump** = `<out>/<session>/system.bin, sub_NN.{stmt,proof,coins}, rust_sub_NN.json, rust_batch.json, hello.json,
  session.json (per-message timestamps, bytes, live-check results), verdict.json`; exactly what `ligero-verify batch` reads.
- **Record** (`live.py record`): pulls a run's sessions over ssh, puts run-files/v1 + verification-verdict/v1 (independent=true only
  with the Rust core), labels the prover's result `verified=... --by live-verifier --ref <verdict>`. Runs on a torch-less laptop.
- **Negatives client** (`live.py negatives`), **probe** (`live.py probe`: RTT + one-flow throughput), `research pods create
  --expose-port`.
- **The socket finding** (47c84f9): with the pods' default bbr the kernel paces every connection for life (bbr sets
  SK_PACING_NEEDED at the handshake; a later switch to cubic keeps pacing at 1.2 x cwnd/RTT ~ 100 Mbps for the 0.7 MB window the
  bursty control channel ever grows) -> the 0.5 MB test message was smeared over ~40 ms and each opening cost ~2 RTTs. Options
  set before connect(): cubic from the handshake = unpaced; opening = RTT. `ss -tin` traces and the probe are in the transcript.

## 2. Measurements (4090 EUR-IS-2 -> verifier EU-RO-1, path RTT 69-70 ms; fp8-ada int-ZK K=1536, 4096 VUs = 49 sub-batches x 85 VUs)

| run | sockets | `t.total` (prover) | `net.wait_seconds` | `t.total_live` | `net.rtt_ms` median | verifier `verify.wall_s` / `cpu_s` | accepted |
|---|---|---|---|---|---|---|---|
| r20260923-063416-9f8b (3 reps) | bbr (kernel default), options after connect | 1.44-1.65 s | 11.7-12.2 s | 13.2-13.9 s | 134 | 4.72 / 4.59 | 147/147 |
| r20260923-064820-9c2a (1 rep) | cubic after connect (still paced) | 1.69 s | 8.0 s | 9.66 s | 87 | 4.71 / 4.58 | 49/49 |
| r20260923-065347-65b1 (3 reps) | cubic after connect | 1.40 s | 10.2-12.1 s | 11.6-13.5 s | 133-140 | 4.4 / 4.3 | 147/147 |
| r20260923-072706-c28a (1 rep) | **cubic before connect (47c84f9)** | 1.47 s | 8.14 s | 9.61 s | 70.3 | 5.11 / 4.79 | 49/49 |
| **r20260923-073016-bf7d (3 reps, headline)** | cubic before connect | **1.42-1.70 s** | **6.81-7.02 s** | **8.43-8.52 s** | **68.9-70.3** | **5.0-5.2 / 4.7-4.8** | **147/147** |
| r20260923-073655-908c (4 provers AT ONCE, 1 rep each) | cubic before connect | 1.49-1.73 s | 6.7-7.0 s | 8.42-8.53 s | 67.6-69.8 | 6.7-7.9 / 5.8-6.3 | 4 x 49/49 |
| r20260923-080849-fc65 **bf16-ampere** (vu.py runner; 98 sub-batches x 42 VUs, 1 rep) | cubic before connect | 2.22 s | 13.9 s | 16.1 s | 70.3 | 8.64 / 8.36 | 98/98 |

Per-sub-batch anatomy (server timestamps, headline code): ROOT->OPEN1 0.0 ms server time; OPEN1 -> TESTS received 84 ms
(= RTT + 11 ms tests + 0.52 MB wire); TESTS->OPEN2 0.1 ms; OPEN2 i -> ROOT i+1 113 ms (RTT + STMT + the prover's ~25 ms to the
root); proof i lands 84 ms after OPEN2 i. Pace 199 ms per sub-batch (was 255-300). `net.bytes_out` 221 MB per session
(181 MB proofs + 25.6 MB test messages + 12 MB statements + 0.6 MB coins); `net.bytes_in` 13.6 kB; `net.messages` 349.

Verifier cost per 4096 VUs (fp8-ada, target 128, cpu3m 8 vCPU): 49 x `ligero-verify verify` = 4.4-4.8 s wall = CPU (0.09 s per
sub-batch = 1.1 ms per VU, one core each, 6 in parallel while the session runs) + `batch` at the end 1.3-1.4 s wall (6.2 CPU-s at
6 jobs). `ligero-verify batch --jobs` on one 49-proof session (the whole verification from the dump): 1 job 4.35 s wall / 4.18 CPU-s;
2: 2.81 / 5.36; 4: 1.81 / 6.16; 6: 1.43 / 6.10; 8: 1.24 / 6.58 (8 vCPU = 4 cores x 2 threads; CPU-s inflate past 4 jobs).
Throughput: 11.3 sub-batches/s per core (1 job), 40 sub-batches/s on the pod (8 jobs); bytes in 221 MB per 4096 VUs.
Four concurrent sessions: the pod kept up (`verify.wall_s` 6.7-7.9 s, still inside the 8.5 s sessions).
bf16-ampere costs twice the round trips (98 sub-batches of 42 VUs at l=4096): `net.wait_seconds` 13.9 s = 196 x 71 ms -- the
sub-batch count, not the bytes, is what the live session pays for (see 6, pipelining).

Path: `live probe` from the 4090: RTT 68.6-70.8 ms; 0.5 MB burst -> ack 69 ms (cubic-before-connect) vs 104-137 ms (bbr / kernel
default); 4 MB frames: 86 ms to ack after the first = ~1.9 Gbps on the wire; a session's sustained 221 MB / 11.4 s = 154 Mbps is
the prover's pace, not the path's.

## 3. Negatives

From the 4090 against the live verifier (r20260923-074050-c7b3, fp8-ada 2 VUs, cuda, Rust core; the same six also on the CPU pod's
loopback 06:17Z and in `live_test.py`):

| prover | verdict | where it was caught |
|---|---|---|
| honest | ACCEPT (Rust verify + batch) | -- |
| tamper-column (one opened symbol +1 after the coins were opened) | REJECT `merkle path 0 invalid` | Rust verify |
| root-swap (proof carries another root than the one sent before slot 1 opened) | REJECT `proof root differs from the root committed before coin slot 1 was opened` | live check, before any cryptography (Rust batch also rejects: merkle path) |
| tests-swap (w altered after slot 2 opened) | REJECT `test message (w, h, q, v) differs from the one committed before coin slot 2 was opened` | live check (Rust batch: proximity test failed) |
| prover-coins (challenges from coins the prover sampled: D7's forged transcript) | REJECT `coins are not this session's step-0 coins` | live check (Rust batch `--coins`: not this verifier's) |
| stale-coins (coins replayed from the earlier honest session) | REJECT same | live check (Rust batch same) |
| Fiat-Shamir HELLO | session refused (`interactive only`) | HELLO (`live_test`) |

Each rejection is logged in `serve.log` and kept in the session dir (`verdict.json.live_rejections`).

## 4. Artifacts (all `--preserve`d; push + snapshot in 7)

- headline run r20260923-073016-bf7d: bench-result/v1 **art:e12a50fb274c9684fc5d7dd35835b5ec66fb93ad4eda137b7ff8f25d46453bc4**
  (labelled `verified=accepted --by live-verifier --ref art:9080447d…`), prover run-files art:e963e13f407e6c77dabb0900e5954d036c6b5842eecef50333748b00414c78e8
  (147 dumped proofs), verifier sessions run-files/v1 **art:0a192adcf967497ad96237029e20f4a899fb56b75cf7a982ffd8c71b393d6fb5**
  (s20260923T073037Z-d99b, s20260923T073051Z-4c96, s20260923T073105Z-f75e), verification-verdict/v1
  **art:9080447d5a8b6bbe2ecb5df637ba65164269fa8f36fca827447e9a79b741fd71** (independent=true, live-verifier@47c84f94f5da, 147/147).
- first 3-rep run r20260923-063416-9f8b (bbr sockets): bench-result/v1 art:dcee40f4cfa27fb5756152fa4a22038d1f213ccb3d13efe54cd01eb2686bbc7a
  (labelled verified=accepted), sessions art:588d20455ab0be9135a4252a76a96ba2ab77f816c985ed55bf3c5713478bb358, verdict
  art:209c9052dc0352b74ef65bcba166844f4ee094c5dc8c7516036f0bb34af0a946 (live-verifier@d55c9c3ef84c, 147/147).
- bf16-ampere live run r20260923-080849-fc65 (vu.py runner): bench-result/v1 art:642218b64b36a79fda0121d2e529c4b406e5ea7c632f3971e254b5457cd30bf8
  (labelled verified=accepted --by live-verifier), sessions art:a373c9b3bb79635b5f2706d2559569b5d668ee8093dc3a0376989b83e8bd0b3d,
  verdict art:146519b58e1375925db88398f5c9ae661b13d63a0778be780a6d3a9df03907cb (live-verifier@83d1de38a3c0, 98/98).
- negatives from the 4090: run r20260923-074050-c7b3 (`negatives.json`: all six as expected; not a store artifact -- the six
  sessions are on the verifier, index.jsonl 07:41Z, and in `live_test.py`).
- snapshot **`live-verifier-v1` = art:6f57a14a64bfa07e1fccd8d61a624710e0e41f0fe66834de946a336a8fa599f3** (PRESERVED): the fp8-ada
  headline run's result / verdict / sessions / prover dumps + the first run's. **`live-verifier-v2` = art:cf05bc5ee7f28ffedf69d29d08da0452d278588742d322bace553cff5ff99e8a** (PRESERVED) adds the bf16-ampere row (result, verdict, sessions).
- remote: `research data push --pending` at 07:50Z (bf7d: 5/5 PRESERVED; the prover dumps' blobs were "already there" -- the
  verifier's session files had uploaded the identical bytes) and again at 08:17Z+ (fc65, sessions).

## 5. Pod accounting (budget <= $4.00)

- vy-live-verifier d4maiikv32zn56: cpu3m 8 vCPU $0.44/h, created 05:57Z (a 16-vCPU cpu3m at $0.88/h existed 05:54-05:57Z: ~$0.05).
  To 12:30Z = 6.55 h = $2.88. Stays up for the device lanes; terminate at 12:30Z unless the coordinator says otherwise.
- vy-live-4090 gh0vlgpq7st5s3: $0.74/h, 06:25Z -> **terminated 08:29Z** = 2.05 h = **$1.52** (the bf16-ampere runner test and the
  full device pytest cost the last 40 min). `pods create` itself died on the laptop's full disk after the REST create (registered
  by hand); check-part: reference (host AMD EPYC 7532, load 45-190: a busy shared host).
- Total: $0.05 + $1.52 + $0.44/h x CPU pod hours. **To stay <= $4.00 the CPU pod must go down by ~11:25Z** (5.5 h = $2.43);
  to 12:30Z it is $2.88 and the lane totals ~$4.45. Coordinator's call (6); the default in this note is 12:30Z as instructed.

## 6. Coordinator

- The device lanes' trees must contain lane/live-verifier at **c595383** (or 47c84f9+: the socket fix matters, it halves the
  session time; c595383 adds the vu.py `--out`/run_id fixes the bf16 line in (b) relies on) -- `live.py`, `run.py --verifier`, the three runner hooks, `contract.py` fields. The verifier process is independent
  of their tree version as long as wire version 1 and the proof formats hold; a tree at d55c9c3..663b52b still works (sessions
  accepted) but sees ~2 x RTT per opening.
- The verifier at tcp://213.173.105.69:30899 stays up until 12:30Z; it logs to /workspace/live/sessions/serve.log; restart ONLY
  between sessions (`bash /tmp/lv/restart_verifier.sh`). Disk: 221 MB per 4096-VU session, 45 GB free.
- Recording is (c) above, per prover run, from the laptop; it takes ~1 min per session (the sessions are pulled over ssh).
- DC: EU-RO-1. If the device pods land elsewhere with RTT > 100 ms, the runbook's (d).3 gives a second verifier in 5 min.
- Budget: see 5 -- say if the CPU pod should stop at ~11:25Z (<= $4.00) or run to 12:30Z (~$4.45).
- bf16-ampere: `vu.py bench-vu` on main needs `--run-id <id>` and a literal `--out` path when launched by `research run`
  (relchain/fp4 expand `$RESEARCH_RUN_DIR` and fall back to `$RESEARCH_RUN_ID`); c595383 makes vu.py do the same. Its live session
  pays 2 x 98 round trips (16 s at 70 ms) because bf16 makes 98 sub-batches of 42 VUs.

## 7. Status log

- 06:24Z verifier up (d55c9c3). 06:36Z first 3-rep run accepted 147/147 (rtt 134 ms median). 06:53Z cubic default. 07:10Z
  probe + torch-less record. 07:27Z sockets configured before connect: openings at the RTT (70 ms), t.total_live 9.6 -> 8.5 s.
  07:33Z headline run bf7d recorded. 07:40Z 4 concurrent sessions accepted. 07:42Z negatives from the 4090: 6/6 as expected.
  07:44Z verifier restarted at 83d1de3. 07:50Z push + snapshot live-verifier-v1. 08:08Z bf16-ampere (vu.py runner) live
  session accepted 98/98 (two vu.py one-liners to get the result attached to the run). 08:15Z full ligero pytest on the 4090
  at c595383: 63 passed. 08:29Z 4090 terminated. 08:35Z push --pending (88 artifacts preserved), snapshot live-verifier-v2.
  08:40Z verifier restarted at c595383 (no session running); probe from the laptop answered by live-verifier@c595383b4cdb.

## 8. What remains / next hypotheses

- **Pipelining across sub-batches (the big one).** After the socket fix a session costs n_proofs x (2 x RTT + ~20 ms) on top of
  `t.total`: 49 x 160 ms = 7.8 s for fp8-ada, 98 x 142 ms = 13.9 s for bf16-ampere. The protocol allows sub-batch i+1's step 0 and
  root while i waits for OPEN1 (independent proofs, independent coins; COMMIT i+1 is already there), but `protocol.prove` is
  synchronous per sub-batch and the runners prove sub-batches one after another, so the openings are dead time. Two sub-batches
  in flight (a second thread / two CUDA streams) would hide one RTT per sub-batch; a runner that sends all n roots, gets all n
  (r1, s1), sends all n test messages, gets all n (r2, s2) -- the same 8c per sub-batch, messages grouped -- would make the
  session cost 2 x RTT total (0.14 s) instead of 2 x RTT x n. That is a runner/`protocol.prove` change (lane hp2-host owns
  `protocol.py`); the server already handles any interleaving because every frame carries its sub-batch index.
- **DC placement.** With the sockets fixed the cost IS the RTT: a verifier in the GPU pods' DC (RTT ~0.5-1 ms) makes
  `t.total_live` ~ `t.total` + the 221 MB transfer (~2 s at 1 Gbps). Runbook (d).3.
- **Verifier throughput.** 11.3 sub-batches/s per core; the 8-vCPU pod verifies ~40 sub-batches/s (`--jobs 8`), i.e. ~8 concurrent
  4096-VU fp8-ada sessions at today's pace (5 sub-batches/s each) before verification lags the stream; 4 concurrent were fine.
  For a same-DC verifier (sessions ~10 x faster) the CPU would be the bottleneck: `--jobs 8` + more cores, or `--threads 2` in
  ligero-verify (untested), or verifying the batch only at END (per-sub-batch verification is what makes a REJECT immediate).
- **Verifier cost table per target** (only 128 measured: verify 4.4-4.8 s wall per 4096 fp8-ada VUs, 4.2-6.6 CPU-s depending on
  jobs, 221 MB in; bf16-ampere 8.6 s / 8.4 CPU-s per 4096 VUs, 98 sub-batches). 100 / 80-bit targets not run (no time).
- Disk retention on the verifier (221 MB per session; 44 GB free = ~200 sessions); an `index.jsonl`-driven eviction is a
  10-line addition if the device lanes run many reps.
- `research verify serve` (a tools/research CLI wrapper) was not added; `python -m backends.direct.ligero.live serve` is the entry.

## 9. Anything wrong in the spec

- `--cpu cpu5m --vcpu 16` "~$0.2/h": cpu5m had no stock at 05:55Z; cpu3m is $0.055/vCPU-h ($0.44/h for 8, $0.88/h for 16).
- The spec frames latency as RTT; the dominant effect on RunPod was TCP pacing under the pods' default bbr (2 x RTT per opening
  for bursty flows) -- fixed in the client, but any other bursty request/response tool on these pods has the same problem.
- "labels `--by live-verifier --ref <run>`": the label's `--ref` here is the verification-verdict/v1 artifact (which names the run),
  as verify_record.py does; the run id is in the verdict's meta.
- The bf16-ampere runner (`vu.py bench-vu`) on main does not expand `$RESEARCH_RUN_DIR` in `--out` and does not pick up
  `$RESEARCH_RUN_ID` -- the spec's "all runners" needed two one-line fixes in vu.py (c595383) for the (b) command to work as written
  (the hostphase §8 lines work around it with `--run-id ID` and a literal path).
- Prover-side `verifier.seconds` in the results is still the in-process Python verifier's time (as before); `verify.wall_s/cpu_s`
  are the live verifier's. Both are reported; the contract does not require them to agree.
- The 4090 ran 2.05 h (not <= 1.5): the bf16 runner test and the device pytest at the checkpoint sha were worth the $0.40.
