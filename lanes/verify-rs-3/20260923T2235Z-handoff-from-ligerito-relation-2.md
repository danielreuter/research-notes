---
lane: ligerito-relation-2
to: verify-rs-3
kind: handoff (answers your 21:55Z asks + 22:05Z update)
created: 2026-09-23T22:35Z
branch: lane/ligerito-relation-2 @ e3ad950 (V1 = cf9a63a; proof/statement/key bytes unchanged since cf9a63a)
---

# V1 opening layout (as committed), fixtures, pins, F11, F5

## 1. Opening layout: your 22:05Z update is exactly what the prover writes

~~~text
blocks   proof.zero_blocks(key.virt): the aligned cover of every maximal run of consecutive virtual rows, runs in row order,
         each greedy from its low end (largest aligned block that fits); SAME rule with and without --zk
params   "zero_blocks": [[b, pfx], ...] in that order (rows [pfx << b, (pfx + 1) << b)); "n_claims" = 1 + n_links + len(blocks)
claims   J = [ w~(r_i, r_c) = values[0],  w~(bits(c_x), rho_c) = values[1 + x] for x < n_links,  then one per block, value 0 ]
point    block (b, pfx): (r_i[:b] || bits(pfx, n_i - b) LSB first || r_c), (r_i || r_c) = claims[0].point;
         r_c = the ZERO-CHECK's column point (NOT the combined sumcheck's rho_c; docstrings in proof.py / prove.py now say so)
PCS      every point rotated like the others: (p_c || p_i) row-major; zk.permute_point under "zk-interleaved";
         absorb "z" = all J points, beta = challenge("beta", J), running = sum_j beta_j values_j
sound    + log2(1 + n_links + |blocks|) - log2|F| (beta), + log2(sum_blocks (b + n_c)) - log2|F| (zero claims)
~~~

Read back from the dumped proofs (`params.zero_blocks`, `[b, pfx]` -> rows); the free rows above the last virtual row are not
zero-claimed (the prover zeroes them in non-ZK mode, no constraint or public row reads them):

~~~text
fp8-ada      m=3577 virt [3577,3777)  6 blocks: [3577,3578) [3578,3580) [3580,3584) [3584,3712) [3712,3776) [3776,3777)
fp8-ada --zk same 6 blocks (zk-interleaved, t_pad 256)
bf16-hopper  m=3196 virt [3196,3300)  4 blocks: [3196,3200) [3200,3264) [3264,3296) [3296,3300)
fp8-hopper   m=3204 virt [3204,3404)  8 blocks: [3204,3208) [3208,3216) [3216,3232) [3232,3264) [3264,3328) [3328,3392) [3392,3400) [3400,3404)
bf16-ampere  m=3420 virt [3420,3524)  4 blocks: [3420,3424) [3424,3456) [3456,3520) [3520,3524)
fp4-nvf4     m=1442 virt [1442,1593)  9 blocks (n_i = 11): [1442,1444) [1444,1448) [1448,1456) [1456,1472) [1472,1536) [1536,1568) [1568,1584) [1584,1592) [1592,1593)
~~~

## 2. Pins (sys_id, sha256(key.bin)), l = 256 gate keys at 32d3d42 (key bytes unchanged by V1)

~~~text
fp8-ada      6b570eef0c7faa07ccd1dddb2508e2699bd5367b108b15920469d46d16073d37  da27387bb23ff60a60b4b21ef99f180c84c17456edf41efa31e5797aaed9227b   (= your 3592bd0 pin)
bf16-hopper  9dcc7cdc1377a00d877440cc01a0dcdb73b3e989d86df8244eccb35a81be0df4  1726c3be0bd163ebfba38cc8e9fcaed0d74b76f3b592db0748e6be254b946846
fp8-hopper   c7cbebe365cb5f773a679bc13b5382fb45714511b1912e4e4ab7fb48accd4bc3  ea793f49d4c0015d835d886df3bab65949189f20a8f35222e653482dc7d65d60
bf16-ampere  44cb05b9e6988219beba2d66582124e67a1893aac39d0b66126ce0b9d4db89cb  e0059e7009ba368dc1119abdc923dfcf6e06b81d4424e81106fdd01721a30eb6
fp4-nvf4     a825ba0b826a15366bfb8cdd720a5e9978603cbe589491abcbba7346ad35bf3c  ac61d99e195150a4c23ccc9d3d5ff73cd72248b7236843ae5339a07c4708928e
~~~

The key depends on l: the 4096-VU bench keys (l = 16384) are different files (`key.bin` in each bench dump below).

## 3. Fixtures (all `research data fetch ART`; remote = 1 verified)

Gate dumps, 32d3d42, l = 256, 12 VUs, L40S. Each dir holds BOTH coin kinds (fiat-shamir + local): 92 files = 2 honest + 90
negatives (45 per kind), among them the five V1 forgeries per kind (manifest `name` starts with "V1 "; four must fail at "PCS",
`next:0` at "combined final"). Python verify-dir 92/92 each.

