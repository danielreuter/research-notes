---
lane: verify-rs-4
kind: report
created: 2026-09-23T23:55Z
status: final
branch: lane/verify-rs-3 (worktree ~/projects/verity-main-wt/verify-rs-3, taken over from verify-rs-3 @ 732e5d5f + uncommitted)
---

CHECKPOINT 0e4ef1d1 (00:32Z) [final] FINAL 0e4ef1d1 (pushed): ZK keys pinned by derivation (all 5 relations + real-size fp8-ada match); LGSC0004 end to end; R3-7/R3-10 Rust session check (slots from the verifier record only, one batch per proof, claims over complete stores); relation-3 e1114b4c 10/10 dumps: 20/20 honest, 990/990 negatives rejected, 1010/1010 agree. cargo 98 + 1 ignored. Remaining: real-size LGSC0004 proof (relation-3 bench OOM).
CHECKPOINT none (00:31Z) [open] 0e4ef1d1 (pushed): --session claims only over a complete verifier store (relation-3 E rule). Real-size 2b0f87a6 benches fs/local/live-local 1/1 each accepted; real-size --zk bench OOM'd on the 4090 (no proof), its key = my derived 875f45c5. All 4 deliverables done; waiting for a real-size LGSC0004 proof; FINAL by 03:00Z.
CHECKPOINT none (00:28Z) [open] 4d66a40d: deliverable 4 done on relation-3 gates-e1114b4c: 10/10 dumps (5 relations x plain/--zk) batch-accepted, 20/20 honest, 990/990 negatives rejected, 1010/1010 agree with Python, all 5 ZK keys pinned by derivation; live --session over relation-3 r37 (real loopback records) = Python verdicts (A/B rejected, D 1/2); one-batch-one-proof adopted. cargo 98 pass + 1 ignored.
CHECKPOINT none (00:15Z) [open] 908a04b7: LGSC0004 end to end on relation-2 e61b24fe --zk gate: ZK key 8c4cd91f pinned by derivation (da27387b), 2/2 honest + 96/96 negatives rejected, 98/98 agree with Python; 54b4a8d3: R3-7 Rust session check (slots from the verifier record only; --session) + R3-10 attempts factor; real live-ro dumps 3/3 authenticated, 4096 bench claim 2^-126.42 (3 batches on one statement). Python verify-session does NOT derive slots from the record (R3-7 gap). cargo 96+1 ignored. Next: tell relation-3; batch its fresh 10 gates when they land.
CHECKPOINT none (00:07Z) [open] 00:07Z: derived ZK-key pinning + soundness J fix committed earlier; asks note written to relation-3. Now R3-7 in Rust: new src/session.rs (live slots derived ONLY from the verifier's session.json: STMT = lgto-stmt|v1| sha256(params) sha256(stmt) sha256(key); commitments = coin_commit of recorded coins; slot k = expand_challenge(batch_context, k, recorded label, r_k); exact length; per-round MSG/label vs record; claim = union + log2(recorded batches on the statement) for R3-10). Builds; next: fixture from a real ChallengeServerSession + verify-session CLI.
CHECKPOINT 80d5d746 (00:00Z) [open] 80d5d746: LGSC0004 keys pinned by DERIVATION from the pinned LGSC0003 key (zk_key_of = layout_for(zk=True)+constraints, byte-equal to Python's ZK layout/constraints on sumcheck-3 62f24d4 toy fixtures); LGSC0004 soundness J = 5 + |zb| as relation-3 e61b24fe; asks written to ligerito-relation-3 (23:58Z). cargo 89/89. Next: derived digests for all 5 relations, R3-7 scope, relation-3 --zk dumps
CHECKPOINT 1aea9b3e (23:52Z) [open] 1aea9b3e: took over verify-rs-3 worktree/branch (lane/verify-rs-3); in-progress must-reject canon_y_offend (relation-2 32e9bd5 neg 45) committed, rejected at statement stage; cargo 87/87 + 1 ignored. Next: LGSC0004 vs sumcheck-3 62f24d42, relation-3 asks, R3-7
# verify-rs-4: finish verify-rs-3's Ligerito Rust verifier (canon negative, LGSC0004 / ZK key, R3-7, relation-3 batch)

## Log

* 23:51Z start. Read relaunch brief §0/§3, verify-rs-3 report + handoffs, red-team-ligerito-3 FINAL. Took over worktree
  `verify-rs-3` (branch `lane/verify-rs-3` @ 732e5d5f; origin at the same tip, so no second writer) with its uncommitted
  `src/lgto.rs` (+10, test `python_proof_for_a_non_canonical_statement_rejected`) and fixture
  `fixtures/lgto/fp8ada_l256_v1/canon_y_offend.{lgto.neg,stmt}`. Disk 11 GB free. `lanes/ligerito-relation-3/` does not exist yet.
* 23:52Z 1aea9b3e: the in-progress must-reject `canon_y_offend` (relation-2 32e9bd5 neg 45: y[0] = 1 off a chain end, proved
  for that statement) committed; rejected at the statement stage ("claimed word off a chain end (non-canonical)"); the v1
  batch test counts 6 negatives.
* 00:00Z 80d5d746: LGSC0004 keys are pinned by DERIVATION, not by digest. `lgto::zk_key_of(key3, n_s, n_j)` =
  `layout_for(zk=True)` + `constraints()` from an LGSC0003 key; `lgsc3_key_of` inverts it. A ZK key is pinned iff its inverse's
  digest is a pinned LGSC0003 key AND the forward derivation reproduces the file byte for byte (`key_derived_from` in the
  report). Cross-checked byte-for-byte against Python's ZK layout/constraints on sumcheck-3 62f24d4's LGSC0004 toy fixtures.
  LGSC0004 soundness J = 5 + |zero_blocks| (relation-3 e61b24fe). `zk-key --key K --l L --s S` prints/writes derived keys.
* 00:05Z asks note `lanes/ligerito-relation-3/20260923T2358Z-asks-from-verify-rs-4.md` (+ derived digests for all 5
  relations at the gate and real sizes).
* 00:10Z 54b4a8d3 **R3-7 / R3-10 on the Rust side** (`src/session.rs`; `verify` / `batch --session PATH`, repeatable: a
  `ChallengeServerSession` record dir or a dir of them). Live slots are derived from the verifier's RECORD only: the batch is
  selected by `stmt_sha256` = sha256(STMT), STMT = `lgto-stmt|v1| sha256(params) sha256(stmt file) sha256(key)` computed
  here; commitments = `coin_commit(r_k, s_k)` of every recorded coin; slot k = `expand_challenge(batch_context(STMT, commitments),
  k, recorded label k, r_k)`; exact length (recorded rounds == committed coins == the proof's coin rounds); every round's
  sha256(MSG k) and label must equal the proof's own absorbs (`SessionReplayCoins` framing); session accepted. The dump's
  `.coins` / `stream_binding` are never read. Claim = interactive union + log2(A), A = recorded batches on the statement
  (abort-and-retry, R3-10); pre-V1 proofs still claim nothing; unauthenticated live proofs are rejected under `--session`.
  - **Python's `run.py verify-session` does not close R3-7**: it verifies with the dump's `.coins` slots and only checks that
    the dump's openings equal the record's; it never derives the slots from them. A prover that ignored the verifier's coins
    (sent its MSGs, then used slots of its choosing) passes it. The Rust path above does not have this gap.
  - Real dumps with real verifier records (relation-2 32e9bd59 bench `live-ro`, sessions c8a8 / da81, pulled read-only to
    /tmp/lr2-art): 4096-VU 1/1 and 2x2048 2/2 authenticated. **R3-10 is live in that bench:** session c8a8 recorded 3 batches
    on the one statement (timing reps), so the prover saw 3 coin sets and published one: Rust claims 2^-126.42, Python's
    verify-session 2^-128.00. 2x2048: 2 batches per statement, 2^-127.02 per proof.
  - Tests (tests/session.rs, 5): hermetic on ligerito-relation's l=256 StreamCoins fixture (record-derived slots verify the
    Python-written proof; Rust STMT and coin commitments = Python's); MSG (rounds 0/17/63), label, coin r, coin s, one round
    short / one extra, coins != rounds, verdict not accepted, other statement: all rejected; prover-chosen slots accepted by
    file replay but rejected by the record; record JSON reader; env-gated real-dump test (`LIGERITO_LIVE_DUMPS`) passes on both.
* 00:14Z 908a04b7 **LGSC0004 end to end.** relation-2 e61b24fe's `--zk` gate (pod dump `/workspace/lr2/gates-lgsc4/dump_fp8-ada-zk`,
  23:37Z; pulled read-only to /tmp/vrs4zk): key 8c4cd91f45f2... = the digest derived at 00:05Z, pinned by derivation from
  da27387b (no `--allow-any-key`). `batch --dir` at the default 2^-128 target: 2/2 honest (fiat-shamir + local) accepted,
  sumcheck LGSC0004, zk_mode lgsc0004, union 2^-128.03; **96/96 negatives rejected**, all at the stage Python names (committed
  next:0 / committed M_next -> "combined round 0"); 98/98 manifest verdicts agree. Subset committed as fixture
  `fixtures/lgto/fp8ada_l256_zk_lgsc4` (2.4 MB) + CLI test. cargo 96 pass + 1 ignored.
* 00:19Z baseline batch (deliverable 4, pre-relation-3): relation-2 32e9bd59's gate set (pod `/workspace/lr2/gates-32e9bd59`,
  pulled read-only to /tmp/vrs4g32), `batch --dir` at the default 2^-128 target, pinned keys only:

  ~~~text
  dump              honest (fs+local)  negatives rejected  manifest agree  sumcheck / zk_mode      union
  fp8-ada           2/2                94/94               96/96           LGSC0003 / none         2^-128.017
  fp8-ada --zk      2/2                94/94               96/96           LGSC0003 / partial      2^-128.030
  bf16-hopper       2/2                94/94               96/96           LGSC0003 / none         2^-128.017
  fp8-hopper        2/2                94/94               96/96           LGSC0003 / none         2^-128.017
  bf16-ampere       2/2                94/94               96/96           LGSC0003 / none         2^-128.017
  fp4-nvf4          2/2                94/94               96/96           LGSC0003 / none         2^-128.025
  fp8-ada --zk e61b24fe (LGSC0004)  2/2  96/96             98/98           LGSC0004 / lgsc0004     2^-128.030
  live-ro 4096 (--session)          1/1  -                 -               LGSC0003 / none         claim 2^-126.42
  live-ro 2x2048 (--session)        2/2  -                 -               LGSC0003 / none         claim 2^-127.02
  ~~~
* 00:26Z 4d66a40d: one recorded verifier batch authenticates one proof (`session::authenticate_unused`; `batch --session`
  re-authenticates in file order a proof whose batch another proof took) = relation-3 2b0f87a6's rule (its D case); report
  field `live_session`. Fixture `fixtures/session/fp8ada_l256_zk_live` (1.3 MB) from relation-3's loopback-verifier test:
  real records, LGSC0004 live: honest authenticated (claim union + log2 4: 3 accepted + 1 aborted session on the statement),
  R3-7 A label grinding / B context grinding valid under their own `.coins`, rejected under every recorded batch; CLI test.
  cargo 98 pass + 1 ignored.
* 00:28Z **deliverable 4: relation-3's fresh gates (e1114b4c, pod `/workspace/lr3/gates-e1114b4c`, pulled read-only to
  /tmp/vrs4e11), `batch --dir` at the default 2^-128 target, pinned keys only (no `--allow-any-key`), Rust @ 4d66a40d:**

  ~~~text
  relation      mode    honest (fs+local)  negatives rejected  manifest agree  sumcheck / zk_mode   key (derived from)        union
  fp8-ada       plain   2/2                98/98               100/100         LGSC0003 / none      da27387b                  2^-128.017
  fp8-ada       --zk    2/2                100/100             102/102         LGSC0004 / lgsc0004  8c4cd91f (da27387b)       2^-128.030
  bf16-hopper   plain   2/2                98/98               100/100         LGSC0003 / none      1726c3be                  2^-128.017
  bf16-hopper   --zk    2/2                100/100             102/102         LGSC0004 / lgsc0004  8b36e2cd (1726c3be)       2^-128.032
  fp8-hopper    plain   2/2                98/98               100/100         LGSC0003 / none      ea793f49                  2^-128.017
  fp8-hopper    --zk    2/2                100/100             102/102         LGSC0004 / lgsc0004  80a95d1f (ea793f49)       2^-128.030
  bf16-ampere   plain   2/2                98/98               100/100         LGSC0003 / none      e0059e70                  2^-128.017
  bf16-ampere   --zk    2/2                100/100             102/102         LGSC0004 / lgsc0004  fd5c7a08 (e0059e70)       2^-128.032
  fp4-nvf4      plain   2/2                98/98               100/100         LGSC0003 / none      ac61d99e                  2^-128.025
  fp4-nvf4      --zk    2/2                100/100             102/102         LGSC0004 / lgsc0004  16431681 (ac61d99e)       2^-128.062
  total                 20/20              990/990             1010/1010
  ~~~

  Live (`--session`, relation-3 2b0f87a6 r37, real loopback records): fp8-ada plain + --zk: honest authenticated (claims
  2^-126.02 / 2^-126.03 with the store's 4 batches on the statement), A label grinding + B context grinding rejected, D
  (copy of the honest proof) 1 of 2 authenticated; = Python's verify-session verdicts. Relation-3's own `rust batch` lines
  on these ZK dumps said "not a pinned system and key": its pod build `/workspace/vrs4` predates 80d5d746 (no `zk_key_of`).
* 00:31Z relation-3's real-size benches (2b0f87a6, pod `/workspace/lr3/meas-2b0f87a6`, fp8-ada 4096 VUs, pulled read-only
  to /tmp/vrs4meas): fiat-shamir 1/1, local 1/1, live-replay (live-local) 1/1 accepted, pinned, union 2^-128.001. The
  three `--zk` benches died on the 4090 (CUDA OOM, 9 GiB table in LGSC0004 `fold`), no proof; their key.bin is 875f45c5 =
  my derived l = 16384 ZK key. So no real-size LGSC0004 proof exists yet to verify.
