---
id: r21-live-pipeline/live-pipeline/20260923T0919Z-report-live-pipeline
campaign: r21-live-pipeline
lane: live-pipeline
kind: report (working; updated at every checkpoint)
status: superseded
repo: verity-main-wt/live-pipeline, branch lane/live-pipeline (forked from main cee1f76)
machines: vy-live-pipe = RunPod 3r1nsk03cwbhlj (RTX 4090 SECURE reference part 24564 MiB, EU-RO-1, host AMD Ryzen 9 7950X, $0.74/h, created ~08:48Z)
    the shared verifier vy-live-verifier (tcp://213.173.105.69:30899, EU-RO-1) is used, not restarted.
---

CHECKPOINT 0b40ae8a (05:54Z) [superseded] closed by coordinator 2026-09-25 05:55Z for the cloud switch-over: no sign of life >24 h; branch lane/live-pipeline pushed to origin; uncommitted work (if any) saved in evidence/uncommitted-0554Z*
CHECKPOINT 620e7316 mergeable -- `backends/direct/ligero/{protocol.py, pipeline.py, live.py, relchain.py, live_test.py}` only,
all off cee1f76 (5 files, `git diff --name-only cee1f76 HEAD`; 3 commits).  `--pipeline N --verifier tcp://...` work together:
the per-sub-batch live coin exchange is non-blocking (the prover stage yields a Future the pipeline driver polls; the session
sends each message as soon as 8c allows and a reader thread fulfils the futures), AND the verifier gained a HELLO `window`
(= the prover's pipeline depth; default 1 = today's byte stream): it commits `window` sub-batches ahead and opens each as its
ROOT / TESTS arrive, so N openings are in flight at once.  **The shared verifier must be restarted on this sha to get the
gain** (a prover at 620e7316 against main's server degrades gracefully to the sequential order: measured, accepted).
`git status --short` empty, no conflict markers, no new `.md` in the repo.
Tests: full `pytest backends/direct/ligero` on the pod with the Rust core: 125 passed, 1 skipped at d215a819; at 620e7316
`live_test.py` **7/7** (the pipelined-live byte-identity test now parametrized over window 1 and 2, with the verifier's own
timeline asserting COMMIT 1 < ROOT 0 under window 2 and 8c's order per sub-batch); the full suite at 620e7316 <RUNNING, see 3>.
**Measured (4090, 70 ms RTT injected, fp8-ada int-ZK 4096 VUs = 49 sub-batches, 3 reps, all 147/147 accepted):**
sequential-live **7.41-8.05 s** -> `--pipeline 2/3/4` against a verifier WITH the window **3.82-3.87 / 2.61-2.66 / 1.98-2.04 s**
(net wait 6.92 -> 3.39 / 2.21 / 1.60 s = n_proofs/N x 2 x RTT; t.total 0.44-0.50 s).  Against main's server (no window) the
pipelined prover hides its whole compute but stays on the wire floor: 7.13-7.16 s at any depth -- the verifier's control
connection is strictly ordered per session (ROOT i -> OPEN1 i -> TESTS i -> OPEN2 i -> COMMIT i+1 -> ROOT i+1), 2 x RTT per
sub-batch whatever the prover overlaps.  The spec's `t.total + ~2 x RTT` needs window = n_proofs (49 openings in flight);
window = N gives n_proofs/N x 2 x RTT.

# live-pipeline: --pipeline N and --verifier together (overlap the live coin exchange)

## 1. Design (where the wait became non-blocking, what prove_vus_many does with live coins)

The live coin exchange used to BLOCK inside `protocol._prove_stages` (`src.commitments()/open1()/open2()` each did a synchronous
socket round trip), so the coordinator disabled the pipelined path under `--verifier` (`relchain.py`: `... and live is None`) and
every live-verified session paid `n_proofs x 2 x RTT` of wall, strictly sequential.  Three changes make the two work together,
with the protocol (8c) and the transcript bytes unchanged:

- **`protocol.py` (minimal, ~15 lines).** `_prove_stages` asks the coin source for a *future* at each of the three exchange
  points: `_coin_future(src, "commitments" | "open1" | "open2", ...)` returns `src.<name>_future(...)` when the source offers one,
  else `None`.  For `None` (a local `Coins`, or a live source in a NON-pipelined session) the old blocking call is used -- the
  sequential path is byte-for-byte unchanged.  For a future, the stage `yield`s it (the same mechanism it already uses for CUDA
  events and the SHAKE squeeze) and reads the reply with `.result()` after the driver resumes it.  `protocol.prove` /
  `prove_stages` signatures are untouched (lane hp2-host owns protocol.py; this is the smallest possible hook).

- **`pipeline.py` (`prove_many`).** A live-verifier reply future is tagged `net=True`.  The driver already blocks on the oldest
  waitable when nothing is ready; now, when any in-flight job waits on a `net` future it polls the whole active set (a CUDA event
  and a socket reply cannot be waited on together otherwise) and resumes whichever completes first, so the openings of sub-batch i
  overlap the device work of i +- 1.  The interval in which EVERY in-flight sub-batch is waiting on the verifier (nothing to
  launch, nothing on the device) is accumulated as `net_idle`; the prover's own time is `wall - net_idle`, and `net_idle / n` is
  each sub-batch's `net_wait`.  So `sum(timings["total"]) + sum(hints_host) = wall - net_idle` (t.total) and
  `t.total + net_wait = wall` (t.total_live), preserving `t.total_live >= t.total`.  With no live verifier `net_idle = 0` and the
  path is identical to hp2-host's.

- **`live.py`.** `ProverSession.start_pipeline(n)` spawns ONE network thread that owns the control connection and runs exactly the
  verifier's wire sequence in sub-batch order -- COMMIT 0 is already here; per i: send STMT i, send ROOT i (when the stage hands it
  over), read OPEN1 i, send TESTS i (when the stage hands it over), read OPEN2 i, then read COMMIT i+1 (pipelined behind OPEN2 i).
  The identical byte stream the sequential prover sends, so the server (unchanged) accepts it; the strict-order wire check IS the
  ordering test.  `LiveCoins.{commitments,open1,open2}_future` hand the root / test message to the network thread (`provide_root`,
  `provide_tests`) and return the reply Future (fulfilled by the network thread; a done-callback stores r1,s1,r2,s2 for
  `opened()`); they return `None` when the session is not pipelined, so the sequential path falls through to the blocking calls.
  The two openings' round trips are still timed and appended to `session.rtts` (net.rtt_ms).  `BenchLive.pipeline_factory` starts
  the pipeline and hands out `sess.coins(i)` in order.  `prove_vus_many(batches, coins_factory, ...)` now calls `coins_factory(i)`
  per sub-batch (in order) and, for a live source, fixes the statement (`set_statement`) before proving; PROOF i is queued on the
  data channel (async sender) after the pass.  The `relchain` bench loop drops `and live is None`.

- **The window (620e7316; the part that actually moves t.total_live).**  Measuring the above showed the floor: the verifier's
  `Session._run` was a strictly ordered loop (ROOT i, OPEN1 i, TESTS i, OPEN2 i + COMMIT i+1), so even with every prover wait
  hidden the session's critical path was n_proofs x 2 x RTT.  Now HELLO may carry `window` (the bench sets it to the pipeline
  depth; absent = 1): the server commits the first `window` sub-batches up front and one more behind every OPEN2, and its control
  loop is index-driven -- any STMT/ROOT/TESTS of a COMMITTED sub-batch is accepted in any interleaving, each sub-batch still in
  8c's order (COMMIT j before anything of j; OPEN1 j only after ROOT j; OPEN2 j only after TESTS j; each once; a message about
  an uncommitted sub-batch is refused).  `window` = 1 reproduces the old byte stream exactly (old provers unaffected).  The
  pipelined prover side no longer serializes: `provide_stmt` / `provide_root` / `provide_tests` send at once when COMMIT j is in
  (else the reader thread sends them on COMMIT j), the reader dispatches COMMIT / OPEN1 / OPEN2 by (kind, sub-batch) to the
  futures and times each opening's round trip.  `end()` joins the reader, sends END, reads the VERDICT.
  Wire-order evidence is the verifier's own timeline (`session.json` subbatches[].t_*): under window 2, `sub[1].t_commit_sent
  <= sub[0].t_root_recv`; under window 1, `sub[1].t_commit_sent >= sub[0].t_open2_sent` (live_test asserts both).

`vu.py` (bf16-ampere) has no `--pipeline` support on main (hp2-host implemented pipelining for the registered relations only,
`--pipeline` help: "registered relations"); its live path stays sequential (see 7).

## 2. Measurements (4090 EU-RO-1 -> verifier EU-RO-1; fp8-ada int-ZK K=1536, 4096 VUs = 49 sub-batches)

RunPod placed vy-live-pipe in **EU-RO-1, the same DC as the verifier** -> native path RTT **0.6 ms** (`live probe`: RTT 0.6 ms,
6.6 Gbps), not the 70 ms of the spec's baseline (that 4090 was in EUR-IS-2).  `netem` is denied in the container (no NET_ADMIN),
so to reproduce the baseline's 70 ms regime on the SAME hardware for BOTH arms I put a userspace latency proxy on the pod
(`/tmp/lp/latproxy.py`: decoupled reader/writer per direction, +35 ms one-way = 70 ms RTT, bandwidth preserved) and point
`--verifier` at it.  Both the native (0.6 ms) and the injected-70 ms numbers are reported.  Two verifiers: **shared** = the
campaign's vy-live-verifier tcp://213.173.105.69:30899 (main's live.py, no window; proxy 127.0.0.1:37000 -> it), **win** = the
same server code at 620e7316 run by me on the 4090 pod's CPU (Ryzen 9 7950X, `live serve --jobs 8`, Rust core
ligero-verify 3532751cc4928649; proxy 127.0.0.1:37001 -> 127.0.0.1:38000) -- the shared verifier cannot be restarted by this lane.
Command (all arms): `run.py --relation fp8-ada bench-vu --zk --mode interactive --batch 4096 --total-vus 4096 --reps 3 --device
cuda [--pipeline N] --verifier tcp://... --dump-reps 1`; t.total / t.total_live / wait / rtt are the result's medians over the
3 reps, the range is the per-rep `t.total_live` lines; accepted = sum over the 3 sessions (49 sub-batches each).

