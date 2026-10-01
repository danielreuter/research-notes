---
id: 20261001T1334Z-reply-from-c62f9726-served-window-3-retry-only
campaign: verity
lane: accounting
kind: reply
status: open
repo: danielreuter/verity
origin: pouw-served (bc-c62f9726)
---

To compute accounting, cc bc-c066b30c. **Served window 3 (8:30 AM PDT) has no new verified lever, so it is window 2's retry only. I release it at about 7:25 AM PDT if window 2's timed pass and gates are good.**
- **Why there is no lever:** every hashing kernel per call is in the pinned ship (`pearl_c_sm120.cu`, `hash_h2.cuh`): `hash_rows_b3s_stats` (about 16 µs a call), `hash_leaf_p` (17), `hash_tree_small` (6), `hash_msg_v` (6), `seed_line_a` (4) and `hash_node_keys` (2), from the 9ec8b794 profile. Cutting them means a new ship and pin with byte-identical commitments. That can't build, pass `check` and verify untimed before 8:10, and CPU fill freezes during your 15:00Z window.
- **What a cut needs:** 2.9× needs 0.63 ms off run 5's 22.28 ms step, which is 10% of its 6.03 ms of hashing. Fusing the four small A-tree and tree kernels (seed, node keys, small tree, message) is the first candidate. I'll stage it as a ship change after the morning, if you want it.
- **If window 2 fails** (a crash, a gate, or JIT), window 3 reruns bdedc145 as is: START at 15:30Z, verified by 15:55Z.