* 00:34Z 0e4ef1d1: `--session` claims only over a whole verifier store whose every session has its record (relation-3's
  E cases): a single record dir, or a store with an open session (hello.json only), authenticates but claims nothing.
  CLI test. 32e9bd59 live-ro claims unchanged (their `verifier_session/` is a complete store). Pushed origin
  lane/verify-rs-3 @ 0e4ef1d1.

## FINAL (00:36Z)

**Branch tip:** `lane/verify-rs-3` @ 0e4ef1d1 (pushed to origin; worktree ~/projects/verity-main-wt/verify-rs-3). Commits
this lane: 1aea9b3e, 80d5d746, 54b4a8d3, 908a04b7, 4d66a40d, 0e4ef1d1. No pod of my own; relation-3's dumps pulled read-only.
**Tests:** `cargo test --release` 98 pass + 1 ignored (83 lib + 9 cli + 6 session); `LIGERITO_LIVE_DUMPS` env test passes
on relation-2 32e9bd59's two live-ro dumps.

**Deliverables**
1. `canon_y_offend` must-reject committed (1aea9b3e); rejected at the statement stage.
2. **ZK key pinned: yes, by derivation** (80d5d746): an LGSC0004 key is pinned iff it is `zk_key_of(pinned LGSC0003
   key, S, l)` byte for byte. All five relations' gate ZK keys from relation-3 e1114b4c and the real-size fp8-ada ZK key
   (875f45c5) equal the derived digests. LGSC0004 verifies end to end: e61b24fe gate 2/2 + 96/96; e1114b4c gates below;
   fixture `fp8ada_l256_zk_lgsc4` + CLI test.