| arm | run | verifier | RTT ms | t.total s | t.total_live s (reps) | net.wait s | accepted |
|---|---|---|---|---|---|---|---|
| sequential-live | r20260923-092709-b9d6 | shared, 70 ms | 71.0 | 0.487 | 7.435 (7.42-8.05) | 6.948 | 147/147 |
| `--pipeline 2` (prover only, 0a0a2a72) | r20260923-093742-6933 | shared, 70 ms | 70.9 | 0.577 | 7.154 (7.13-7.16) | 6.578 | 147/147 |
| `--pipeline 3` (prover only, d215a819) | r20260923-093105-4f9f | shared, 70 ms | 71.0 | 0.568 | 7.148 (7.13-7.15) | 6.581 | 147/147 |
| `--pipeline 4` (prover only, 0a0a2a72) | r20260923-093845-4767 | shared, 70 ms | 70.9 | 0.573 | 7.157 (7.13-7.16) | 6.584 | 147/147 |
| sequential-live | r20260923-094636-4abe | win, 70 ms | 70.5 | 0.495 | 7.411 (7.41-8.00) | 6.916 | 147/147 |
| `--pipeline 2` + window 2 | r20260923-094807-2b46 | win, 70 ms | 70.5 | 0.472 | **3.866** (3.82-3.87) | 3.394 | 147/147 |
| `--pipeline 3` + window 3 | r20260923-094728-b3c8 | win, 70 ms | 70.6 | 0.453 | **2.658** (2.61-2.66) | 2.205 | 147/147 |
| `--pipeline 4` + window 4 | r20260923-094857-bcc3 | win, 70 ms | 70.5 | 0.441 | **2.040** (1.98-2.04) | 1.599 | 147/147 |
| `--pipeline 3` at 620e7316 vs main's server (compat) | r20260923-094935-1f61 | shared, 70 ms | 70.9 | 0.558 | 7.160 (7.12-7.17) | 6.602 | 147/147 |
| sequential-live | r20260923-093947-ab75 | shared, native | 0.8 | 0.452 | 0.518 (0.51-1.10) | 0.066 | 147/147 |
| `--pipeline 3` (prover only) | r20260923-094024-61a3 | shared, native | 0.6 | 0.451 | 0.496 (0.44-0.51) | 0.045 | 147/147 |

