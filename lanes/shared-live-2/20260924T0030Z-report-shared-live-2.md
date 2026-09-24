---
lane: shared-live-2
kind: report
created: 2026-09-24T00:30Z
status: final
---

CHECKPOINT e2a3b27e (01:01Z) [final] FINAL e2a3b27e: 12/12 cells passed, 30/30 campaign live sessions ACCEPTED, re-verified by shared-live-2 with pinned Rust (51/51 pairs, 32/32 honest sessions + 12/12 dumps batch ACCEPT, G3 negative REJECT); fp8-ada ZK bare/shared local 0.246/0.389 (1.58x), live 0.380/0.669 (1.76x); bf16-hopper local 0.371/0.695 (1.87x), live 1.065/1.326 (1.25x); 23 arts PRESERVED (research data preserved rc 0); pod hinjpqggt7riic terminated 00:53:16Z (404); ~$1.22 pod life
CHECKPOINT e2a3b27e (00:43Z) [open] pulled 5 GB, sha256 = pod for all 12 cells + 2956 session files; my pinned Rust batch on ALL 33 sessions + 12 rep1 dumps: 32/32 honest ACCEPT, t2 negative REJECT (rc 1), 12/12 dumps ACCEPT; 12 cell arts PRESERVED (remote) + labelled verified=accepted by shared-live-2; pushing 7 session groups + 3 single sessions + run-files now
CHECKPOINT e2a3b27e (00:33Z) [open] campaign COMPLETE: 12/12 cells passed (5 reps each, --zk --mode interactive --pipeline 4, 4096 VUs, l=16384, code fe0c4f48 on 4090); 30/30 campaign live sessions ACCEPTED (live check + Rust per pair + Rust batch >= 2^-128); my independent Rust re-verify of 3 shared-live sessions (fp8-ada x2, bf16-hopper x1) ACCEPT 51/51 pairs + 3/3 batches, swapped-coin negatives REJECT; fp8-ada ZK local bare 0.246 / shared 0.389 (1.58x), live t.total_live 0.380 / 0.669 (1.76x); bf16-hopper local 0.371 / 0.696 (1.87x), live 1.065 / 1.326 (1.25x); pulling 5 GB for custody
CHECKPOINT e2a3b27e (00:30Z) [open] successor of shared-live (died ~23:49Z); read its report (ends 23:32Z, campaign running); collecting /workspace/runs/campall.out + 12 run dirs + 35 live sessions from pod hinjpqggt7riic; no new work

# shared-live-2 — collect, verify, custody and report shared-live's 4090 campaign

Brief: coordinator message 00:28Z. Worktree `~/projects/verity-main-wt/shared-live`, branch `lane/shared-live` @ e2a3b27e (clean).
Pod vy-shared-live = RunPod hinjpqggt7riic (4090, EU-RO-1). Deadline 01:15Z. No new pods, no feature work.

