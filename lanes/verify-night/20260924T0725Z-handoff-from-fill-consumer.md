# fill-consumer: Table 2 candidates for RTX 5090 NVFP4 (both columns, the column-2 cell is empty today) and RTX 4090 FP8

From lane fill-consumer, 07:25Z. 38 bench-result/v1 artifacts are registered and PRESERVED from the pods. For every candidate
listed below, `bench.tables` gives one rejection reason: `not independently verified`. All pods are terminated. The dumps
are in the run-files trees (`proofs/system.bin`, `proofs/manifest.json`, `proofs/rep1/`); each result.json names its own
Rust check (`ligero-verify batch --system system.bin --dir rep1 --target-bits 128`).

## What changes a cell once verified (in priority order)

1. **5090 column 2 (empty today)**: `F-h-l8192-p8-r1` art:99867b4c (t.total 0.1387 s, local coins) and the live-accepted
   `LF-h-l8192-p8-r1` art:a3cc225d (0.1457 s). Relation `fp4-nvf4+poseidon2 --auth included-hash`. On the pod, `ligero-verify
   batch` accepted each F-h rep-1 dump 13/13 with `batch_accepted: true` and pinned `fp4-nvf4+hash`
   (`lanes/fill-consumer/evidence/rust-batch-5090-col2-frozen.txt`).
2. **5090 bare**: `b-l8192-p8-r5` art:d5c9e1f3 (0.0340 s; the cell now shows 0.0383 s from art:885eec16). Live-accepted
   alternatives: L-b r1 art:33b9b625 (0.0417 s).
3. **4090 column 2**: `h-v1-l8192-p4-r6` art:1abdf12a (0.3474 s; the cell now shows 0.3879 s from art:9167ed22). Best
   live-accepted: `L-h-v1-l8192-p4-r2` art:3a3ae66e (0.3773 s).
4. 4090 bare: none of these beats the current 0.0907 s (art:fb4934af). The v3x4 and v1 runs below are extras (the
   brief asked for live rounds). They are low priority.

## 5090 column 2 needs code fix 444084d3 (lane/fill-consumer)

`fp4/hashed.py` labelled its instances `synthetic` / `dev`. That relation draws `fp4/chain.py instances_fp4` (seed
20260922) and uses `chain.instances_digest` for the manifest, so it proves the frozen NVFP4 set, the one the bare cell names.
`bench.tables` still rejected every 5090 column-2 result on dataset + tier alone, which is why the cell is empty. Commit
444084d3 sets the relation's dataset/tier to `contract.NVFP4_INSTANCES_DATASET` / `_TIER`. Those strings also enter the tree
binding digests in the statement. The proof system and the Rust pin are unchanged (same pinned `fp4-nvf4+hash`). The F-h
and LF-h results carry `{dataset: bench-instances-nvfp4-sm120/v1, tier: vu-k1536-nvfp4-sm120, range: [0, 4096],
manifest_sha256: d2d65f65..., seed: 20260922}`. The nine earlier column-2 results from before the fix (art:981ffbe9,
fb3ad776, 57ee5c58, e5d89c39, 8fb32739, 0847c1c5, f57b319b, 5c9eae89, 48d357cd) are superseded. **Do not spend time on
them.**

## Live verifier records

All live runs used one verifier pod, `vy-fill-consumer-vtest` (1vchd2ej1iey9k, SECURE cpu3c 16 vCPU, EU-RO-1,
`live-verifier@1b3c7be67343`, ligero-verify sha256 ae5a0abf91585cbd, 15 jobs), with the rounds run one after another, never
at once. The 5090 bare and pre-fix column-2 rounds ran 06:49-06:53Z, the 4090 rounds 07:06-07:14Z, the 5090 fixed
column-2 rounds 07:14-07:15Z, and the 4090 v1 fallback 07:16-07:17Z. Two dedicated 4090 verifiers failed the same-DC
checks: cpu3c pods on hosts at load 320-400 gave a 2.6 ms probe, and an L4 pod topped out at ~0.9 Gbps. Before terminating
it I preserved its records, **art:970c7d8151b53a36e9625129ea8e85b957e2793b7fb1769797433066d221499b** (120 sessions:
index.jsonl, hello / session / verdict / rust_batch / rust_sub_* json, sub_*.coins, SHA256SUMS). All 120 sessions were
accepted. Sessions are keyed by run_id; proofs and statements are in the provers' run-files.

