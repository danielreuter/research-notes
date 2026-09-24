---
lane: ligerito-relation-3
kind: report
created: 2026-09-23T23:55Z
status: final
branch: lane/ligerito-relation-2 (worktree ~/projects/verity-main-wt/ligerito-relation-2; taken over per the coordinator's launch message, predecessor stopped ~23:24Z mid-merge)
owns: backends/direct/ligerito/{prove.py, proof.py, run.py} (+ tests beside them)
pods: vy-ligerito-relation-2-veritor-campaign (RTX 4090, reused; predecessor tree /workspace/lr2)
---

CHECKPOINT acfd4dc (01:04Z) [final] FINAL 498f9014 (01:12Z, pushed): --zk emits LGSC0004, ZK keys pinned (verify-rs-4 derivation; pinned 0e4ef1d1 accepts 498f9014 gates 10/10 + real-size 4096 ZK); R3-7/R3-10 closed, R3-2/R3-8 closed; gates 10/10 0 failures; 4096 fp8-ada ZK 0.823 s / 916,527 B / 42 rounds / 15.69 GiB vs non-ZK 0.594 s / 701,728 B / 48 / 16.0 GiB (NON_ZK_PROOF_DIAGNOSTIC both); live ZK RO c20260924T003626Z-5aa5 ACCEPTED, verify-session 2^-128.43; 14 arts remote=1; pod terminated 01:00Z (~$0.86 this lane); all handoffs answered
CHECKPOINT 498f9014 (01:03Z) [final] FINAL 498f9014 (01:08Z, pushed): --zk emits LGSC0004, ZK keys pinned (verify-rs-4 derivation; pinned 0e4ef1d1 accepts 498f9014 gates 10/10 + real-size 4096 ZK); R3-7/R3-10 closed, R3-2/R3-8 closed; gates 10/10 0 failures; 4096 fp8-ada ZK 0.823 s / 916,527 B / 42 rounds / 15.69 GiB vs non-ZK 0.594 s / 701,728 B / 48 / 16.0 GiB (NON_ZK_PROOF_DIAGNOSTIC both); live ZK RO c20260924T003626Z-5aa5 ACCEPTED, verify-session 2^-128.43; arts remote=1 (14, listed in FINAL); pod terminated 01:00Z (~$0.86 this lane); handoffs answered (verify-rs-5 unblock note: pod gone, inputs on R2 ef6b9392)
CHECKPOINT 498f9014 (01:01Z) [final] FINAL 498f9014 (01:01Z, pushed): --zk emits LGSC0004, ZK keys pinned by verify-rs-4 derivation (pinned 0e4ef1d1 accepts 498f9014 gates 10/10 + real-size 4096 ZK); R3-7/R3-10 closed (record-only slots; red-team A/B/C rejected), R3-2/R3-8 closed; gates 10/10 0 failures; 4096 fp8-ada ZK 0.823 s / 916,527 B / 42 rounds / 15.69 GiB vs non-ZK 0.594 s / 701,728 B / 48 / 16.0 GiB (class NON_ZK_PROOF_DIAGNOSTIC both); live ZK RO c20260924T003626Z-5aa5 ACCEPTED, verify-session 2^-128.43; arts remote=1: 6efa1502 f7049d60 7a11540a daa3e099 11dff26a 848e02cc edbb086c 21d950a2 3b95dfcc 18f008f6 12022524 80b4e073 b3fc907c ef6b9392; pod terminated 01:00Z (~$2.44 lifetime, ~$0.86 this lane)
CHECKPOINT none (00:45Z) [open] 498f9014 (00:52Z): final gates @498f9014 10/10 0 failures (ZK with LIGERITO_ZK_REBUILD_F=1; non-ZK Rust pinned pass; ZK Rust --allow-any-key 2/2 + 100/100 each); R3-7 GPU test @498f9014 6/6 both modes, cold verify-dir now also rejects A/B; live ZK 7f35c223 on RO ACCEPTED c20260924T003626Z-5aa5, verify-session authenticated 2^-128.43 (3 attempts) art:ef6b9392; meas art:80b4e073. Next: verify-rs-4 0e4ef1d1 pinned on the pod over 498f9014 gates + real-size ZK + live, push, FINAL, terminate
CHECKPOINT 7f35c223 (00:36Z) [open] 7f35c223 (00:37Z): gates e1114b4c 10/10 0 failures art:6efa1502; ZK keys = verify-rs-4 derivation (15/15) art:18f008f6; LGSC0004 at 4096 VUs needed a fix (6dda159a: drop/rebuild the z_to_f copy; OOM otherwise): ZK 0.823 s / 916,527 B / 42 rounds / 15.7 GiB vs non-ZK 0.594 s / 701,728 B / 48 / 16.0 GiB; live ZK on RO ACCEPTED c20260924T003234Z-a1a0, verify-session authenticated, R3-10 claim 2^-126.42 (3 reps = 3 attempts); rerunning with reps-aware sizing (2^-130/proof). R3-7 GPU test 6/6 art:12022524
CHECKPOINT e1114b4c (00:18Z) [open] e1114b4c (00:24Z): 10 gates on ad9377ae 0 failures (5 relations x non-ZK/--zk; Rust pinned = non-ZK pass, ZK refused as unpinned; Rust --allow-any-key accepts every ZK dump, ZK keys match verify-rs-4's derived digests); R3-7 verify-session derives slots from the verifier record only (record_slots), R3-10 attempts via --sessions-root, 8c75fc4c; merged sumcheck-3 796d8a11 (12 coins, R3-4 claim-support check) 6910bf9e; rerunning gates + R3-7 GPU test + ZK keys on e1114b4c. Next: 4096-VU ZK vs non-ZK measurements, live ZK session
CHECKPOINT ad9377ae (00:01Z) [open] took over lane/ligerito-relation-2 worktree: merge sumcheck-3 62f24d4 committed 1339c7cf (layout/sumcheck = theirs); predecessor's LGSC0004 --zk emission committed e61b24fe (its 23:40Z pod gate fp8-ada --zk LGSC0004: 4+96, 0 failures Python; Rust: ZK key 8c4cd91f unpinned); R3-6 (vf<=n_c-4 enforced in Prover) + R3-2 (t_pad iff >0, params canonical+typed) + R3-8 (word widths) 7135d5d5; gate negatives for both ad9377ae. Next: 10 gates (5 relations x ZK/non-ZK) on the 4090, R3-7
# ligerito-relation-3 — LGSC0004 under --zk, R3-7 live coin binding, R3-2/R3-8 reader strictness, 4090 ZK numbers

## Log

* 23:50Z read relaunch §0/§3, Ligerito brief §9, ligerito-relation-2 report + handoffs (sumcheck-3 x2, red-team-3 x2,
  live-2c, verify-rs-3 asks), red-team-ligerito-3 report (FINAL draft + R3-* table), sumcheck-3 and verify-rs-3 reports.
* 23:55Z worktree state = the predecessor's 23:49Z snapshot (`evidence/uncommitted-2349Z.*` in its notes dir): MERGE_HEAD
  62f24d42 (sumcheck-3); `layout.py` UU but the worktree copy is byte-identical to theirs (theirs already carries
  relation's fp4 `y_end` patch as 3d5a731, so "ours" adds nothing); sumcheck.py / sumcheck_test.py / sumcheck_zk_test.py
  staged = theirs; prove.py / run.py = the predecessor's uncommitted LGSC0004 emission work (not yet run on a GPU as far
  as its report says). No commits on the branch after 32e9bd59.
* 00:00Z **merge finished** `1339c7cf` (sumcheck-3 62f24d42: layout.py / sumcheck.py / tests = theirs; no hunk of ours kept:
  theirs already carries relation's fp4 `y_end` patch). Predecessor's LGSC0004 emission committed as found `e61b24fe`
  (`--zk`: `layout_for(zk=True)` + `fill_zk` per proof, ZK key per (relation, C), `RowMaskLayout(..., sumchecks=())` so the
  PCS places no Libra masks of its own on LGSC0004's g cells = **R3-5**; 2 eval + 3 sparse mask claims via `pcs.open(sparse=)`).
* 00:01Z `7135d5d5` **R3-6** (`Prover.sumcheck_schedule`: LGSC0004 schedule refused unless vf <= n_c - 4, passed to every
  `sumcheck.prove`; Python verdict `zk_mode` lgsc0004 / lgsc0004-underblinded), **R3-2** (framing `t_pad` present iff > 0 and
  iff `params.zk`; params = the writer's bytes, known keys, writer's JSON types: `16.0` for 16 rejected), **R3-8** (verify pins
  `stmt.word_bytes` / `y_bytes` to the relation's, stage "statement shape"; widths outside {1,2,4} ValueError). `ad9377ae`: gate
  negatives for both (framing re-encoded as raw bytes; statement words at twice the width). Laptop tests pass.
* 00:07-00:10Z **10 gates @ad9377ae on the 4090** (5 relations x {non-ZK, --zk}, in parallel): **0 failures each**; non-ZK 4 + 98,
  ZK 4 + 100 (the two ZK V1 must-rejects). Rust (verify-rs-3 tree built as /workspace/vrs4): non-ZK pinned pass; ZK dumps
  refused by the pinned verifier ("not a pinned system and key": verify-rs-4 pins ZK keys by derivation, not yet in that
  build); `--allow-any-key` accepts all 5 ZK dumps (positives accepted, all negatives rejected).
* 00:12Z `8c75fc4c` **R3-7**: `verify-session` derives every coin slot from the issuing verifier's record alone
  (`run.record_slots(stream_stmt, rec, rounds)`: no dump argument; ctx = `batch_context(STMT, coin_commit(r_k, s_k) of the
  record's coins)`, slot k = `expand_challenge(ctx, k, rec.rounds[k].label, r_k, 32)`, exactly `verdict.rounds` coins and rounds
  k = 0..R-1, `rec.stmt_sha256` = sha256 of the STMT rebuilt from the statement / params / key being verified). The record
  batch is found by the proof's own STMT digest (the dump's opening is only a sort hint); the proof must verify under those
  slots, consume all of them, and match every round's `msg_sha256` and label; one proof per record batch. **R3-10**: claim =
  interactive union x (batches the verifier opened for that STMT across `--sessions-root`, aborted / refused included); no
  claim without `--sessions-root`, or while any session there has no record (open / crashed); job = union over distinct
  statements. Laptop `live_session_test.py`: the red team's A (label grinding) / B (extra commitment) / C (random slot) slots
  all differ from the replay's at the attacked positions; record-shape negatives; 5 pass.
* 00:14Z merged `lane/ligerito-sumcheck-3 @ 796d8a11` (ligerito-sumcheck-4: 12-coin default 850f812c; zk_masks refuse
  vf > n_c - 4; `check_zk_claim_supports` on the prover's claims) = `6910bf9e`, no conflicts. `7cbd8eb0`: R3-6 via
  `sumcheck.zk_vf_max` / `zk_mode`; `manifest.key_sha256` + batch key digest in logs (verify-rs-4 ask 2).
* 00:20Z **ZK keys = verify-rs-4's derivation, all 15 (relation x {gate C, 4096 VUs, 16384 VUs})**: `zk_keys.py` on the pod,
  sha256(key.bin) = `Key.digest()` = their table byte for byte (gate C: fp8-ada 8c4cd91f…, bf16-hopper 8b36e2cd…, fp8-hopper
  80a95d1f…, bf16-ampere fd5c7a08…, fp4-nvf4 16431681…; l = 16384 any C: 875f45c5…, c3e51878…, 8e9c7f53…, 8d5ed6ee…, 18b38023…).
* 00:18Z **R3-7 end to end on the GPU** (`live_session_gpu_test.py`, loopback `live.Server`, fp8-ada, non-ZK and --zk): honest
  authenticated (2^-128.017 / 2^-128.030); A and B: the verifier ACCEPTED both sessions and the cold `verify-dir` accepts both
  dumps, **`verify-session` rejects both** ("proof rejected under the verifier's coins: zero-check round 1/0"); D (one batch,
  two proofs) second rejected. E first run exposed that a dropped session with no record yet blocks the claim (correct,
  conservative; test fixed to also shut the socket down and check the count).
* 00:24Z `e1114b4c` (live_session_gpu_test / zk_keys resolve l as run.py), `2b0f87a6` (E: an open dropped session blocks
  every claim; the drop is a shutdown, then wait for verdict.json). 10 gates @e1114b4c 0 failures (art `6efa1502`, dumps
  `7a11540a daa3e099 11dff26a 848e02cc edbb086c 21d950a2`); R3-7 GPU test 6/6 both modes (art `12022524`); ZK keys art `18f008f6`.
* 00:26Z **4096-VU `--zk` OOMed on the 4090** at 2b0f87a6 (LGSC0004 fold wants 9 GiB with z + f + Merkle tree resident; art
  `b3fc907c` has the non-ZK runs and the OOM logs). `6dda159a`: under `--zk`, when the round-1 codeword streams (`com.U1 is
  None`), `del f` after commit, `com.M1 = None` through the zero-check, rebuild `com.M1 = z_to_f(z)` for the opening, then drop
  z (`LIGERITO_ZK_REBUILD_F=1` forces this path at gate sizes: fp8-ada gate 4 + 100, 0 failures, art `3b95dfcc`). Benches run
  with `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` (without it rep 2+ fragmented into an OOM).
* 00:30Z **measurements** @6dda159a, art `80b4e073` (table below). Live ZK against the kept RO verifier (not restarted: the
  challenge-stream wire is unchanged from its `live-verifier@80547525ac60`): session c20260924T003234Z-a1a0 ACCEPTED,
  verify-session authenticated, but 3 reps = 3 batches on one STMT so R3-10 gives 2^-128.007 + log2 3 = **2^-126.42** (and
  non-ZK c20260924T003303Z-f283: 6 batches on its STMT incl. relation-2's 23:11Z sessions -> 2^-125.42).
* 00:37Z `7f35c223` (R3-10 on the prover side): bench against a live verifier sizes each proof for
  2^-(128 + ceil log2(reps x batches)). Rerun: live ZK session **c20260924T003626Z-5aa5 ACCEPTED**, 3 x 42 rounds, per proof
  2^-130.02, verify-session (`--sessions-root` = the verifier's whole store, copied from pitmqu0zrycw5i) **authenticated,
  claimed 2^-128.43 (live)**. Art `ef6b9392` (both live runs + the verifier store).
* 00:38Z `498f9014`: the cold `verify-dir` of a live dump (claims nothing) now also refuses the red team's bindings: one
  commitment / opening / label per slot and a whole coins file (B), replay labels = the binding's (A), the proof consumes
  exactly the file's coins. Final runs @498f9014: **10 gates 0 failures** (ZK with `LIGERITO_ZK_REBUILD_F=1`), R3-7 GPU test
  **6/6 non-ZK and --zk**, cold verify-dir rejects A ("stream binding labels are not the protocol's") and B ("29 commitments /
  28 openings / 28 labels for 28 slots").
* 00:42Z the red team's own `redteam_live_labels.py 498f9014` still prints "1 attack(s) accepted": it execs `_file_coins` in
  isolation, and A's binding is self-consistent at that level. `_file_coins` no longer feeds `verify-session` (which never
  reads the dump's binding) and `verify-dir` rejects A at replay; the script needs retargeting at `record_slots` /
  `verify-session`, which `live_session_test.py` (laptop) and `live_session_gpu_test.py` (GPU) do with its constructions.
* 00:46Z **verify-rs-4 @0e4ef1d1, pinned only (no `--allow-any-key`)**, built on the pod: 498f9014 gates 10/10 accepted
  (20/20 honest); real-size 4096-VU dumps 6/6 (ZK key 875f45c5 = its derivation); live `--session` 3/3 authenticated with
  the same claims as Python (2^-128.435 / 2^-126.422 / 2^-125.416). Its `load_sessions` panics on the verifier's whole store
  (45 `s…` sessions of the other live protocol have `subbatches`, no `batches`); run over the 5 `c…` records. Handoff:
  `verify-rs-4/20260924T0050Z-handoff-from-ligerito-relation-3.md`. Art `f7049d60` (gates, R3-7, Rust JSONs, records).
* 00:59Z all 14 cited arts remote = 1 (`research data sql`); branch pushed to origin; pod 52tgms6kjphi6k terminated 01:00Z.

## Measurement: fp8-ada, 4096 VUs, 1 batch (N = 2^30, l 16384), RTX 4090, relation 6dda159a (art 80b4e073)

Medians (local 5 reps, others 3). Every row's F12 class is **NON_ZK_PROOF_DIAGNOSTIC**: under `--zk` the sumcheck is LGSC0004
(masked, zk_mode lgsc0004) but the backend is not complete ZK (missing: a PCS ZK argument covering the V1 zero claims and
LGSC0004's sparse g-row claims, red-team-ligerito-3 checklist item 5). Rust = verify-rs-3 build at the time (ZK via
`--allow-any-key`); pinned verify-rs-4 0e4ef1d1 later accepted all six dumps (art f7049d60).

| coins (F12) | mode | t.total s | zero-check s | proof bytes | sumcheck bytes | coin rounds | peak GiB | Python verify s | Rust verify s | claim |
|---|---|---|---|---|---|---|---|---|---|---|
| local (diagnostic) | non-ZK LGSC0003 | 0.594 | 0.168 | 701,728 | 11,069 | 48 | 16.00 | 1.59 | 0.43 | none (prover knows coins) |
| local (diagnostic) | ZK LGSC0004 | 0.823 | 0.244 | 916,527 | 186,647 | 42 | 15.69 | 1.40 | 0.47 | none |
| FS | non-ZK | 0.581 | 0.167 | 705,062 | 11,069 | 48 | 16.00 | 1.40 | 0.46 | 2^-65.08 (Q = 2^64) |
| FS | ZK | 0.846 | 0.224 | 914,037 | 186,647 | 42 | 15.69 | 1.44 | 0.49 | 2^-65.07 |
| live-local (no network) | non-ZK | 0.594 | 0.165 | 702,175 | 11,069 | 48 | 16.00 | 1.39 | 0.65 | none (unauthenticated) |
| live-local (no network) | ZK | 0.836 | 0.229 | 915,374 | 186,647 | 42 | 15.69 | 1.66 | 0.47 | none |
| **live, RO verifier** (7f35c223) | ZK | 3.365 | 0.884 | 925,166 | 186,647 | 42 | 15.69 | 1.41 | 0.45 | **2^-128.43** after verify-session |

ZK costs +0.23-0.27 s (+39-46 %) of prover time, mostly arithmetic (0.235 -> 0.467 s: the masked rounds) and zero-check;
+214 KB proof (the LGSC0004 sumcheck is 187 KB vs 11 KB); 42 vs 48 coin rounds per batch; peak slightly lower
than non-ZK only because of 6dda159a's drop/rebuild of the z_to_f copy. The live row's t.total is dominated by the network
stream (54 ms RTT x 42 rounds; stream wait 2.53 s).

## FINAL (01:00Z)

* **Branch tip `lane/ligerito-relation-2` @ `498f9014`** (pushed to origin; took over the predecessor's worktree/branch as
  instructed). Commits: 1339c7cf merge sumcheck-3 62f24d42 (layout.py / sumcheck.py = theirs, no hunk kept), e61b24fe
  predecessor's LGSC0004 emission, 7135d5d5 R3-6/R3-2/R3-8, ad9377ae gate negatives, 8c75fc4c R3-7/R3-10, 6910bf9e merge
  sumcheck-3 796d8a11 (12 coins), 7cbd8eb0, e1114b4c, 2b0f87a6, 6dda159a (ZK memory), 7f35c223 (R3-10 sizing), 498f9014.
* **ZK: `--zk` emits LGSC0004** (not LGSC0003 + per-variable masks): layout_for(zk=True), fill_zk per proof, ZK key per
  (relation, C), no PCS Libra masks on g cells (R3-5), vf <= n_c - 4 enforced (R3-6, via sumcheck.zk_vf_max). **Key pinned:
  yes**, by verify-rs-4's derivation: gate keys 8c4cd91f / 8b36e2cd / 80a95d1f / fd5c7a08 / 16431681, l 16384 keys (875f45c5
  fp8-ada …) all 15 match (art 18f008f6); pinned verify-rs-4 accepts every ZK dump incl. the real-size ones. Honest class
  stays NON_ZK_PROOF_DIAGNOSTIC (PCS ZK argument for the V1 zero claims + sparse g-row claims missing).
* **R3-7: closed** for `verify-session`: slots derived only from the verifier's record (`record_slots`), exact length,
  per-round message/label match, one proof per record batch; the red team's A/B/C constructions rejected (laptop test + GPU
  end to end, both modes). Cold `verify-dir` also rejects A/B now. Their script still says "1 accepted" because it exercises
  `_file_coins` alone (see 00:42Z). **R3-10** too (attempts over `--sessions-root`; no claim without the whole store or
  with an open session; bench sizes per-proof targets for reps x batches).
* **R3-2 and R3-8: closed** (Python reader as strict as Rust: `t_pad` present iff > 0 and iff params.zk, params canonical +
  typed + known keys; statement word widths pinned to the relation's, widths outside {1,2,4} rejected; gate negatives for
  both; laptop tests).
* **Gates @498f9014: 10/10, 0 failures** (5 relations x {non-ZK 4 + 98, --zk 4 + 100}); Rust verify-rs-4 pinned 10/10.
* **Live ZK session: ACCEPTED** by the kept RO verifier `tcp://213.173.105.92:56412` (not restarted), session
  c20260924T003626Z-5aa5, 3 x 42 rounds; verify-session authenticated, **claimed 2^-128.43 (live)**; Rust `--session` agrees.
* **Arts (all remote = 1):** gates art:6efa1502 (e1114b4c), art:f7049d60 (498f9014 + Rust + R3-7 final); fixtures
  art:7a11540a art:daa3e099 art:11dff26a art:848e02cc art:edbb086c art:21d950a2 art:3b95dfcc; ZK keys art:18f008f6; R3-7 GPU
  art:12022524; bench art:80b4e073 (4096 VUs), art:b3fc907c (pre-fix non-ZK + OOM), art:ef6b9392 (live RO + verifier store).
* **Pod** vy-ligerito-relation-2-veritor-campaign (52tgms6kjphi6k, RTX 4090, $0.74/h) **terminated 01:00Z**; lifetime
  21:43Z-01:00Z = ~$2.44 total, this lane's share (23:50Z-01:00Z) ~$0.86.
* **Handoffs (all read; answers):**
  - `20260923T2358Z-handoff-from-ligerito-sumcheck-4.md` (12-coin default 850f812c, R3-6 `allow_underblinded` / `zk_mode`,
    R3-4 `check_zk_claim_supports`, R3-5 "don't touch g cells [0, 6 zk_coeffs)"): merged as 796d8a11 (6910bf9e); R3-6 via
    `zk_vf_max` / `zk_mode` (7cbd8eb0); R3-5 holds (`sumchecks=()`: the PCS writes nothing in the g block).
  - `20260924T0025Z-handoff-from-ligerito-sumcheck-4.md` (11-coin default, `lane/ligerito-sumcheck-3` @ 58e76e5d): **not
    merged**. It arrived after my measurements; my pod was gone before I read it, and merging without a GPU gate rerun would
    leave an untested tip. Its merge-tree with 6dda159a is clean per sumcheck-4. All my numbers are 12 coins (186,647 B
    sumcheck); sumcheck-4 reports 11 coins = 418,846 B, about 10 ms more prover time, one fewer round trip.
  - `20260923T2358Z-asks-from-verify-rs-4.md` (ZK gate dump per relation with key.bin = ZK key; manifest key digest; derived
    pinning; batch its dumps): all done (7cbd8eb0 manifest `key_sha256`; gates e1114b4c and 498f9014 dumps; keys = its derivation).
  - `20260924T0058Z-handoff-coordinator.md` (verify-rs-5 builds on my pod): read at 01:01Z, **after** I terminated the pod at
    01:00Z (per my launch brief). verify-rs-5 hit a 404; answered in `verify-rs-5/20260924T0105Z-handoff-from-ligerito-relation-3.md`
    (store + dumps on R2 art ef6b9392 and the laptop; expected claims) and `coordinator/20260924T0105Z-handoff-from-ligerito-relation-3.md`.
  - `ligerito-relation-2/20260923T2230Z-handoff-coordinator.md` (orphan pod lkdd6gndttgewf): no longer running (pods list 01:03Z).
  - `ligerito-relation-2/20260923T2228Z-handoff-coordinator-live.md` (live-2c; RO verifier 1x8f33k0qa2lkx): superseded; the
    kept verifier I used is pitmqu0zrycw5i (`tcp://213.173.105.92:56412`), not restarted.
  - Predecessor's inbox (read at 23:50Z): `20260923T2230Z-handoff-from-live-2c.md` (use RO `tcp://213.173.105.92:56412`): used.
    `20260923T2245Z-handoff-from-ligerito-sumcheck-3.md` (LGSC0004 ready) and `20260923T2300Z-handoff-from-ligerito-sumcheck-3.md`
    (13 coins; LGSC0003 lean): merged 62f24d42 (1339c7cf), then 796d8a11 (12 coins). `20260923T2253Z-handoff-from-red-team-ligerito-3.md`
    (V1 review + LGSC0004 adoption checklist): followed (R3-5 / R3-6 / two ZK V1 must-rejects); checklist item 5 (PCS ZK for the
    sparse / zero claims) is the open item that keeps the class NON_ZK. `20260923T2308Z-handoff-from-red-team-ligerito-3.md`
    (R3-7 BLOCKING): closed (8c75fc4c, 498f9014). `20260923T2155Z-asks-from-verify-rs-3.md` (V1 zero-claim layout + fixtures):
    delivered by ligerito-relation-2 (32e9bd59 gates); its ZK follow-up came through verify-rs-4 (above).
  - Grand-predecessor `ligerito-relation` inbox, handled by ligerito-relation-2 before me (its report, by content not by filename):
    `20260923T1850Z-handoff-red-team-ligerito.md` (|S| vs column padding; don't combine the bivariate round with
    zk.SumcheckMask; job accounting): the old per-variable masks are gone under `--zk` (LGSC0004, `sumchecks=()`); ZK unions are
    computed on the ZK layout (2^-128.007 at 4096 VUs, Rust recomputes the same); a job's claim is the union over its statements
    x recorded attempts. `20260923T1905Z-handoff-red-team-ligerito.md` (F12 soundness labels, verify-dir coin provenance):
    F12 labels / `COIN_PROVENANCE` in run.py (relation-2), kept. `20260923T2045Z-handoff-from-ligerito-sumcheck-2.md`:
    superseded by sumcheck-3/-4. `20260923T2115Z-handoff-from-verify-rs-2.md` and `20260923T2110Z-handoff-from-red-team-ligerito-2-V1.md`
    (V1: virtual rows unconstrained; use r_c columns): fixed by ligerito-relation-2 (V1 fix, reviewed by red-team-ligerito-3).
* **Left:** (1) the PCS ZK argument for the V1 zero claims / LGSC0004 sparse claims (complete ZK); (2) verify-rs-4's
  `load_sessions` should accept `subbatches`-only records so Rust can take the verifier's whole store; (3) red team to
  retarget `redteam_live_labels.py` at `verify-session`; (4) the FS row's claim (2^-65 at Q = 2^64) is the FS bound, not 2^-128.
