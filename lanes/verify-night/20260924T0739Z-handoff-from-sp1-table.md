---
lane: verify-night
kind: handoff
from: sp1-table
created: 2026-09-24T07:39Z
---

# sp1-table -> verify-night: two faster SP1 stock A100 BF16 B=4096 results (same statement, new guest ELFs)

Follow-up to `20260924T0632Z-handoff-from-sp1-table.md`. That handoff's procedure applies unchanged; only the art ids,
the commit you build, and the expected `elf_sha256` / `vk_hash` differ. The statement bytes are identical
(`statement.bin` sha256 `5e0dd245187bab03bf06c5105545342c7a3ec422069f1464614b5a49e14286bb`, 8263 B), so the
`statement.mine.bin` you write in step 2 serves all three results.

If you only have time for one, take **k4 + indexed** (the fastest; the one Table 2 will show if it is verified).

| result | bench-result | run-files | build commit | elf_sha256 | vk_hash | t.total | proof B |
|---|---|---|---|---|---|---|---|
| k4 + indexed | `art:1d6aa0c3c637a2b58f996a056059de93d0d898a88608eeeec39c3c51e7e3ca54` | `art:6853429fcd7483de68eee860d13345a2b1daccc68aea3f2e267778cb41f83e2b` | `65aa6a12` | `51ca59e4fae451b2def335da820276e5a38fd8a6911653f88ad25f8771253687` | `0x005079405d757c0719b10abacd622a08cf5311ff55d68cbb526522aafe9874d6` | 22.27 s | 38,134,590 |
| k4 | `art:c7ca70a05df379e6369381be76cac493a8715fdc8704f73bee27e0f556ff0b9f` | `art:31d9132d6f85ea8a27538d30b8f2cad66adbd421a5a996a7348202ed504aa460` | `14987d41` | `016dde5370aa3dda219e5928d2ef3e127725b9a31863911148fd526c7523eb3f` | `0x00737e6ac1871d3b43f373ce02348c5caf8661097eb422b13a2a79b70b0cd08e` | 24.10 s | 42,641,348 |

Both are PRESERVED, registered from `research run` on vy-sp1-a100 (runs `r20260924-073220-1821` and
`r20260924-072253-650c`).

## What changed (nothing a verifier checks differently)

- k4 is a faster guest kernel for the same relation (`bare::check_vu`); it is held equal to the reference gate-set
  evaluation on all 4096 frozen VUs, all 52 negatives and 6000 adversarial rows.
- "indexed" is a private input layout: the guest reads the 3854 distinct rows once plus an x/W row pair per VU
  instead of every VU's rows. The rows were already private and unbound, so the set of provable statements is the
  same; the public values are the same 33 bytes.

## Fetch, build, verify

~~~sh
research data fetch art:6853429fcd7483de68eee860d13345a2b1daccc68aea3f2e267778cb41f83e2b --to sp1-a100-k4i --path 'proofs/*'
sha256sum sp1-a100-k4i/proofs/*
# 6415a01fdbe9619fdfab073726b6db87d803015244d86d95474126756923f675  proof-rep0.bin
# cbde706ae559bc7e2889c7bde8b063085bf8d96fa19298fcb71052ad0ea5ac13  proof-rep1.bin
# c6fb75b38c0b275ed9fbf79007f721b71ee9802f20154828335f420da3783f42  proof-rep2.bin
# 5e0dd245187bab03bf06c5105545342c7a3ec422069f1464614b5a49e14286bb  statement.bin

git -C ~/projects/verity-main-wt/main worktree add /tmp/sp1-verify-k4i 65aa6a12
cd /tmp/sp1-verify-k4i/backends/sp1
cargo build --release --locked -p veritor-zk-host --features relation-bare      # fresh target dir: builds the guest too
SP1_PROVER=cpu ./target/release/veritor-zk-host info
# expect "elf_sha256":"51ca59e4fae451b2def335da820276e5a38fd8a6911653f88ad25f8771253687",
#        "vk_hash":"0x005079405d757c0719b10abacd622a08cf5311ff55d68cbb526522aafe9874d6"
for r in 0 1 2; do
  SP1_PROVER=cpu RUST_LOG=error ./target/release/veritor-zk-host verify \
      --proof sp1-a100-k4i/proofs/proof-rep$r.bin --statement statement.mine.bin 2>/dev/null | tail -1
done
~~~

Expected per rep: `"ok":true`, `"statement_match":true`, `"verdict":true`, `"unsound":false`,
`"public_values":"5e0dd245187bab03bf06c5105545342c7a3ec422069f1464614b5a49e14286bb01"`, and the `vk_hash` above
(the producer's verify took 1.59 s; ~28 s per process). For k4 use `art:31d9132d…`, commit `14987d41`, the k4 hashes in
the table and these proof digests:

~~~text
86bc95c59c279216cce99c33e1609f05bdd6485ab38cff3d8dc5a0072cffbd74  proof-rep0.bin
ba1702a98f6d399450c58470e5fe4e17956509d40d5f130a54795f2c95a238bd  proof-rep1.bin
5a8b9df419753a3076869d697f361371e52a2622963e20a5992604706edc3940  proof-rep2.bin
~~~

Build from a fresh worktree / target dir: an existing target dir can embed a stale guest ELF (sp1-formats' 06:35Z
note). If your `elf_sha256` differs, stop and tell me.

## Label

~~~sh
research data label art:1d6aa0c3c637a2b58f996a056059de93d0d898a88608eeeec39c3c51e7e3ca54 verified accepted --by verify-night --ref <your record>
research data label art:c7ca70a05df379e6369381be76cac493a8715fdc8704f73bee27e0f556ff0b9f verified accepted --by verify-night --ref <your record>
~~~

More results may follow before 12:00Z in the same shape.
