---
lane: x4-hopper-blake3
kind: report
created: 2026-09-25T17:43Z
status: open
---

CHECKPOINT 775786b7 (21:16Z) [open] cells art:d88a9948 fp8 1.50e8x @65536, art:5ea60c40 bf16 1.47e8x @16384 (+14 equiv docs) handed off 2112Z; xob PINS 775786b7; xob sweeps r20260925-211547-43ab running, polling in-turn
CHECKPOINT 9a78cd68 (20:01Z) [open] fp8-hopper-x4+blake3 sweep done: plateau 65536 at 4271 VU/s (~1.5e8x vs 1978.9T; slower than sha256 x4's 6162), pinned Rust 193/193, equiv equal=True; bf16 sweep running (r20260925-182011-dcc4)
CHECKPOINT 9a78cd68 (19:44Z) [open] fp8-hopper-x4+blake3 sweep at p7 131072 (e2e ~4.2-4.4k VU/s from 32768 on; in-process verifier ~400 s/rep dominates wall); bf16 sweep next; polling in-turn r20260925-182011-dcc4
CHECKPOINT 9a78cd68 (18:22Z) [open] WAITING r20260925-182011-dcc4 on vy-x4-hopper-blake3-h100 (pinned sweeps fp8/bf16-hopper-x4+blake3 l4096 p4 from 1024 + equiv), check after 19:30Z; agent bc-4c84a7da-0134-54f4-a563-e23117bb6a32; done: PINS 9a78cd68 pushed, merge-ready handoff 1824Z; next: verification handoff
CHECKPOINT cd963fd4 (17:50Z) [open] WAITING r20260925-174812-50ad on vy-x4-hopper-blake3-h100 (bootstrap OK; fixtures+gates fp8/bf16-hopper-x4+blake3), check after 18:40Z; agent bc-4c84a7da-0134-54f4-a563-e23117bb6a32; next: PINS rows commit, then 20-pinned-sweeps.sh
CHECKPOINT cd963fd4 (17:46Z) [open] pod vy-x4-hopper-blake3-h100 (chrjjy3bvb2aif, H100 80GB HBM3 ref part) created+registered guard 60; next: sync + bootstrap, then 10-pins-gates LEAF=blake3 RELS='fp8-hopper-x4 bf16-hopper-x4'
CHECKPOINT cd963fd4 (17:43Z) [open] started: branch lane/x4-hopper-blake3 at cd963fd4; reading contract, pod scripts; no pod yet; agent bc-4c84a7da-0134-54f4-a563-e23117bb6a32
