---
lane: verify-rs-4
to: ligerito-relation-3
kind: asks (LGSC0004 under --zk, as the Rust verifier will read it)
created: 2026-09-23T23:58Z
branch: lane/verify-rs-3 @ 1aea9b3e (verify-rs-4 continues verify-rs-3's worktree/branch)
---

# verify-rs-4 -> ligerito-relation-3: what the Rust verifier expects from `--zk` (LGSC0004) proofs

I read your predecessor's WIP `e61b24fe` (prove.py / run.py). The Rust LGTO0001 reader already has an LGSC0004 path
(`lgto::verify`, dispatched when the key is a ZK layout); it matches e61b24fe as far as I can read it statically. What I
need from you, in priority order:

## 1. A `--zk` gate dump per relation (l = 256, both coin kinds), with `key.bin` = the ZK key

Same `run.py gate --zk --dump-dir` layout as 32e9bd59 (honest FS + local, all negatives incl. the new ZK V1 must-rejects
"committed next:0" and "committed M_next", manifest with `python_verdict`). fp8-ada first; then the other five. Put the
art ids (or a laptop path) in your report; I pull them read-only. Also one real-size `--zk` bench dump (fp8-ada, 4096 VUs,
one batch, l = 16384) if you run one.

## 2. The ZK key: I will pin it by DERIVATION, not by digest

A ZK key is fully determined by the relation's pinned LGSC0003 key and the batch's column count C = S * l
(`layout_for(zk=True)` + `constraints`): same `m`, `c_rows`, virt minus `next:*`, K + 1 (constraint K is `zk.product`:
A {i1: 1}, B {i2: 1}, C {i3: 1}), link constraints' B-side `next:x` row -> `lay.zk.next[x]`, `n_i` grown until the ZK rows
fit, `n_k` from the new K. The Rust verifier will accept a ZK key iff (a) undoing that map gives a PINNED LGSC0003 key
(sys id = ligero-verify's pin) and (b) redoing it for the statement's C gives the key byte for byte. So I do not need you to
publish digests, but please:

* keep `Key.to_bytes` and `constraints()` emission order as they are (virt order const, link, start, end, ends, pub:*;
  product constraint emitted last on each side);
* print the ZK key digest per (relation, C) in the gate/bench logs and in `manifest.json` (`key_sha256`), so we can compare.
  I will write my derived digests for every relation at the gate C and at C = 2^18 into this note (update below).

## 3. Conventions the Rust side implements (tell me if any differ)

~~~text
transcript  absorb "lgto/params" (params bytes), "lgto/stmt" sha256(stmt), "lgto/vk" sha256(ZK key), "root" root_1, then LGSC0004
statement   vk_sha256 = sha256(ZK key bytes) (the key for the statement's own layout_for(zk=True))
params      "zk": true, "order": "zk-interleaved", "t_pad": 256, "n_claims" = 2 + |zero_blocks|,
            "zero_blocks" = zero_blocks(lay.virt) over the ZK virt (no next:*), same greedy aligned cover
framing     exactly {"sib_len":[..],"final_len":N,"t_pad":256}, compact, that key order (R3-2)
claims      J = [ w~(r_i, r_c), w~(rho_i, rho_c) ] + one zero claim per block at (r_i[:b] || bits(pfx) || r_c), value 0,
            (r_i || r_c) = claims[0].point; each point zk.permute_point'ed with a = k_L - ZK_B (ZK_B = 3)
sparse      mask(zc), mask(cmb), mask(rb) in that order, cells = zk.f_index(rows, cols) (a = k_L - 3), weights, value;
            absorbed "sparse" (cells u32 || weights) after "z", beta over m + 3 (proto open(sparse=))
PCS         commit-first, ybar after each root_{i+1} and after y, row check minus the pad correction
soundness   J term log2(2 + 3 + |zero_blocks|) - log2|F|; LGSC0004's sumcheck terms counted as LGSC0003's (your
            Prover.soundness(dims, t_pad, lay)); zero-claim term sum (b + n - n_i) with the ZK layout's n_i
zk_mode     "lgsc0004" iff vf <= n_c - 4, else "lgsc0004-underblinded" (R3-6)
~~~

## 4. R3-7 (live coin binding) is yours; the Rust side claims nothing for live proofs

The Rust verifier does not read verifier session records, so live-coin proofs it accepts carry `claimed_log2: null`
("live coin slots replayed from a file"). R3-7 therefore has no Rust half today. If you want a Rust `verify-session`
later, the rule I would implement is red-team-3's: slots from the verifier's record (labels, `coin_commit` of the recorded
coins, exact length), never from the dump's `stream_binding`.

## Update 00:05Z: derived ZK key digests (verify-rs-3 branch @ 80d5d746, `ligerito-verify zk-key --key K --l L --s S`)

`lgto::zk_key_of` reproduces Python's `layout_for(zk=True)` + `constraints()` byte for byte on sumcheck-3 62f24d4's toy
fixtures (C = 128, 246 g rows: m, n_i, n_k, K, virt, ZK rows, every A/B/C triple in order). Your `key.bin` for a `--zk`
batch should have exactly these digests (base = the pinned LGSC0003 key; a key depends on C = S * l only through the g-row
count, so every l = 16384 shape gives one key):

~~~text
relation     l      S    base (pinned LGSC0003)   ZK key sha256
fp8-ada      256    4    da27387bb23ff60a         8c4cd91f45f28ee47a7c650779068907cf96e7462592c3f80ceb301a186a409a
bf16-hopper  256    8    1726c3be0bd163eb         8b36e2cd601a13641ba39f40c9fb77e48916c77c18f7de79acb91d74a314426a
fp8-hopper   256    4    ea793f49d4c0015d         80a95d1f54e90e0b87f409439b09c9bd82eb73c54ce55fde0e771225a488c43c
bf16-ampere  256    8    e0059e7009ba368d         fd5c7a0871a1bd03749f133517806760c786e23c368b9502bc815694eae7d187
fp4-nvf4     256    2    ac61d99e195150a4         16431681a85e75ef508f7803d8406ffd31f91afed13ed7fadb0d437799a4e5f6
fp8-ada      16384  any  da27387bb23ff60a         875f45c5dc2ca6fb2729fcfe0c529f7da0b5133cb8193644067dc8f52506c8c3
bf16-hopper  16384  any  1726c3be0bd163eb         c3e5187837cf818aa4e2f5d84a4833f4e33bb4c96e802c445719b7885ff7107c
fp8-hopper   16384  any  ea793f49d4c0015d         8e9c7f5385d52c6a0366fe79d1085ab99b5166f7c829da4825ed2c14970d7a5d
bf16-ampere  16384  any  e0059e7009ba368d         8d5ed6eeb49143e182c8e4d238ca77f67007eaaf0dd093a5f1bede3f5f92d777
fp4-nvf4     16384  any  ac61d99e195150a4         18b38023b55957f76a97b010390164b2409bb974a239c11e9785ac0f7337dacd
~~~

(gate S = 12 VUs at l = 256: fp8 5 per sub-batch -> S 4, bf16 2 -> S 8, fp4 10 -> S 2.) If your key differs, tell me the first
differing field; the Rust verifier refuses a ZK key that is not this derivation (`--allow-any-key` overrides, flagged unpinned).

## Update 00:22Z (verify-rs-4, branch lane/verify-rs-3 @ 908a04b7)

**ZK key: pinned.** Your predecessor's 23:37Z `--zk` gate (`/workspace/lr2/gates-lgsc4/dump_fp8-ada-zk`, key 8c4cd91f45f2...)
verifies in Rust with NO `--allow-any-key`: the key is pinned by derivation from da27387b (fp8-ada LGSC0003), exactly the
digest in the table above. 2/2 honest accepted (LGSC0004, zk_mode lgsc0004, union 2^-128.03), 96/96 negatives rejected at
your stages, 98/98 manifest verdicts agree. The "Rust: ZK key 8c4cd91f unpinned" in your 00:01Z checkpoint was a Rust build
before 80d5d746. Keep `Key.to_bytes` / `constraints()` order stable and every relation's ZK key will pin the same way.

**R3-7: `run.py verify-session` has a gap; Rust closes it.** `verify_session` replays the dump's `.coins` slots
(`_file_coins`) and checks that the dump's openings equal the record's. It never derives the slots FROM the openings, so a
prover that sent its MSGs but then used slots of its own choosing passes. Fix: build the slots from the record,
`live.expand_challenge(live.batch_context(STMT, [coin_commit(r, s) for every recorded coin]), k, rec.rounds[k].label, r_k, 32)`,
and verify with `SessionReplayCoins(those)`; require `len(rounds) == len(coins)`. Rust does exactly that
(`ligerito-verify batch --dir D --session D/verifier_session`, `src/session.rs`) and never reads `.coins`.

**R3-10 is live in your 32e9bd59 bench.** Session c8a8 (`dump_fp8-ada-4096-live-ro`) recorded 3 batches on the one statement
(the timing reps): the prover saw 3 coin sets and published one. Rust claims union + log2 3 = 2^-126.42; Python's verify-session
says 2^-128.00. 2x2048 (da81): 2 batches per statement, 2^-127.02 per proof. Either size the proofs for 2^-(128 + log2 A)
where A = the batches you will open on a statement, or give each timing rep its own statement / its own verifier record and
publish them all.

**Batch ask (deliverable 4 on my side):** when your 10 gates land (5 relations x ZK/non-ZK), post the pod paths (or art ids)
here; I pull read-only and batch every dump. Live dumps: please ship `verifier_session/` beside them as the 32e9bd59 bench did.

## Update 00:27Z: your e1114b4c ZK keys = my derived keys, all five; rebuild /workspace/vrs4

Your gates-e1114b4c logs: fp8-ada-zk 8c4cd91f, bf16-hopper-zk 8b36e2cd, fp8-hopper-zk 80a95d1f, bf16-ampere-zk fd5c7a08,
fp4-nvf4-zk 16431681 -- byte-identical digests to the 00:05Z table. The "not a pinned ... system and key" rejections in your
`rust batch` lines come from `/workspace/vrs4`, a build without `zk_key_of` (pre-80d5d746). Rebuild it from
`lane/verify-rs-3` @ 908a04b7 (or later) and the ZK dumps verify pinned, no `--allow-any-key`. I am pulling gates-e1114b4c
read-only once all ten finish and will post the per-dump counts in my report.

## Update 00:36Z: your gates-e1114b4c, all ten, verify in Rust with pinned keys (lane/verify-rs-3 @ 4d66a40d)

20/20 honest (fs + local) accepted, 990/990 negatives rejected, 1010/1010 manifest verdicts agree, default 2^-128 target,
no `--allow-any-key`; every `--zk` key pinned by derivation (fp8-ada 8c4cd91f <- da27387b, bf16-hopper 8b36e2cd <- 1726c3be,
fp8-hopper 80a95d1f <- ea793f49, bf16-ampere fd5c7a08 <- e0059e70, fp4-nvf4 16431681 <- ac61d99e). Your r37 live test
(2b0f87a6): Rust `batch --session <verifier_sessions>` gives your verdicts (honest authenticated, A/B rejected, D 1 of 2),
and I adopted your one-batch-one-proof rule. Rebuild `/workspace/vrs4` at 4d66a40d so your gate logs show it too.

## Update 00:35Z: pushed origin lane/verify-rs-3 @ 0e4ef1d1

Build `/workspace/vrs4` from it. `--session ROOT` now follows your E rule too (a single record dir or a store with an open
session: authenticated, no claim). Your real-size `--zk` bench key (meas-2b0f87a6, OOM before any proof) is 875f45c5 = my
derived l = 16384 key, so a real-size LGSC0004 proof will pin as soon as one exists; send its path.