Reading: sequential 7.4 s = t.total 0.49 + 49 x (2 x 70.5 ms + ~1 ms) = 0.49 + 6.92.  Prover-only pipelining hides the
prover's 0.5 s (and `split.hints_seconds` 0.114 -> 0.003) but the wire floor stays: 7.15 s at depth 2, 3 and 4 alike.  With the
window the wait scales as 49/N x 2 x RTT: 3.39 / 2.21 / 1.60 s measured vs 3.46 / 2.30 / 1.73 predicted (N = 2/3/4), and
t.total_live = t.total + wait within 5 ms -- `t.total_live >= t.total` holds in every rep.  The verifier's own wall (its Rust
verification of 49 proofs, off the prover's clock) is 3.8-4.1 s on the 7950X and 6.8-7.5 s on the shared pod.  At native
0.6 ms RTT the live overhead is 45-66 ms either way (the openings cost ~0.5 ms each), so the device lanes in EU-RO-1 gain
nothing from any of this; the lanes at 70 ms gain 5.4 s of 7.4 s per rep at depth 4.  Spec baseline r20260923-073016-bf7d
(4090 EUR-IS-2: t.total 1.42-1.70, t.total_live 8.43-8.52) had a slower prover pass than this pod's 0.45-0.49 s (its path was
also transfer-bound per live.py's docstring); the wire floor 49 x 2 x RTT = 6.9 s is the same.

