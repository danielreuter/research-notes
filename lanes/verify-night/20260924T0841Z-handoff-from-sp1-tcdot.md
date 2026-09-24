---
lane: verify-night
kind: handoff
from: sp1-tcdot
created: 2026-09-24T08:41Z
---

# sp1-tcdot -> verify-night: please verify art:174d7b4d (t.total 5.811 s), built from the witness-operands fork

**The newest result** is `art:174d7b4d7269742dfdfb3749f951b2d80484d4e99a8c66fa04f203baef5c5fd8` (bench-result/v1).
Its run-files are `art:ff5eaf2ad385335a6c038e1f751f1ff609b5d0a86eb341cb8444b127d4895af7`. Both are PRESERVED.

- Same statement as before (`5e0dd245…86bb`).
- 8 shards and 11,393,879 B per proof; t.total 5.811 s.
- Source `lane/sp1-tcdot` @ `0742a046`, fork `6096d886` (tree `136b65c4`).

**Important: this is a different AIR from the proofs you verified, and the vk does not show it.** SP1's `vk_hash`
commits to the program (the preprocessed traces of the ELF), not to the chips' constraints. The chips are compiled into
the verifier binary.

- These results come from the fork's witness-operands arm (`FORK_HEAD_WIT`, patches `witness-operands/0007-0009`). Its
  TC_DOT_BF16 chip has no memory reads for its operands: the 16+16 BF16 operands of each step are free witness
  columns, range-checked as BF16. The accumulator word is still read and written through memory.
- A proof therefore shows each claimed y word is reachable by chaining the VU's 96 exact tc-ampere-bf16 steps from
  some finite BF16 operands. That is sound for relation-bare (existential in x and W), not for a statement that
  authenticates x and W. The coordinator asked for this arm at 07:45Z.
- Hill-climb 3 (`art:a68f2446…`) shows the vk trap: it carries the same `vk_hash` `0x00b4876f…` as `art:255f4f78`
  (memory arm), yet its AIR differs.
- **Please build the verifier from the witness fork and put the fork pin (`6096d886`) in your verdict**, so the label
  says which AIR was checked. A memory-arm verifier (`d14b4c62`) should reject these proofs on shape.

~~~sh
research data fetch art:ff5eaf2ad385335a6c038e1f751f1ff609b5d0a86eb341cb8444b127d4895af7 --to tcdot-m1 --path 'proofs/*'
# 395b5a09260f0b515a8e6a141b37d3c31aaaaf6efd810e9b6d050e9539d5b300  proof-rep0.bin
# d55e7174e280b13a1ceffcddfb48f5d5c3104b00e54a1d2345b36c233cfc0fe5  proof-rep1.bin
# 13f74250422cce8a3d89ded12eba7bd3f95581acee33fe56f2efe7f3420927b8  proof-rep2.bin
# 5e0dd245187bab03bf06c5105545342c7a3ec422069f1464614b5a49e14286bb  statement.bin

# CPU pod, verity source at 0742a046:
OPERANDS=witness SKIP_SERVER=1 SP1_TCDOT_ROOT=/workspace/tcdot-verify bash backends/sp1/tcdot/build_fork.sh
#   upstream v6.4.0 f66b4bff + 0001-0006 + witness-operands/0007-0009; fails unless tree = 136b65c4 (HEAD 6096d886)
cd backends/sp1/tcdot
VERITY_TCDOT_FORK_HEAD=$(git -C sp1 rev-parse HEAD) cargo build --release --locked -p verity-tcdot-host --features stream-operands
#   no cuda; stream-operands builds the guest whose TC_DOT_BF16 VUs take their operands from stdin
target/release/verity-tcdot-host info
#   expect vk_hash 0x00896ef46d917e41bd6f29ef3f4504676f1bccffe2c10936a150113a9ca49384, operands stream, fork_head 6096d886…
#   (elf_sha256 525841da… on my pod; compare the vk, not the ELF)
target/release/verity-tcdot-host verify --proof proof-rep0.bin --statement statement.mine.bin   # per rep; 8 shards
~~~

**The same host also verifies hill-climb 4**, `art:76c113f47347b6b1dd64395acb055fe8734f712cbbcfd08a00fd8c8fbf9ec985`
(runs `art:44bded3a6418aecb7cba8eb2ac297fc8d1b5671b739c32034bb48e1a2d8f8dee`; t.total 5.923 s, fork `e3756374`,
source `b189a963`). It has the same guest, ELF and vk.

- Patch 0008 changes only the executors: operands are popped from stdin and replayed.
- Patch 0009 changes only how the prover assembles a precompile shard's record: runs of calls on one accumulator word
  share one local memory event. A wrong merge would unbalance the memory bus and the proof would not verify.
- Neither patch touches a chip or the verifier.
- Hill-climb 4 proof digests: `d81dfb46…783e`, `12bfc8a1…d6b3`, `79a2cc29…0d12`.

Hill-climb 3 (`art:a68f2446…`, runs `art:204f58d0…`, 8.771 s) is lower priority. It needs its own host at source
`d3a5b955` (fork `cbf66ccd`, patch 0007 only, built without `stream-operands`, vk `0x00b4876f…`).

Please label `art:174d7b4d…` first, then `art:76c113f4…`.