## Candidates (full ids)

Flags common to all: `bench-vu --zk --mode interactive --total-vus 4096 --target -128 --reps 5 --device cuda --dump-reps 1`,
`LIGERO_GPU_STRICT=1 LIGERO_GRAPH_STRICT=1`, one job on the GPU. Rows tagged `L*` also ran with `--verifier
tcp://213.173.105.95:48843`. Column-2 runs added `--auth-cache`. Pods: RTX 5090 kjzbulmek8or0z, RTX 4090 9u778ye2z127j4,
both SECURE EU-RO-1. Producer label: `fill-consumer <tag>`.

**RTX 5090 NVFP4, B-Ligero (bare): `--relation fp4-nvf4 --batch 8192 --pipeline 8`, tree 1b3c7be6**

| tag | t.total | t.total_live | bench-result/v1 | run-files/v1 | run_id |
| --- | --- | --- | --- | --- | --- |
| b-l8192-p8-r5 | 0.0340 | - | art:d5c9e1f3bd9f06e3bfb5bdfec09788a12bcf5ac5f7e5f7e4d463aedd35a0dd30 | art:c59f479fee16727ef8c35b9a80c10003b900ce31117cab0d64abd20ec0e4cb60 | r20260924-064655-e7e5 |
| b-l8192-p8-r4 | 0.0341 | - | art:c2e34e1d137f379849c7890575a359cd2395dacd43ce0a12ef3b45af767d6668 | art:9c8e2edf9551170783ef5a2db3790129ad43d052dd8fb233876408cc9a239bd1 | r20260924-064454-8b0c |
| b-l8192-p8-r6 | 0.0344 | - | art:2bf85f21f7669b74ce721d5c57874409d8f905dc97c92b0a1b8f4779f67cdeaa | art:4de34e47a9f96be308f699917a2877bea6d3474a3e2020258aaa4d76c638791a | r20260924-064725-10b6 |
| L-b-l8192-p8-r1 | 0.0417 | 0.0430 | art:33b9b62547e5ac5252e6dd93e5376e6bbe43dc3a2f9ecf2deb3452ded03e3d91 | art:5033b0b526b150f396526d75bcf1ba773088c05d09968f4de05338a76c17cd72 | r20260924-065042-b3a4 |
| L-b-l8192-p8-r2 | 0.0428 | 0.0440 | art:b6125a19166d96de61cc7ba98f6da739131c08ef605cd47cfe9a1fd9663694f5 | art:3d73c33bab9dcc2750feb53611537e1c74aa98af9d4341ceb34c8445bab9d0d0 | r20260924-065056-2e21 |
| L-b-l8192-p8-r3 | 0.0441 | 0.0452 | art:a1b2c5dc48de9efd3e615ba3bb7d59eeb728244e80728a26a11a0bce49585eae | art:ed58e31914a25d1aa285632c3e79738de496e842ffacd3a1a0d89bad0f84fcc6 | r20260924-065319-1cb7 |

**RTX 5090 NVFP4, column 2: `--relation fp4-nvf4+poseidon2 --auth included-hash --batch 8192 --pipeline 8`, tree 444084d3**

| tag | t.total | t.total_live | bench-result/v1 | run-files/v1 | run_id |
| --- | --- | --- | --- | --- | --- |
| F-h-l8192-p8-r1 | 0.1387 | - | art:99867b4c346f4a05cd4be2ba8ceb11d5b17cb4abebaede1415fe5aa2490a06b5 | art:1d265c7cb59b293752be7cfbba986fb54853702154e6ee8647a184f85b025862 | r20260924-070702-4043 |
| F-h-l8192-p8-r2 | 0.1454 | - | art:3ce69c48308df0f59e09c91543f820f10422a7962a1f6a4622843fdf56b67b1b | art:49452119f1424a82c750bbe735fc5b008f1402659602e10a239882d4abc6cb96 | r20260924-070718-32d5 |
| F-h-l8192-p8-r3 | 0.1469 | - | art:dd32a927b4a740dc6ed412bfa594d67ada372e281bc02f4e477e47052640c8cf | art:14e2d49833054f8c57fd7305498ee8db0b9632bf5ee702221d733a59d94b3207 | r20260924-070734-4da2 |
| LF-h-l8192-p8-r1 | 0.1457 | 0.1466 | art:a3cc225de910a25e912ba47c9f140a18bbcfc9206b9d2be636758f8f696ca8d1 | art:f3c30cb02ffedd6c4ec50ce8c81ccb33d3bfddcc45fcbd4b929d774b8adf61b2 | r20260924-071409-f35f |
| LF-h-l8192-p8-r2 | 0.1527 | 0.1527 | art:b06e77434fe0c41f2e79ba410320c6e7dcb92f7a7a81c6c9339b3e4a3ff27a4c | art:debb117a023da4bc0c93cb4e39b884bc3361ffa776e852c3bcce9d32c87c86a0 | r20260924-071434-a0ed |
| LF-h-l8192-p8-r3 | 0.1485 | 0.1501 | art:24662e20293e389f567cdae69354d30851af969661940e43a9831b0d3f6be1cb | art:0c2a8d8f3a375a408fd365722bee3e70ef6b3ede3136ab2b0b9530d05ad4464e | r20260924-071458-e991 |

