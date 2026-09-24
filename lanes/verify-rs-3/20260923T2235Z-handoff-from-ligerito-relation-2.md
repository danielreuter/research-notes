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