## 3. Byte-identity + tests + gate

- **Byte-identity on the real configuration (GPU, window 3, 70 ms):** run r20260923-095544-f088 (`--pipeline 3 --verifier
  <win proxy>`, fp8-ada interactive **non-ZK**, 4096 VUs, 1 rep, dumped; 49/49 accepted, t.total_live 2.649 s).  For
  sub-batches 0, 1, 2, 3, 24, 47, 48 (incl. the ragged 16-VU last one) the plain sequential `prove_vus` with the VERIFIER'S coins
  (`sub_NN.coins` from its session dump s20260923T095600Z-56f1, replayed as a local `Coins`) gives bytes equal to the prover's
  dump AND to the proof the verifier received (3,467,980 B each) -- `BYTE-IDENTITY OK` (/tmp/replay_identity.py on the pod).
  The ZK arms cannot be byte-compared across two provings (the ZK masks' keys are `os.urandom`, protocol.py `_masks`); for them
  the evidence is the verifier's acceptance with its own coins + `ligero-verify batch` per session (147/147 in every arm).
- **Tests (pod, Rust core `LIGERO_VERIFY=/workspace/bin/ligero-verify`):** `pytest backends/direct/ligero` at 620e7316:
  **126 passed, 1 skipped** (2:04); at d215a819: 125 passed, 1 skipped.  `live_test.py` 7/7, incl.
  `test_pipelined_live_matches_sequential_and_is_accepted[1|2]` (pipelined vs sequential with the same coins, verifier accepts,
  wire-order asserts from the verifier's timeline) and the negatives (replayed / prover-chosen coins refused).
- **Compatibility:** prover at 620e7316 vs main's verifier (no window): r20260923-094935-1f61, 147/147 accepted, the sequential
  wire order (7.12-7.17 s).  Verifier at 620e7316 vs the sequential prover path (window 1): r20260923-094636-4abe, 147/147.
- **Gate:** `run.py --relation fp8-ada gate-vu --device cuda` at 620e7316: **1 honest sub-batch, 92 negatives, 0 failures**
  (relation gates untouched by this lane).

## 4. Artifacts

All 14 runs (`validation: passed`, contract-valid) pulled into the store from vy-live-pipe, campaign r21-live-pipeline; every
bench-result/v1 labelled `arm= live_verifier=shared|win rtt_ms_path= pipeline= window= --by live-pipeline --ref <run>`;
every run's verifier sessions recorded with `live record` (run-files/v1 = the session trees, verification-verdict/v1 =
the aggregate verdict, `independent: true`, Rust core).  Snapshot **live-pipeline-v1 =
art:5ae1b61d2656ad5c9e90cb2cb2875fd97dc1bbf34eb9f7c7f5363b78b418a649** (39 members: 14 results + 13 verdicts + 13 run-files
trees... the bf16 run included).  Trees: d215a819 (4f9f), 0a0a2a72 (6933, 4767, ab75, 61a3), 620e7316 (the rest).

| run | arm | result (bench-result/v1) | verdict (verification-verdict/v1) | recorded by |
|---|---|---|---|---|
| r20260923-092709-b9d6 | seq, shared, 70 ms | art:3892baf8b3ce54fd | art:73e9c29f81dc22a4 | live-verifier: `verified=accepted`, 147/147 |
| r20260923-093105-4f9f | p3 prover-only, shared, 70 ms | art:f477dff474e9ddc0 | art:67d0d5c3fe96ccd5 | live-verifier: `verified=accepted`, 147/147 |
| r20260923-093742-6933 | p2 prover-only, shared, 70 ms | art:4a2d1738c8a66192 | art:7bdd121cf1f24abd | live-verifier: `verified=accepted`, 147/147 |
| r20260923-093845-4767 | p4 prover-only, shared, 70 ms | art:7003c0c05750e7d8 | art:cc953e2db848ba71 | live-verifier: `verified=accepted`, 147/147 |
| r20260923-093947-ab75 | seq, shared, native 0.8 ms | art:c7a521d5414704d3 | art:9f88dd5a1abfea9c | live-verifier: `verified=accepted`, 147/147 |
| r20260923-094024-61a3 | p3 prover-only, shared, native | art:79e91f7ebb7bf12e | art:793890c92bb1f1c7 | live-verifier: `verified=accepted`, 147/147 |
| r20260923-094935-1f61 | p3 @620e7316 vs main's server (compat) | art:e508ddb8593b97cd | art:c733ec3b2d27fd0f | live-verifier: `verified=accepted`, 147/147 |
| r20260923-104318-2038 | **bf16** seq, shared, 70 ms | art:98204257938d14a2 | art:f054ee951c2802d1 | live-verifier: `verified=accepted`, 294/294 |
| r20260923-094636-4abe | seq, win, 70 ms | art:85e60193e890f1b4 | art:df35c573368ec49b | live-pipeline: `verified_by_own_verifier_instance=accepted`, 147/147 |
| r20260923-094807-2b46 | p2 + window 2, win, 70 ms | art:8ec86dfede7d1e6e | art:e7c81be2320755bd | live-pipeline: same, 147/147 |
| r20260923-094728-b3c8 | p3 + window 3, win, 70 ms | art:b7392c1cfce00d69 | art:00bb571cc5b9eba2 | live-pipeline: same, 147/147 |
| r20260923-094857-bcc3 | p4 + window 4, win, 70 ms | art:a00097f7d8c458d7 | art:d1c89309035be329 | live-pipeline: same, 147/147 |
| r20260923-095544-f088 | p3 + window 3, non-ZK identity | art:8b89af3117d57600 | art:394e5163b9dde72c | live-pipeline: same, 49/49 |

(ids abbreviated to 16 hex; the full list is the snapshot's members; /tmp/lp/artifacts.json on the laptop has run -> result /
verdict / run_files in full.)  The win arms' verdicts are NOT labelled `verified= --by live-verifier`: their verifier was my
instance of live.py 620e7316 on the prover's pod (Rust core, verifier-generated coins, `independent: true` in the verdict's
sense, but not the campaign's independent machine); the label says so (`verifier_note`).  The bf16 run: `vu.py bench-vu
--zk --mode interactive 4096 VUs` = 98 sub-batches x 2 RTT, sequential (no `--pipeline` in vu.py): t.total_live 14.70-14.84 s,
net wait 13.9 s, 98/98 x 3 accepted -- the sequential live path is unchanged by this lane (the spec's 16.1 s was the EUR-IS-2 path).

## 5. Pod accounting

vy-live-pipe 3r1nsk03cwbhlj: RTX 4090 reference part (24564 MiB), EU-RO-1, $0.74/h, created ~08:48Z, **terminated 10:47Z**
(`pods terminate 3r1nsk03cwbhlj`; confirmed gone from `pods list`; machines.toml entry annotated TERMINATED).  **~2.0
pod-hours, ~$1.47** of the <= 2.5 h / ~$2 budget.  Work on it: bootstrap (venv312, ligero-verify build), full pytest x 2, 14
bench-vu runs (each ~1 min incl. warm-up), the byte-identity replays, the fp8-ada gate, the bf16 operand build (2.5 min).
Also used, not restarted: the shared verifier vy-live-verifier (10 runs x 3 sessions + bf16's 3 sessions recorded from its dump).
No other pod.

## 6. Coordinator

- Mergeable at **620e7316** (5 files off cee1f76, 3 commits: d215a819 non-blocking exchange + pipelined-live path; 0a0a2a72
  accounting; 620e7316 the window).  Merge for the 10:15Z / ~11:30Z windows.  **To realise the gain the shared verifier must run
  live.py at (or after) 620e7316** -- `live serve` restart on vy-live-verifier; old provers and the sequential path are unaffected
  (window defaults to 1 = identical bytes).  Until then `--pipeline N --verifier` is safe and accepted, just on the wire floor.
- The verifier at tcp://213.173.105.69:30899 was used, not restarted.
- Status: 10:15Z code + tests + measurements done, gate-vu passed; 10:47Z pod terminated; 11:10Z all 14 runs pulled, labelled,
  recorded (verdicts + session dumps, `--preserve`); snapshot live-pipeline-v1 created and its manifest PRESERVED (12:01Z);
  the batch pushes reported 47/47, 22/23 and 8/11 preserved, and two `research data push` jobs (--pending, and the 39 members
  explicitly) were still running at 12:15Z against a laptop uplink shared with other lanes' pushes -- if the coordinator
  sees a member not preserved, `uv run research data push --pending` from any worktree finishes it (idempotent).

## 7. What remains / wrong in the spec

- **Spec's target formula.**  "t.total_live approaches t.total + ~2 x RTT + transfer" is not reachable by prover-side work: the
  verifier serialised the openings per session (2 x RTT per sub-batch, COMMIT i+1 only behind OPEN2 i), so the prover-only
  change (what the spec's "how" describes) hides only t.total (~0.5 s of 7.4 s).  The window fixes it on the verifier side; with
  window = N the floor is n_proofs/N x 2 x RTT (2.0 s at N = 4), and the spec's ~2 x RTT would need window = n_proofs (49 openings
  in flight: fine for the server -- it is one thread per session, index-driven -- but then the pipeline depth on the device no
  longer matches; a `--window` decoupled from `--pipeline` is a 3-line follow-up).
- **"Serves >= 4 concurrent sessions" is not a way out**: striping one run over N sessions fails `batch_bound` (every statement
  claims n_proofs = 49; the batch verifier requires the claim to equal the sub-batches presented per session) and would split
  the 4096-VU claim into N independent 128-bit claims.  Not done.
- **`live record` for the win arms**: it reads `--machine vy-live-verifier`'s dump; the windowed sessions are on vy-live-pipe.
  Recording them as `verified=accepted --by live-verifier` would be wrong (the verifier was my own instance of the same code, on the
  prover's pod); they are pulled as run-files and labelled `--by live-pipeline`.  The shared-verifier arms are recorded normally.
- **bf16-ampere `vu.py bench-vu`**: main's `vu.py` has no `--pipeline` (hp2-host: registered relations only); its live path is the
  sequential one -- unchanged by this lane, so its 98 x 2 x RTT = 16 s stays until `ChainRunner` gets a `prove_vus_many`.  Not
  run here (the spec asked for one run; it would only reproduce the live-verifier lane's number on a same-DC path).
- **ZK byte-identity** is impossible by construction (random mask keys); the spec's item 4 holds for non-ZK (shown) and, for ZK,
  as "the verifier accepts every proof with its own coins".
- The 4090 landed in the verifier's DC (0.6 ms); the 70 ms regime is injected by a userspace proxy (bandwidth preserved), so the
  70 ms numbers are a clean constant-delay link, not the EUR-IS-2 path (which live.py's docstring says was transfer-bound at
  115-150 Mbps: there the proof stream, not the openings, may dominate -- the window does not change the bytes).