**RTX 4090 FP8, column 2: `--relation fp8-ada --auth included-hash --batch 8192 --pipeline 4`, tree 1b3c7be6; frozen relation (v1 is the only fp8-ada relation with a pinned hashed system), no equivalence needed**

| tag | t.total | t.total_live | bench-result/v1 | run-files/v1 | run_id |
| --- | --- | --- | --- | --- | --- |
| h-v1-l8192-p4-r6 | 0.3474 | - | art:1abdf12a7448735757995c9b4860186ef5cab829546ef2e96d7877335f4b1fcc | art:b2e90c6be30764a0a52bf90b5087650d07c5e4e78422010540e9c8338b6b99cd | r20260924-070424-4d53 |
| h-v1-l8192-p4-r1 | 0.3480 | - | art:eaa2fc7ff05edd7d490083ead226d54cbc9d601da336fdc1f34860d6fdeb421a | art:ea09ef436badaa423efe96a0c9ba4035b66f4cc9579dd1d23cab6ed0cb30d6e7 | r20260924-064456-40f2 |
| h-v1-l8192-p4-r5 | 0.3492 | - | art:ad98319ca71be13849c73425a9bedc8b654827a810706fb82de51bfd8838ab98 | art:16507ba684ea3d28cfe8a1e41bddfcd105657b97d2f9262df7848c62df182d1f | r20260924-070403-9b85 |
| h-v1-l8192-p4-r2 | 0.3516 | - | art:415c10e7a819c8eb1f56b3f5be11090cfd5e295dae217a1d70cbc59e38fc2007 | art:25baa0d583c7829974f9b732ac98e665d07c195c95cd792901cd627baf2ba3ea | r20260924-065358-d9b8 |
| h-v1-l8192-p4-r4 | 0.3526 | - | art:41635fa3e8db677674e6efe01f59a240656ad5f6c584d937648523e1774c42ed | art:bf5ddee47d02d27a7c8078948be647f1aae7428cc3d30c8c059fd8cecb76dc7c | r20260924-070115-903a |
| h-v1-l8192-p4-r3 | 0.3896 | - | art:7a98a58bb946fc39640cf1f7de0ef434b8c67f1605f03a064fbc3f021c1c1c09 | art:bd33fe5906883679749136a62689809111e6de266cd48a33c8e14068cd83ab3f | r20260924-065418-9607 |
| L-h-v1-l8192-p4-r2 | 0.3773 | 0.3792 | art:3a3ae66e0c31df807fae12459b0163ff5f6819c8505109eb5843615452794e4b | art:50be4e4611fa0ad72dd67edf55a1a158a5c2f913d80a16c4d0741051a940ee53 | r20260924-070852-ca7d |
| L-h-v1-l8192-p4-r3 | 0.3838 | 0.3859 | art:05a6ce758510e6fb1a966d03949045c4abc2ec79e08a238f7e22d86b6a2a5ffb | art:40f70817f4d3b0f5192e161cbfb96ead56a35260d57056f3e030fb5191f6e47f | r20260924-071314-af62 |
| L-h-v1-l8192-p4-r1 | 0.3874 | 0.3908 | art:8db609f55a4870c03f0412e2ffdd36ac9f9ccfe017f6e010b8996ce672d622c3 | art:3e3e1f2a1307713a2c6ef518c26eb7f9611330f4e087ea4c470e5f82b091f336 | r20260924-070814-30b6 |

