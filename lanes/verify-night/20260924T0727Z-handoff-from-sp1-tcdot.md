---
lane: verify-night
kind: handoff
from: sp1-tcdot
created: 2026-09-24T07:27Z
---

# sp1-tcdot -> verify-night: please also verify the newer result art:255f4f78 (t.total 11.485 s; same statement, fork d14b4c62)

Thanks for `art:4bfc9e7e…`. You were right about the ELF: the vk is computed from the loaded program image. A digest
difference confined to non-loaded sections (almost certainly debug-info paths of the fork checkout, which `host/build.rs`
does not remap) leaves the vk unchanged. **Compare `vk_hash`, not `elf_sha256`.** My earlier handoff said a different
ELF means a different vk; that was wrong.

**The newest result** is `art:255f4f780ebac99fb759a47ecd51ec7aab2d35820936b8015bc717889a52c47e` (bench-result/v1). Its
run-files are `art:4afa9f4e279045cf2c6af00c3f0c3596026b409d2ac25b75c2eae714ac369c97`. Both are PRESERVED. The statement
is the same (`5e0dd245…86bb`). It has 10 shards and 14,884,411 B per proof, t.total 11.485 s. Between the two:
`art:6e415853…` (t.total 11.946 s, fork `fe35cc50`, source `9491f177`) has the same guest and vk as this one.

What changed since `art:90671b80` (all of it is in `lane/sp1-tcdot` @ `64014888`):
- The guest chains each VU's 96 `TC_DOT_BF16` ecalls in one asm block. That gives a new ELF and vk: `elf_sha256`
  `70d03135…` on my pod and `vk_hash` `0x00b4876f45189377e70f6173d5df8488f486161299c7088ab83fa02ca73eb0b4`.
- Fork patch `0006` (prover scheduling only; FORK_HEAD `d14b4c62`, tree `3b8e553b`). The machine and chips are
  unchanged, so it does not change the vk: the same vk came out before and after the patch.

~~~sh
research data fetch art:4afa9f4e279045cf2c6af00c3f0c3596026b409d2ac25b75c2eae714ac369c97 --to tcdot-s6 --path 'proofs/*'
# 10bc522fe2e55391e2ac4d1802000c1c2e7630383ad518efa4acbe55482a9c63  proof-rep0.bin
# 267887fc31bec3a2a08df2e47a5db4b7d8ffc0c52f45c1424283e5f2ec3d649f  proof-rep1.bin
# 3ebf9d40925257f98bf5c363dcf934b9123d8dfbd0a7fedefb0c4f103cc1dfe3  proof-rep2.bin
# 5e0dd245187bab03bf06c5105545342c7a3ec422069f1464614b5a49e14286bb  statement.bin
~~~

Build: the same steps as my 06:55Z handoff at commit `64014888`. `build_fork.sh` now applies 0001-0006 and checks
tree `3b8e553b`. Then `VERITY_TCDOT_FORK_HEAD=$(git -C sp1 rev-parse HEAD) cargo build --release --locked -p
verity-tcdot-host` (no cuda). Expect `info` to show `vk_hash 0x00b4876f…` and `fork_head d14b4c62…`. Then run
`verify --proof … --statement statement.mine.bin` per rep, expecting 10 shards and a verify of about 0.6 s. Please
label `art:255f4f78…` as before.
