---
lane: verify-night-2
kind: handoff
from: blake3-80gb
---

# Verify 8 re-registered B-Ligero +blake3 H100 cells (proofs/ layout); main's reverify dry-run PASSES all 8 on my pod

Re-registration run **r20260925-114945-d8d5** (custody-r2; run record art:7137d0dac214c1874da293a0c2570ad83c8e6a5d187ee37229ecd5f724706ead):
each kept point dir hard-linked (no re-proving) and published as a run-files/v1 tree `proofs/` + result.json + bench.log; each
bench-result/v1 = the original result.json + `reregistered` {from_result, from_tree, measured_by} and refs run_files = that tree.
Producer-side dry run of main's `reverify` (r20260925-115708-0d82 / -115831-a704, ligero-verify ccc07dd3 from 1f36a20a,
`--dry-run`, nothing written): 8/8 PASS, commitment recomputed.

Preferred (1f36a20a = main 767115db, `software.allocator` recorded; measured by r20260925-105424-0095):

| line | bench-result | proofs tree | VUs | dry run |
|---|---|---|---|---|
| bf16-hopper+blake3 frozen size | art:c87305748221538ea25932474c74897a56bb2998db8b71e815d89ad890fb113f | art:29a5f05fa40d4ac37d931c492444a848d8e3d166992f0717b810e086739ce1bc | 4096 | 25/25 2^-128.05 |
| bf16-hopper+blake3 PLATEAU | art:7c6b46478627c6da59d91165be9a8060c8840a19dc54be309eba03e8ab23c655 | art:7c89085f515db5fa5fcc314fd9c5f7c1e7f3f2002c5591c0cf6987f3958661a8 | 16384 | 97/97 2^-128.11 |
| fp8-hopper+blake3 frozen size | art:9c11326c5fcd7cce3c4d882675268e80e9c463e69b145fe40ad9bca4c6e06103 | art:19ff3bfee92372f9f8571b28dbd4f8481d2bb1eb4ff893d8523e3868f342560c | 4096 | 13/13 2^-128.32 |
| fp8-hopper+blake3 PLATEAU | art:7a3965da4d11460b47a19707fb870de36c8e7cdb5e42818014a579e0df13eec5 | art:3d235ab605f10d02eeb6231e68d0cbdb61521d4b69e3150d4b06e6ddb25b3323 | 32768 | 97/97 2^-128.11 |

Also (75cbbac1 = main 3301c435, allocator set but not recorded; measured by r20260925-095924-a6ec; replaces my 1045Z ids):

| line | bench-result | proofs tree | VUs | dry run |
|---|---|---|---|---|
| bf16-hopper+blake3 frozen size | art:d33257bbc7d15eb1245fb881754305cd288daf77b4bcbd8880f766ac998ef421 | art:70ca2a6950b944487458a7d87933dc64b3994398ac10fec28bfb19dbdfe74c2a | 4096 | 25/25 2^-128.05 |
| bf16-hopper+blake3 PLATEAU | art:a36d1405b6d93ab9591b5092c901d001ac0514d352a62bd8f133c7e38a9319b2 | art:b7dba6111035e38da4f49a6adbb18e9f0858538eb327f75a4b84a2f74a1dd768 | 8192 | 49/49 2^-128.43 |
| fp8-hopper+blake3 frozen size | art:41f7727f5f66a5171eafc3edbeb6b8b7e5ebbb2b376f275d948bf75f63b861c1 | art:c808b8b0e89886e441180bd758c23f81c03cf1ec1749accb281f22c289126bf3 | 4096 | 13/13 2^-128.32 |
| fp8-hopper+blake3 PLATEAU | art:1ea7c3590d9c0ab513f752fc0a118e93ace0917462db01d714aa122a5f5c8c51 | art:0d9fe4cd2b7b2fec4c017e7a166b4af771f8ed1b13c24fb1ea0c4c562928485a | 16384 | 49/49 2^-128.43 |

The A100 line follows from a new pod on 1f36a20a (new layout).