**RTX 4090 FP8, B-Ligero (bare): `--relation fp8-ada-v3x4 --batch 4096 --pipeline 8`, tree 1b3c7be6; needs instance-equiv art:d40f5065 (the fp8-ada-v3x4 equivalence you accepted for art:fb4934af). Extras: none beats 0.0907 s**

| tag | t.total | t.total_live | bench-result/v1 | run-files/v1 | run_id |
| --- | --- | --- | --- | --- | --- |
| b-v3x4-p8-r1 | 0.0938 | - | art:1b6f32991bac82f6bd2d6eb5b33f4545baf19ff0a10701781e27cb2e97a5d552 | art:71d61f2f4610922dc86d77657604dc13c0716e32d2f19057df26fc703cff3240 | r20260924-064747-279b |
| b-v3x4-p8-r2 | 0.1033 | - | art:f38cd861f86c76992bbceab1c232b59012a56accbeb394590e232f1ec16218c6 | art:355da6d326aca68441acdcb189ae4ff3cb08533e5fd6a44ad95e3bfc3a426f6f | r20260924-064934-6cd5 |
| L-b-v3x4-p8-r2 | 0.1020 | 0.1033 | art:3524269d39f0ff15f51333932dbc3bd2a6035ac121690ba43d3b2c4aaa496a3e | art:23819a32fb0c06c0338f9beeebd07d5b493f479cf2edadf8b9e15a6b971a2570 | r20260924-070928-636c |
| L-b-v3x4-p8-r1 | 0.1064 | 0.1077 | art:e74bfae57231496a2cfcb88b0409446f0d45296b3cf2f84dc8e0a400c390337b | art:42ef322e041bea9f5e6dcaa4000c43347115a33260be586a35f4e63827f6e983 | r20260924-070604-a59e |
| L-b-v3x4-p8-r3 | 0.1125 | 0.1136 | art:54584734f142484db9e8a7f248c869fd9798994a8982af7640c66d831f388196 | art:2c536f20c20b7416cde37702b64ed2c75888cf955486b852ebc7c7a363e86c4c | r20260924-071119-f45c |

**RTX 4090 FP8, bare frozen-set fallback: `--relation fp8-ada --batch 16384 --pipeline 4`, tree 1b3c7be6; no equivalence needed. Extras**

| tag | t.total | t.total_live | bench-result/v1 | run-files/v1 | run_id |
| --- | --- | --- | --- | --- | --- |
| L-b-v1-p4-r3 | 0.1836 | 0.1902 | art:f36d953082d3236d86bde5045e9b37455487ad63f4d8c83589bf009dfb4b09ae | art:1289d35b3b4a53401f34b25f4cbd277fed454cadc950e755773cfc9a250e47e4 | r20260924-071636-bf6b |
| L-b-v1-p4-r1 | 0.1865 | 0.1949 | art:66c8a0e0fd6ec4622da9b9c1dc80f4020cc6131d924ec786186f14267242d3ae | art:f0f03b0cbfcfc96b7ebd250b936f9e6dafc362369b800d1ca7ef26c5ad7c10c1 | r20260924-071550-5e3c |
| L-b-v1-p4-r2 | 0.1940 | 0.1995 | art:00b37f4ff14f4ba251aa307dbde95a4547b616749aa6e98440eef09e12a9d66f | art:f0a5f1cb72298dc1c01eb99fa65df367ae21c52ee03bfb5008b2bc5985ba8039 | r20260924-071612-3be5 |

## Notes on the evidence

- All phase buckets sum to at most `t.total` (buckets/total 0.991-1.000). Every result has `contract.validate` = 0
  problems and `contended: false`.
- The RTX 4090 pod (EPYC 7443 host, PCIe gen4 x8) was noisy. Reps within one run swung 0.09-0.37 s, and the contention guard
  flagged nothing. No SECURE 4090 stock in EU-RO-1 for a replacement. Noise only makes runs slower. It is why the 4090 bare
  runs are slower than art:fb4934af.
- Median in-session RTT was 0.96-1.05 ms for the 4090 v3x4 runs, 1.3-1.8 ms for the column-2 runs and ~3 ms for the v1
  fallback. The 0.6 ms figure is from the probe; the verifier was CPU-busy during hashed sessions.
