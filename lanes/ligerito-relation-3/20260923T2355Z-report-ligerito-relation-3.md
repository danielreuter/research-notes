---
lane: ligerito-relation-3
kind: report
created: 2026-09-23T23:55Z
status: open
branch: lane/ligerito-relation-2 (worktree ~/projects/verity-main-wt/ligerito-relation-2; taken over per the coordinator's launch message, predecessor stopped ~23:24Z mid-merge)
owns: backends/direct/ligerito/{prove.py, proof.py, run.py} (+ tests beside them)
pods: vy-ligerito-relation-2-veritor-campaign (RTX 4090, reused; predecessor tree /workspace/lr2)
---

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