## Log
* 00:27Z worktree clean at e2a3b27e. Predecessor report read (last entry 23:32Z: G3 fixed, G3 negative REJECTED, campaign started).
* 00:28Z pod: `campall.out` has all 12 cells `rc=0` + `rust <cell> rc=0` (camp.sh: per relation/round bare-local, shared-local,
  bare-live, shared-live; `b.sh ... --zk --mode interactive --batch 16384 --pipeline 4 --total-vus 4096 --target -128 --reps 5
  --dump-dir .../dump --dump-reps 1`; live = `--verifier tcp://127.0.0.1:7000`, the `live serve --jobs 4 --threads 1 --target-bits
  128` on the SAME pod; rv.sh = pinned `ligero-verify batch` (+`--system-h` for shared) on each cell's rep1 dump). Pod tree stamp
  `.research-source.json` = fe0c4f48 (lane/shared-live, clean) -- e2a3b27e only adds live_test.py, so the measured code = tip code.
  C-fp8-ada-shared-local is complete (92M, same as its A twin; the smaller dir entry is just fewer files than the B dirs).
* 00:30Z laptop disk had 4.9 GiB free: `research data evict --target-free-gb 15` (evicts only blobs PRESERVED on the remote) ->
  15 GB free; pulling `/workspace/{runs,live/sessions}` (~5 GB) by ssh tar to `~/scratch/shared-live-2/`.
* 00:31Z extracted every cell's result.json (`~/scratch/shared-live-2/extract.{py,json}`):
  - all 12 `validation: passed`; every local/live rep self-verified (dumps 13/13 or 25/25, batch accept); Rust rv.sh on each rep1
    dump: all accepted, `system pinned` (fp8-ada+hash / bf16-hopper+hash for shared), union bound 2^-128.32 (fp8 bare, 13 proofs),
    2^-128.66 (fp8 shared, 26), 2^-128.05 (bf16 bare, 25), 2^-128.28 (bf16 shared, 50).
  - live cells: 5 sessions each, every verdict `accepted`, accepted_subbatches = n_proofs (13 or 25), 0 live rejections, 0 errors,
    Rust batch rc 0, own_coins = n, system_pinned; verifier core ligero-verify sha256 4eb710af... (= /workspace/bin/ligero-verify).
  - index.jsonl: 33 sessions = t1 (pipelined, ACCEPT 13/13) + t2 (G3 negative own-coins-h, REJECTED 0/13 "H: coins are not this
    session's step-0 coins") + t3 (sequential, ACCEPT 13/13) + 30 campaign sessions (all ACCEPT). The coordinator's "35" is 33.
  - gate-fp8-ada (IA, +shared, zk): 13 honest / 98 negatives / 0 failures (log only; no result.json by design of gate-vu).
* 00:32Z **independent re-verify (this lane, on the pod, pinned binary sha256 4eb710af...)**, outputs `/workspace/reverify/`:
  per pair `verify --system system.bin --statement X.stmt --proof X.proof --coins X.coins --soundness-bits 128 --system-h
  system_h.bin --proof-h X.hproof --coins-h X.hcoins` + `batch --system-h`:
  - s20260923T234846Z-e5a2 (C fp8-ada shared-live): 13/13 rc 0; batch ACCEPT 26 sub-batches 2^-128.66, system pinned (fp8-ada+hash)
  - s20260923T233422Z-3b64 (A fp8-ada shared-live): 13/13 rc 0; batch ACCEPT 26 sub-batches 2^-128.66, pinned
  - s20260923T234403Z-d977 (B bf16-hopper shared-live): 25/25 rc 0; batch ACCEPT 50 sub-batches 2^-128.28, pinned (bf16-hopper+hash)
  - sanity negatives on e5a2 sub_00: G coins from sub_01 -> REJECT "G: coins are not this verifier's step-0 coins"; H coins from
    sub_01 -> REJECT "H: coins are not this verifier's step-0 coins".
* 00:34Z **pinned Rust batch on everything** (`/workspace/reverify2.sh`, outputs `/workspace/reverify/all/`): all 33 sessions
  (`batch --system system.bin [--system-h system_h.bin] --dir . --target-bits 128`) + all 12 cells' rep1 dumps: 32/32 honest
  sessions rc 0, t2 (own-coins-h) rc 1 = REJECT as intended, 12/12 dumps rc 0.
* 00:35-00:41Z custody of the 12 cell dirs (`~/scratch/shared-live-2/custody.py`, kind proof/v1, tree = result.json + log +
  rust_batch.* + dump/): all PRESERVED on s3://verity-dev (push verified etag-md5), ~5 MB/s up. Pull finished 00:41Z; sha256 of all
  12 cells (`pod_runs.sha256`) and all 2956 session files (`pod_sessions.sha256`) match the pod byte for byte (no truncation).
* 00:42Z sessions grouped per live cell (5 each) + g3tests (t1/t2/t3 run dirs + their 3 sessions); run-files tree = scripts,
  campall.out, gate-fp8-ada, live index.jsonl + serve.log, extract.*, reverify outputs. Pushing.

## FINAL

**Tip `e2a3b27e`** on `lane/shared-live` (clean; no commits by shared-live-2). Base: `453d7cf4` (share-logup-3 FINAL) + merged
`lane/live-2c` `54e748f6` (merge commit `e8cf00f9`, no conflicts) + `fe0c4f48` (the G3 fix: +shared pairs take G AND H coins from the
live verifier) + `e2a3b27e` (live_test.py only). Measured code = `fe0c4f48` (pod source stamp, clean); e2a3b27e changes no runtime file.

**Setup (every cell).** RTX 4090 pod hinjpqggt7riic (EU-RO-1, 40-core EPYC-Rome), `bench-vu --zk --mode interactive --batch 16384
--pipeline 4 --total-vus 4096 --target -128 --reps 5`, rep1 dumped; `+shared` = `--auth included-hash-shared --tile 64x64`; live =
`--verifier tcp://127.0.0.1:7000` = `live serve --jobs 4 --threads 1 --target-bits 128` on the SAME pod (localhost, verifier CPU
shares the host). fp8-ada: 13 sub-batches x <= 341 VUs; bf16-hopper: 25 x <= 170 VUs. Rounds: A fp8-ada, B bf16-hopper, C fp8-ada.

**Table (seconds, per-cell median over 5 reps as reported by the result's `t.total` / `t.total_live`; fp8-ada = median over rounds
A and C, i.e. the mean of the two round medians, round values in brackets).**

| relation | coins | bare | +shared | shared / bare | proof bytes bare / +shared |
|---|---|---|---|---|---|
| fp8-ada | local (t.total) | **0.246** [A 0.244, C 0.248] | **0.389** [0.404, 0.374] | **1.58x** | 66.1 / 94.4 MB |
| fp8-ada | live (t.total_live) | **0.380** [0.374, 0.386] | **0.669** [0.650, 0.688] | **1.76x** | 66.1 / 94.4 MB |
| fp8-ada | live, prover t.total | 0.361 [0.351, 0.370] | 0.658 [0.640, 0.675] | 1.82x | |
| bf16-hopper | local (t.total) | **0.371** | **0.695** | **1.87x** | 118.0 / 170.8 MB |
| bf16-hopper | live (t.total_live) | **1.065** | **1.326** | **1.25x** | 118.0 / 170.8 MB |
| bf16-hopper | live, prover t.total | 1.031 | 1.321 | 1.28x | |

(Pooled 10-rep medians for fp8-ada agree: local 0.246 / 0.389, live prover 0.358 / 0.672.)  Live wire per rep: fp8-ada 107 / 129 MB
out, bf16-hopper 195 / 259 MB; round trips per session 26 (fp8 bare) / 52 (fp8 +shared, 4 per pair) / 50 / 100.

**vs share-logup-3 (non-ZK, local coins, other 4090 pod kx69zewzhawgy1):** fp8-ada bare 0.161/0.157, +shared 0.268 (1.69x);
bf16-hopper bare 0.254, +shared 0.512 (2.0x). ZK here costs +55% (fp8 bare) / +45% (fp8 +shared) / +46% / +36% (bf16) -- a
cross-pod comparison, so indicative only; the shared/bare ratio is slightly LOWER under ZK (1.58x vs 1.69x; 1.87x vs 2.0x). The
fp8-ada+shared <= 1.3x bare target stays NOT met (share-logup-3's device-floor argument holds).

**Accept status.** 12/12 cells `validation: passed` (every rep verified in process; rep1 dumps 13/13 or 25/25 by the Python file
verifier, a self-check). Campaign live: 30/30 sessions ACCEPTED (live check + verifier-side Rust per pair + Rust batch), union bounds
2^-128.32 (fp8 bare, 13 proofs) / 2^-128.66 (fp8 +shared, 26) / 2^-128.05 (bf16 bare, 25) / 2^-128.28 (bf16 +shared, 50), all >= 2^-128,
system pinned. **shared-live-2 independent re-verification** (pinned `ligero-verify` sha256 4eb710af..., on the pod): per pair
`verify --system-h --proof-h --coins-h` on 3 +shared sessions (fp8-ada 3b64 + e5a2, bf16-hopper d977): 51/51 ACCEPT, 3/3 batch
ACCEPT; `batch` on all 33 sessions: 32/32 honest ACCEPT, t2 REJECT; `batch` on all 12 rep1 dumps: 12/12 ACCEPT; swapped-coin
negatives (G coins or H coins of another sub-batch) REJECT "G/H: coins are not this verifier's step-0 coins".

**ZK status.** G and H both masked: G zk, t_pad 256 (k = 16384 + 256), H zk, t_pad 256 (k = 4096 + 256 fp8-ada, 8192 + 256
bf16-hopper), Rust v6 statement `zk: true` (a non-masked H is unparseable in a zk statement, format.rs per shared-live);
proof_class COMPLETE_ZK_BACKEND; claim: malicious-verifier ZK (simulator rewinds V* after step 0, CRH only).

**G3 negative.** `LIVE_NEGATIVE=own-coins-h` (t2, session s20260923T232742Z-ad17, H proved on prover-sampled coins): REJECTED 0/13 by
the live check ("H: coins are not this session's step-0 coins (replayed / prover-chosen coins)") AND by my Rust batch ("13 rejected;
batch reject (sub_00: H: coins are not this verifier's step-0 coins)"). Honest pipelined (t1) and sequential (t3) pair sessions ACCEPT 13/13.

**Integration must merge together:** `lane/shared-live` @ e2a3b27e as one unit -- it already contains share-logup-3 (453d7cf4) and
live-2c (54e748f6). Merging share-logup-3's `+shared` with live-2c's live verifier WITHOUT fe0c4f48 reopens G3 (H on prover-sampled
coins_h); fe0c4f48 changes live.py / relchain.py / protocol.py only (no system, statement or proof format change; pins unchanged).

**Known gaps.**
* Live numbers are same-pod localhost: the verifier (live check + Rust, 4 jobs) competes with the prover for the host, so
  t.total_live / local t.total = 1.55x (fp8 bare), 1.72x (fp8 +shared), 2.87x (bf16 bare), 1.91x (bf16 +shared) is contention +
  per-sub-batch round-trip serialization, not network; not separated. No cross-host live run of +shared in this lane.
* bf16-hopper bare-live is noisy (reps 0.88-1.51 s) and disproportionately slow vs its local 0.37 s, which is why its live
  shared/bare (1.25x) is below local (1.87x); one round only for bf16-hopper (5 reps), unexplained.
* bf16-hopper +shared live rep1 3.69 s (cold graph capture) -- excluded by the median, reported here.
* Only fp8-ada and bf16-hopper were measured; fp8-hopper / bf16-ampere +shared live not run.
* The Python in-process/file verification is a self-check; independence rests on the Rust `ligero-verify` (pinned binary).
* Standing caveats from the statement: SHAKE-256 challenge expander and hash parameters marked placeholder (`hash_placeholder`).
* live_test.py (e2a3b27e) not re-run by shared-live-2 (pod tree is fe0c4f48). LogUp range-cut stretch goal: not started (out of scope).
* The coordinator's "35 sessions" = 33 (30 campaign + t1/t2/t3).

**Artifact ids** (all kind proof/v1 unless noted; every push `PRESERVED ... verified etag-md5` on s3://verity-dev; labels
lane=shared-live, relation, zk=true, mode=interactive, authentication (excluded / included-hash-shared), K=1536, B=4096,
proof_class=COMPLETE_ZK_BACKEND, hardware, by shared-live-2; `verified=accepted` + `verifier=ligero-verify sha256 4eb710af ...`
by shared-live-2 on every art below except g3tests (mixed honest + negative; `note` label instead) and run-files; labels-sync pushed):
* cells (result.json + log + Rust batch verdict + rep1 dump):
  A-fp8-ada bare-local `art:c1e415dec055461559341949af2018e8b45bb4dbedb19973265c9dadbf9fe3a1`,
  bare-live `art:bad689530dadd59b518b3b460a940cc4a0e4ed6a711ebf9fad933bca382b7fc8`,
  shared-local `art:fa2be3987db0b45687f51caff76c84bc798c28ca6025cbc2117516e94b520289`,
  shared-live `art:a9ffa038df66774ae9049c5f5cc7eebd6c5d614d57e8fd8118f6c9f7562c6923`;
  B-bf16-hopper bare-local `art:62395cc93f0e60897b8e2eaad6b540faf469b2d424218ba1941f85798a2adfce`,
  bare-live `art:13eabfa7b50743573013510ae66b214d92b25c4407280112f0a5958168b46910`,
  shared-local `art:b460261fb4b0c32429e3e865a6c364543396936ddda1c353ffccfb1ce2977ffe`,
  shared-live `art:9685cf18682ac6d6427a157816096a87d371d83e9a082b860aae9efedbcb124d`;
  C-fp8-ada bare-local `art:34ddb3d85ce2b97dde08c5b20687b46d69de257eca4571b87ce35235dd464692`,
  bare-live `art:1335722dca924c37c75406d714d54e5058b92cee10efa7bfd387fda33a1fd926`,
  shared-local `art:222ce4f21cfbad030366d2257da263b1103b21bf0e1e2244d440e6a1d606acc8`,
  shared-live `art:c6c79ecedd4695adbafb23d6b59eb7af0a065037bdb83cf1a95a46e91c30b380`.
* live sessions, 5 per live cell: A bare `art:45fc95d536764bf040d26a317413030e4d2b4defa517fd0813754cd4dbf4514f`, A shared
  `art:12cfe9d96c36620804b56d230f7e39556f3fedd0d94ad1599bf9705bee1e824f`, B bare
  `art:1e876f2446222b4f915f04ac5e29a7f8586fde415973e02f7dcc9c80dd030972`, B shared
  `art:bfbd9da22fa1166c8aad7e5b03a078192f437c2a108e366c01fd0456515943f9`, C bare
  `art:fbcd1167d9387361e07db257e2d1756939f59d8a355b1d9bf7cfbbad10050ffa`, C shared
  `art:55fc2c3320a23a5ded22c9b6d4917f3209c186463f03632746de0fcf748a888b`.
* G3 tests (t1 pipelined / t2 own-coins-h negative / t3 sequential: run dirs + sessions):
  `art:eb30374be4dd1a7d03af2e1f81b2c4a143e86d8ab55a07dcf04be5ea71228748`.
* the 3 sessions re-verified per pair by shared-live-2: 3b64 `art:a62722e13b29ecd02cf3068de4830f8d85f8c341fc82cf91c910ab05a495f152`,
  d977 `art:08d142449462bc601a4021e5f260bc58ac2e6a495a38379f61a5378bf3258b77`, e5a2
  `art:2ce9c590244d2a8e41a1db3e7a9cf650290e2d3f70b4fe085da47cd51dd93a40` (blobs shared with the groups).
* run-files/v1 (scripts, campall.out, gate log, live index.jsonl + serve.log, extract.*, all re-verify outputs, pod sha256 lists):
  `art:759110cab9f6d42a77cefd9c166fc39132fef2cb0b8dd8053696049917aafa2c`.
Pull integrity: sha256 of all 12 cell dirs and all 2956 session files matched the pod before upload (no truncation).
Durability gate 01:00Z: `research data preserved <23 ids> --mode recorded` rc 0, all 23 PRESERVED (etag-md5; 9 also
sha256-readback from a `--mode head` pass that died without output after ~4.6 min); `research data where` shows remote present +
verified for all 23 (output saved in `~/scratch/shared-live-2/preserved_recorded.txt`).

**Pod.** `live serve` stopped 00:45Z (port 7000 closed); pod hinjpqggt7riic **terminated 00:53:16Z** (`research pods terminate`;
RunPod GET -> 404, absent from `pods list`). No new pods created.

**Cost.** Pod life 23:14Z -> 00:53Z = 1.65 h x $0.74/h = **~$1.22** (shared-live ~$0.92 incl. the 23:49-00:28Z idle, shared-live-2
~$0.31). R2: ~4.3 GB new objects. Laptop: evicted 9.4 GB of already-remote blobs to make room (reversible by fetch).
