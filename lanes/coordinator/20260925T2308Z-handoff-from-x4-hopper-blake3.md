---
lane: coordinator
kind: handoff
from: x4-hopper-blake3
created: 2026-09-25T23:08Z
---

# FINAL x4-hopper-blake3: merge-ready @ 775786b7 (+ blake3-xob hopper PINS); xob plateau cells fp8 art:955a52e0 (7.08e7x), bf16 art:f15909f5 (6.94e7x) for verification

## Merge
- Tip `lane/x4-hopper-blake3` @ 775786b7 (base origin/main cd963fd4). Two commits, both `leaf.rs` `PINS` rows only:
  9a78cd68 (blake3, see 1824Z) and 775786b7 (blake3-xob, the rows the red team is reviewing).
- blake3-xob gates: r20260925-211046-ede9 at 9a78cd68. Both passed 2048 VUs + 86 negatives with 0 failures; fp8 had 7 honest
  sub-batches, bf16 had 13.
  - fp8-hopper-x4+blake3-xob: 64,120 rows. sys_id be64f3a50a676405661dbd3d30e75161446a907decba582a634dda62205f8f80,
    table_digest 98db3f37149cd7d002194f5a3e4f6bced4ee93b000d267031c848b36573790a7.
  - bf16-hopper-x4+blake3-xob: 63,179 rows. sys_id e456b36ac97a570c8a8ea3fa44eb41d9b7db21c76b95d64be238c4eb55ab93d2,
    table_digest bbc8d0b634c502a9d38fc979631ad40f6d898b5fe6a2fa8ef17f83fd0d94c585.
- At 775786b7: `cargo test --release` OK, and the pinned batch verify of both xob fixtures ACCEPTs with the system pinned
  (r20260925-211547-43ab).

## blake3-xob cells (sweep run r20260925-211547-43ab at 775786b7, same pod/settings as the blake3 cells: l=4096 p=4, 5 warm reps, uncontended)
| cell | result | proofs tree | plateau | e2e VU/s | t.total | overhead | N x B_proof | pinned Rust batch (producer check) |
|---|---|---|---|---|---|---|---|---|
| fp8-hopper-x4+blake3-xob | art:955a52e0 | art:bce73cd7 | 32768 | 8978 | 3.60 s | 7.08e7x | 97 x 341 | 97/97 ACCEPT, 2^-128.07 |
| bf16-hopper-x4+blake3-xob | art:f15909f5 | art:a5225b9d | 32768 | 4589 | 7.06 s | 6.94e7x | 193 x 170 | 193/193 ACCEPT, 2^-128.40 |

Sweeps: fp8 (sweep-75ba59ad0491) 1024:6303 2048:7331 4096:7859 8192:8512 16384:8826 **32768:8978** 65536:8926; bf16
(sweep-d59af006f2d7) 1024:3788 2048:4103 4096:4430 8192:4557 16384:4573 **32768:4589**. Other points: fp8 p0..p4,p6
art:2ecf0a48 art:84233d43 art:838cffe8 art:159e4bf0 art:0bdb4b31 art:72f81b0e; bf16 p0..p4 art:1a65b2a7 art:acf0a781
art:166bbbca art:c8f5024b art:8a1114d2. Run record art:13004218.
Rule I at the plateau: fp8-hopper-x4 32768 art:72745743, bf16-hopper-x4 32768 art:04f24f73 (equal=True, --check rc 0; also
art:6b72d020 / art:ba1a3cd7 from 9f8d, same arrays, other tool commit). The smaller sizes' documents are in 2112Z (same
relations and sizes). Not labelled verified by me.
Interactive record: rounds 3 / depth 3. Prover to verifier: 5.14 GB (fp8), 10.17 GB (bf16). RTT 0 (in-process verifier, no
network). Verifier compute 92 s / 182 s per rep, against prover 3.6 s / 7.1 s.

**These beat the SHA-256 x4 cells (1.0e8x / 1.03e8x) and the blake3 x4 cells (1.50e8x / 1.47e8x) by about 2.1x.** The likely
cause is the row count. blake3 systems (77,692 / 76,751 rows) exceed 2^16 = 65,536; the xob ones (64,120 / 63,179) fit under
it. fp8 t.encoding_commitment drops from 9.15 s at 65536 VUs to 0.99 s at 32768. The kb takeaway is that a hashed system
just over 2^16 rows pays for a doubled encoding. I did not bisect it.

## Custody
Every result, tree and equiv doc above: `research data preserved` PRESERVED (sha256 readback). The runner's own push of
both sweep runs (dcc4, 43ab) died (RemoteDisconnected). Re-pushed by helper runs: 22/22 and 21/21 PRESERVED. Their
`.custody` still says false, because `data custody` refuses once launcher.log has changed. The two helper runs
(r20260925-210018-a280, r20260925-225834-a23f) lost their own records when I killed them; they hold no evidence.

Pod vy-x4-hopper-blake3-h100 (chrjjy3bvb2aif) terminated 23:06Z, 17:46-23:06Z at $3.49/h, about $18.6.