~~~text
gate_fp8-ada_l256       art:796428f93f7fdd8a3cf3b95993c355d3bef071fa66a3f52dc53f4b984eac6fc9   35 MB
gate_fp8-ada-zk_l256    art:c91bab2a10e9c5f670e3a193d8e9d3f1915845d12730c0121b962555ee411771   38 MB (t_pad 256, ybar)
gate_bf16-hopper_l256   art:a4e959668e530fb01cf4a4aeb030937be6a2021ab57e4dac2bd4e1a5a8e6e666   44 MB
gate_fp8-hopper_l256    art:e50e2ff554c21558c18166a099640d3a765def1191d6062b0eccde3a47218528   35 MB
gate_bf16-ampere_l256   art:998cbafeff45a3b160f96112a49500d652ce6d64c087409c0fbbd07af3459def   44 MB
gate_fp4-nvf4_l256      art:89063ba36887fe3cb9464aa39aace066c7ded78bf1090a96d17d31049f5d2c44   31 MB
~~~

Your item 1 (FS only, small) is on disk: `~/.research/notes/lanes/ligerito-relation-2/evidence/gate_fp8-ada_l256_fs/`
(the fiat-shamir entries of art:796428f9…, 46 files, 17.8 MB, manifest filtered, `subset` key says so).

Real-size dumps (4096 VUs as ONE batch, l = 16384, N = 2^30, H100, abd8f5e; `n_proofs` = 1):

~~~text
fp8-ada local        art:e89d2c1c3dfdaee3efb3dd4b57ce34f6835a794df75cd03c9ec1f4238f4c16ca   15 MB
fp8-ada fiat-shamir  art:7014c64b31fb460c6e88e81c7dc6da2196df3c31b5d7d249664ef324213451c7   15 MB
bf16-hopper local    art:5adab7165bcdc51d0008b864065551d01d74af04e1b1274c126d3ec5133a4840   27 MB
fp8-hopper local     art:3b57ee977f6ddd7c22c4729a19c1f98589dd0f49c4cbc13c9326acde94ab4269   15 MB
~~~

Live-coins dumps (`.coins` + `stream_binding`): a LocalChallenges one (4090, same stream code, no network) and the network
session against vy-live2-verifier after 23:00Z; art ids will be in my report `## FINAL`.

## 4. F11 and F5

* **F11 fixed on the Python side (abd8f5e)**: non-ZK `prove.pcs_verify` rejects non-canonical words in every PCS column-sumcheck
  message and the final vector (`_canonical`, same rule as `proto/pcs._verify`); opened rows were already range-checked.
* **F5**: manifest.json now carries `"n_proofs"` (distinct statements of the job; gate = 1, bench = number of batches) from
  e3ad950. The prover still sizes every proof for 2^-128 on its own, so a multi-batch bench dump (4 x 1024) fails your union
  check; re-dimensioning `dims_for` to 2^-(128 + ceil log2 n) is NOT done (remaining work). All my headline runs are one batch.
* **F12 labels** (FYI, same accounting you use): bench `security.target` is null unless the run's claim meets 2^-128;
  `achieved_log2` = interactive union only for live coins whose verifier session accepted; Fiat-Shamir = 64 + max term
  (2^-65.1 for fp8-ada: the query sets are FS too); local / replayed coins = none.

## Update 22:58Z (ligerito-relation-2 @ 0db857a9): your three asks + F5

* **Ask 2, statement canonicality: YES.** Landed in Python at `0db857a9` (`Prover._stmt_subs`): every real sub-batch's `y`
  must be 0 wherever `lay.chain_layout(s).masks()[2]` (the `end` mask) is 0; reject reason
  `statement sub-batch {s}: claimed word off a chain end (non-canonical)`. Honest dumps already satisfy it (all 6 gates).
  New gate negative per coin kind: `statement word y[0] = 1 off a chain end, proved for that statement (non-canonical)` =
  a proof MADE for that statement (the prover writes the word into the end rows, `ypub_override`), so without the rule it
  is a valid proof: your current build should ACCEPT it (verdict mismatch -> `batch --dir` exit != 0 on my 0db857a9 gate
  dumps until you add the rule). The two `n_vus - 1` negatives now build canonical statements (the dropped VU's end word
  zeroed), so they still reach the PCS / combined final.
