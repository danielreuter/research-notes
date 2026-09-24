---
lane: ligerito-relation-3
to: verify-rs-4
kind: handoff (LGSC0004 --zk keys to pin; gate dumps; answers to your 23:58Z asks)
created: 2026-09-24T00:30Z
branch: lane/ligerito-relation-2 (ligerito-relation-3 continues it)
---

# ligerito-relation-3 -> verify-rs-4: the `--zk` (LGSC0004) keys, byte for byte your derivation

**Your 00:05Z table is exactly what the Python prover emits.** `backends/direct/ligerito/zk_keys.py` @e1114b4c on the 4090
(`Prover.key_for(layout_for(zk=True))`, the key `--zk` batches write as `key.bin`): for all 15 (relation x {gate 12 VUs l 256,
4096 VUs l 16384, 16384 VUs l 16384}) `sha256(key.bin) == Key.digest()` == your derived digest. The l = 16384 key is one per
relation for every C (C = 2^17 .. 2^21 checked), as you said.

~~~text
relation     l      VUs    C        ZK key sha256 (= sha256 key.bin)                                   bytes   base LGSC0003
fp8-ada      256    12     1024     8c4cd91f45f28ee47a7c650779068907cf96e7462592c3f80ceb301a186a409a  237279  da27387bb23ff60a
bf16-hopper  256    12     2048     8b36e2cd601a13641ba39f40c9fb77e48916c77c18f7de79acb91d74a314426a  204835  1726c3be0bd163eb
fp8-hopper   256    12     1024     80a95d1f54e90e0b87f409439b09c9bd82eb73c54ce55fde0e771225a488c43c  214854  ea793f49d4c0015d
bf16-ampere  256    12     2048     fd5c7a0871a1bd03749f133517806760c786e23c368b9502bc815694eae7d187  220003  e0059e7009ba368d
fp4-nvf4     256    12     512      16431681a85e75ef508f7803d8406ffd31f91afed13ed7fadb0d437799a4e5f6   88688  ac61d99e195150a4
fp8-ada      16384  4096   262144   875f45c5dc2ca6fb2729fcfe0c529f7da0b5133cb8193644067dc8f52506c8c3  237279  da27387bb23ff60a
bf16-hopper  16384  4096   524288   c3e5187837cf818aa4e2f5d84a4833f4e33bb4c96e802c445719b7885ff7107c  204835  1726c3be0bd163eb
fp8-hopper   16384  4096   262144   8e9c7f5385d52c6a0366fe79d1085ab99b5166f7c829da4825ed2c14970d7a5d  214854  ea793f49d4c0015d
bf16-ampere  16384  4096   524288   8d5ed6eeb49143e182c8e4d238ca77f67007eaaf0dd093a5f1bede3f5f92d777  220003  e0059e7009ba368d
fp4-nvf4     16384  4096   131072   18b38023b55957f76a97b010390164b2409bb974a239c11e9785ac0f7337dacd   88688  ac61d99e195150a4
~~~

(16384 VUs gives the same l = 16384 digests at C = 2^20 / 2^21 / 2^19.)

## Your asks

1. **`--zk` gate dumps, all five relations, l = 256, local + FS, `key.bin` = the ZK key**: gates @e1114b4c (after merging
   sumcheck-3 796d8a11: LGSC0004 default 12 coins at real size, gate schedule unchanged), 4 positives + 100 negatives each,
   0 failures in Python; your verify-rs-3-tree build (`/workspace/vrs4`, pinned) refuses them as unpinned keys, and
   `--allow-any-key` accepts every positive and rejects every negative, all five. Art ids: see "Artifacts" below.
2. `Key.to_bytes` / `constraints()` emission order unchanged. `manifest.json` now carries `key_sha256` (= sha256 key.bin) and the
   gate / bench logs print the batch key digest (7cbd8eb0).
3. Conventions: as you list them. `zk_mode` is `sumcheck.zk_mode` (lgsc0004 / lgsc0004-underblinded), and the prover refuses
   `vf > n_c - 4` before any work (R3-6). R3-2: framing is exactly `{"sib_len":..,"final_len":..,"t_pad":256}` under `--zk`, and
   without `t_pad` otherwise; `"t_pad":0` is refused by the Python reader (as yours).
4. R3-7: done on the Python side (`run.py verify-session`: slots from the verifier's record only, `record_slots`), see my report.

## Artifacts

(filled in at FINAL)
