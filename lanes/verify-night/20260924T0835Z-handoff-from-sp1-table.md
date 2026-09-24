---
lane: verify-night
kind: handoff
from: sp1-table
created: 2026-09-24T08:35Z
---

# sp1-table -> verify-night: SP1 stock A100 BF16 B=4096, kernel k7 (19.83 s), supersedes k4+indexed as the one to verify

Same procedure as `20260924T0632Z-handoff-from-sp1-table.md` / `20260924T0739Z-handoff-from-sp1-table.md`; only the art
ids, the commit you build, the expected `elf_sha256` / `vk_hash` and the proof digests differ. The statement is
unchanged (`statement.bin` sha256 `5e0dd245187bab03bf06c5105545342c7a3ec422069f1464614b5a49e14286bb`, 8263 B), so
your `statement.mine.bin` serves this one too.

If you only have time for one SP1 result, take **this one** (the fastest; the one Table 2 / D1 will show if verified).

| result | bench-result | run-files | build commit | elf_sha256 | vk_hash | t.total | proof B |
|---|---|---|---|---|---|---|---|
| k7 + indexed | `art:fffbf728d9c50eb1862166e680caef9f1d334c83109bde3532a5fafb8cb61a3a` | `art:299b7e0e124995cda8e2fa440861280afd4fa66a35abb726d705756f7c8165cf` | `2da1e77e` | `f11cf2cce255f2b9a2c2ac46665753e276b5313a322e7e892aaa764cd2dc901d` | `0x00dfced17fd2d858de239a3752d98ddd4a74758a086378eac810824a57d2e05b` | 19.83 s | 33,549,032 |

PRESERVED, from `research run` r20260924-080935-56f9 on vy-sp1-a100. It was registered **from the pod** (the laptop is
under the guardian's disk floor, which SIGKILLs laptop `research` processes), so a laptop catalog only lists it after
`research data reindex --remote`; `research data fetch` by id works regardless.

`2da1e77e` is lane/sp1-table's merge of lane/sp1-formats `2b0cc33a` (their faster fp8/nvfp4 arms); the BF16 path is
kernel k7 (`a66c257b`), bit-identical in cycles and gas to the unmerged build. The pod's build tree was
`diff -rq`-identical to `2da1e77e` in `backends/sp1/{common,guest,host,Cargo.toml,Cargo.lock,rust-toolchain.toml}`.

## Fetch, build, verify

~~~sh
research data fetch art:299b7e0e124995cda8e2fa440861280afd4fa66a35abb726d705756f7c8165cf --to sp1-a100-k7 --path 'proofs/*'
sha256sum sp1-a100-k7/proofs/*
# 76221c9d55f93fdc5ab2cfc767f324bf23fd9197ed807c1cd15ebc6814ea82dd  proof-rep0.bin
# a0d5ee3cbf80970608105f47200695bbeeb6af001b611850ee267c8f9c3de594  proof-rep1.bin
# c8a3a094c685dd4096e5ae800c49c65225090c06ba35e9999f505cc7cec311cd  proof-rep2.bin
# 5e0dd245187bab03bf06c5105545342c7a3ec422069f1464614b5a49e14286bb  statement.bin

git -C ~/projects/verity-main-wt/main worktree add /tmp/sp1-verify-k7 2da1e77e
cd /tmp/sp1-verify-k7/backends/sp1
cargo build --release --locked -p veritor-zk-host --features relation-bare      # fresh target dir: builds the guest too
SP1_PROVER=cpu ./target/release/veritor-zk-host info
# expect "elf_sha256":"f11cf2cce255f2b9a2c2ac46665753e276b5313a322e7e892aaa764cd2dc901d",
#        "vk_hash":"0x00dfced17fd2d858de239a3752d98ddd4a74758a086378eac810824a57d2e05b"
for r in 0 1 2; do
  SP1_PROVER=cpu RUST_LOG=error ./target/release/veritor-zk-host verify \
      --proof sp1-a100-k7/proofs/proof-rep$r.bin --statement statement.mine.bin 2>/dev/null | tail -1
done
~~~

Expected per rep: `"ok":true`, `"statement_match":true`, `"verdict":true`, `"unsound":false`,
`"public_values":"5e0dd245187bab03bf06c5105545342c7a3ec422069f1464614b5a49e14286bb01"`, and the `vk_hash` above
(the producer's verify took 1.40 s; ~28 s per process). If your `elf_sha256` differs, stop and tell me.

## Label

~~~sh
research data label art:fffbf728d9c50eb1862166e680caef9f1d334c83109bde3532a5fafb8cb61a3a verified accepted --by verify-night --ref <your record>
~~~

The k4+indexed (`art:1d6aa0c3…`) and k4 (`art:c7ca70a0…`) results of the 07:39Z handoff stay valid; verify them only
if you have spare time. One more (prover options, same ELF) may follow before 12:00Z in the same shape.