* **Ask 1, Rust in my gates:** done. `lane/verify-rs-3 @ 41570f1` built on my 4090 (`/workspace/vrs3`, release, 16 s);
  all-relation gates at `0db857a9` run with `--rust-verifier` now (verdicts in each dump's `verify_rust.json`). A first
  fp8-ada gate at 0db857a9's parent tree: rust exit 0, 94/94 manifest checked (before the "proved" negative existed).
* **F5 in bench:** `bench` now sizes each of n proofs for 2^-(128 + ceil log2 n) (`Prover.batch(target_log2=)`; 2^-128
  dims unchanged, so 1-proof dumps are byte-compatible); `security.per_proof_target_log2`, `union_over = n`. Tested on a
  2 x 12-VU live dump: per-proof union 2^-129.03, your binary exit 0.
* **Live coins:** new `run.py verify-session D <session dirs>`: matches each live proof to the issuing verifier's own
  `session.json` (openings = the verifier's coins, STMT digest = `b"lgto-stmt|v1|" | sha256(params) | sha256(stmt) |
  sha256(key)`, every round's `msg_sha256` = sha256(BLAKE2b of the proof's absorbs since the previous slot) and label),
  writes `verify_session.json`; only then is the interactive union claimed. If you want the same in Rust: the MSG digest is
  `blake2b-256` over `u32 len(label) | label | u64 len(data) | data` for every absorb since the last coin, as
  `prove.StreamCoins.absorb`. Live dump from the RO verifier follows tonight (art id here).
* **Ask 3, LGSC0004:** not in my `--zk` proofs yet (still LGSC0003 + the partial row masks). I will write here before any
  switch, with a dump.

## Update 23:00Z (ligerito-relation-2 @ 32e9bd59): three canonicality rules for the Rust reader

1. **y off the chain ends = 0** (0db857a9; see 22:58Z). Confirmed malleable before: on my 0db857a9 fp8-ada gate dump your
   41570f1 build ACCEPTS `neg_{fiat-shamir,local}_45` (a proof made for a statement with `y[0][0] = 1`; the constraint is
   `end · (Y − y16) = 0`, silent where `end = 0`), Python rejects it at "statement". That is the only verdict mismatch in the dump.
2. **Pad-unit operand words = 0** (red-team-3 R3-3; 32e9bd59): every a/b word at columns `>= n_vus[s] * steps` of a real
   sub-batch must be 0 ("operand word in a pad unit (non-canonical)"). Gate negative `neg_*_46` (honest proof + one pad word
   = 1): you already reject it (proof mismatch), so no verdict change, but please add the rule.
3. **Canonical framing JSON** (red-team-3 R3-2; 32e9bd59): `read_proof` requires the framing blob to be byte-equal to
   `{"sib_len":[...],"final_len":N}` (+ `,"t_pad":T` when present), keys in that order, ints, no spaces. Your reader accepts
   red-team-3's re-encodings (their fixtures dir `framing_malleability_fp8-ada_e3ad950/`).
All-relation gates at 32e9bd59 are running on my 4090 with your binary; dumps + verify_rust.json go to R2 at ~23:15Z.

## Update 23:16Z: your 60d9cbd agrees on every 32e9bd59 gate; sparse fixture dropped; live dumps + session records

* **Gates @32e9bd59** (4090, 6 relations, 4 positives + 94 negatives each, 0 Python failures): your `60d9cbd` (built from a
  `git archive` of it on my pod) accepts all 6 dirs, 96/96 manifest verdicts, no problems (`verify_rust_60d9cbd.json` in each
  dump). Gate-report art:9d83f26d; dumps (fixture/v1, remote=1): fp8-ada art:4dd85136, fp8-ada-zk art:16870df5, bf16-hopper
  art:fc4674a7, fp8-hopper art:8b67b6b0, bf16-ampere art:8265d89d, fp4-nvf4 art:173734c4. The `verify_rust.json` there
  is 41570f1, which accepts `neg_*_45` (as you said).
* **Your ask**: `evidence/pcs_sparse_fixture_lr2-32e9bd59.json` (sha256 54d42cac…; my tree @32e9bd59 = proto/pcs.py
  `open(..., sparse=)`, RTX 4090): "2 cases, 5 negatives each".
* **Live dumps on RO with the verifier's records** (4096 VUs fp8-ada, 4090 in EUR-NO-1, live-verifier@80547525ac60):
  art:53ab06f7 (1 batch, R = 48, session `c20260923T231103Z-c8a8`) and art:6ff439a8 (2 x 2048, R = 47,
  `c20260923T231131Z-da81`, each proof at 2^-129.02, `n_proofs` 2); `verifier_session/<id>/{hello,session,verdict}.json`
  inside each. `run.py verify-session`: 1/1 and 2/2 authenticated; your batch: accepted (0.40 s / 0.22 s per dir),
  `claimed_union_log2` None (right: you do not read session records). If you want Rust to claim the interactive union, the
  rule is `run.py verify_session` (per live proof: coin openings = a verifier batch's; STMT = `lgto-stmt|v1|` sha256(params)
  sha256(stmt) key_sha256; each round's msg_sha256 = sha256(BLAKE2b-256 of the absorbs since the previous slot, framed
  `len(label) u32le || label || len(data) u64le || data`) and label; verdict accepted).
