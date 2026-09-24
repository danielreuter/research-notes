---
lane: verify-night
kind: handoff
from: sp1-tcdot
created: 2026-09-24T09:54Z
---

# sp1-tcdot -> verify-night: please verify art:0a66c35e (t.total 4.258 s); new AIR, same vk as before

**The newest result** is `art:0a66c35ead22d93f72e178fa275462ec9d9b711349fccb12b1eb0c8a6c9ff4ae` (bench-result/v1).
Its run-files are `art:2dc0261c6f7393018520b44f842564eed593da2a91efd258ee439e9afc704c2e`. Both are PRESERVED.

- Same statement as before (`5e0dd245…86bb`).
- 8 shards and 11,480,593 B per proof; t.total 4.258 s.
- Source `lane/sp1-tcdot` @ `97b5b60a`, fork `6655716e` (tree `4ca5a6ca`), witness-operands arm (patches
  `witness-operands/0007-0011`).

**The AIR changed again, and the vk still does not show it.** `vk_hash` is `0x00896ef4…` as in the 08:41Z handoff,
but patch 0010 widened TC_DOT_BF16 from 1166 to 1173 columns:

- Subnormal GroupSum outputs are now constrained on the chip (denormalized as `tc::group_sum` does) instead of being
  outside its contract.
- On the frozen set, only 64 overflow steps remain in software, and no VU runs whole in software. Guest cycles fall
  from 3.74M to 0.86M.
- Patch 0011 changes only the prover (TcDotBf16's trace and byte lookups are generated in parallel).
- **Please build the verifier at `6655716e` and put that pin in your verdict.** A verifier built from `6096d886` (the
  08:41Z handoff) should reject these proofs on shape. I expect this but have not run it.
- I checked the positive side on the pod: the `6655716e` host verifies rep 0 of `art:0a66c35e` and of hill-climb 6
  `art:b147a31c` (ok, statement_match, verdict true, 8 shards, about 0.5 s).

~~~sh
research data fetch art:2dc0261c6f7393018520b44f842564eed593da2a91efd258ee439e9afc704c2e --to tcdot-p11 --path 'proofs/*'
# ca12c3ff46ff551304be3c21aba3a0477cf9410fbb4937fda30c737d0984629a  proof-rep0.bin
# 7c67d92dd1ff1cb6267d49ed983070f195444235c0e66ca101928a92b0e603d1  proof-rep1.bin
# f3881793ee2b4a5fe088cf8139a04048c502dd6c7a92ec8c2f8e317671e16dc4  proof-rep2.bin
# 5e0dd245187bab03bf06c5105545342c7a3ec422069f1464614b5a49e14286bb  statement.bin

# CPU pod, verity source at 97b5b60a:
OPERANDS=witness SKIP_SERVER=1 SP1_TCDOT_ROOT=/workspace/tcdot-verify bash backends/sp1/tcdot/build_fork.sh
#   upstream v6.4.0 f66b4bff + 0001-0006 + witness-operands/0007-0011; fails unless tree = 4ca5a6ca (HEAD 6655716e)
cd backends/sp1/tcdot
VERITY_TCDOT_FORK_HEAD=$(git -C sp1 rev-parse HEAD) cargo build --release --locked -p verity-tcdot-host --features stream-operands
target/release/verity-tcdot-host info
#   expect vk_hash 0x00896ef46d917e41bd6f29ef3f4504676f1bccffe2c10936a150113a9ca49384, operands stream, fork_head 6655716e…
target/release/verity-tcdot-host verify --proof proof-rep0.bin --statement statement.bin   # per rep; 8 shards
~~~

**The same host verifies two more results.** Neither changes the AIR from `6655716e`: 0011 is prover-only, and
0e00bd15 is 0010 alone.

- Hill-climb 7: `art:2a4760fb9a7c02fadd45d25fc01153cb65cdc30c85dcad2269174b0b18087fc3`, runs
  `art:4b3dc262d6111854dcc39697ca4f525be53dd2a2163d8ad6901805c46106e2bb`. t.total 4.980 s, fork `6655716e`, source
  `97b5b60a`. Proof digests `40c1e6fb…4d7b`, `5a4c6d0e…6b43`, `25d1098f…4dd`.
- Hill-climb 6: `art:b147a31c70cd6d13e2f4bc382738c93d1e53bccd1d78901d9e00110c018c30ef`, runs
  `art:ee9b4fdf0e4615c74760bc39ee592bd2c241ecda8f0e8992274bb9bb76d1abcd`. t.total 5.631 s, fork `0e00bd15` (tree
  `fe0715de`), source `ca647373`. Proof digests `43f845f0…a237`, `b51ca524…a240`, `d4b00ea9…e9ee`.

Please label `art:0a66c35e…` first. Hill-climbs 5 and 4 from the 08:41Z handoff still need the `6096d886` host.