3. **R3-7 on the Rust side: done** (`src/session.rs`, `--session`). Slots come only from the verifier's record (STMT digest,
   coin commitments, recorded labels, exact length); every round's MSG and label must match the record; one recorded batch
   per proof; claim = union + log2(recorded batches on the statement), and only over a complete store (R3-10). The dump's
   `.coins` is never read. Relation-3's Python verify-session now has the same rules (2b0f87a6); Rust gives the same
   verdicts on its A/B/D/E cases.
4. **Batch (relation-3 e1114b4c, every relation, plain and --zk):** 10/10 dumps accepted, 20/20 honest accepted, 990/990
   negatives rejected, 1010/1010 manifest verdicts agree, pinned keys only, 2^-128 target (table at 00:28Z). Also: the
   32e9bd59 gate set 12/12 + 564/564 + 576/576; real-size 2b0f87a6 benches fs/local/live 3/3; live `--session` 3/3 on
   32e9bd59 live-ro and relation-3's r37 honest (plain + zk); r37 attacks A/B rejected, D 1 of 2.

**What verifies, per relation and mode (Rust @ 0e4ef1d1)**

~~~text
relation      plain (LGSC0003)                  --zk (LGSC0004)                      live (--session, real records)
fp8-ada       gate 2+98/98; real-size fs/local/live 3/3   gate 2+100/100 (and e61b24fe 2+96/96)   plain + zk honest; A/B/D rejected
bf16-hopper   gate 2+98/98                      gate 2+100/100                       -
fp8-hopper    gate 2+98/98                      gate 2+100/100                       -
bf16-ampere   gate 2+98/98                      gate 2+100/100                       -
fp4-nvf4      gate 2+98/98                      gate 2+100/100                       -
~~~

**Findings for others**
* R3-10 is live in relation-2 32e9bd59's `live-ro` bench: 3 verifier batches on one statement (timing reps), so the claim
  is 2^-126.42, not 2^-128.00. Size proofs for 2^-(128 + log2 A), or give each rep its own statement and record.
* relation-3's pod `rust batch` lines on ZK dumps said "unpinned": its `/workspace/vrs4` build predates 80d5d746.

**Remaining**
* No real-size LGSC0004 proof exists yet (relation-3's 4096-VU `--zk` bench OOMs on the 4090); its key already pins, so
  run `batch --dir` on one when it lands.
* Live `--session` has been exercised on fp8-ada only (the only relation with live verifier records so far).
* The hermetic l=256 StreamCoins session fixture is pre-V1 (needs `allow_legacy`); the real-record ZK fixture covers the
  current format.
* Local evidence: Rust batch JSONs in `evidence/` (gates-e1114b4c, gates-32e9bd59, gates-lgsc4-e61b24fe, meas-2b0f87a6,
  r37-2b0f87a6); the dumps themselves are relation-3's (pod /workspace/lr3, /workspace/lr2) to push as art.
