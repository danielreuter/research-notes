---
lane: verify-night
kind: handoff
from: sp1-table
created: 2026-09-24T09:06Z
---

# sp1-table -> verify-night: SP1 stock A100 BF16 B=4096, k7 warm run (18.52 s): the one to verify

This supersedes the "take this one" of `20260924T0835Z-handoff-from-sp1-table.md`. It is the **same build, ELF, verifying
key and statement** as that handoff (commit `2da1e77e`, `elf_sha256 f11cf2cc…`, `vk_hash 0x00dfced1…`, `statement.bin`
sha256 `5e0dd245…`), so if you already built the verifier from `2da1e77e`, only the fetch and the proof files differ.
The run differs only in protocol: one full B=4096 warm-up proof (excluded, recorded), then 5 reps, t.total = median.

| result | bench-result | run-files | build commit | elf_sha256 | vk_hash | t.total | proof B |
|---|---|---|---|---|---|---|---|
| k7 + indexed, warm | `art:7233a6a347b6dfffacb05548aff4c391c1def96dfd61343cf37016f48401c7ac` | `art:165503bae53d4fa217a19bf1a05d4cc3c9f702d7773e33a8a00c4f5f304b26e7` | `2da1e77e` | `f11cf2cce255f2b9a2c2ac46665753e276b5313a322e7e892aaa764cd2dc901d` | `0x00dfced17fd2d858de239a3752d98ddd4a74758a086378eac810824a57d2e05b` | 18.52 s | 33,549,032 |

PRESERVED, from `research run` r20260924-083738-0541 on vy-sp1-a100, registered from the pod (laptop catalog lists it
after `research data reindex --remote`; `research data fetch` by id works regardless).

Reproduced on the pod before handing off: a fresh `CARGO_TARGET_DIR` build of the committed tree `2da1e77e` (the research
source cache the run executed, not the benchmark's build dir), `--features relation-bare`, CPU prover, printed the
`elf_sha256` and `vk_hash` above, and its `verify --statement` accepted all 5 proofs (`ok`, `statement_match`,
`verdict` true, `unsound` false, ~1.40 s each).

## Fetch, build, verify

~~~sh
research data fetch art:165503bae53d4fa217a19bf1a05d4cc3c9f702d7773e33a8a00c4f5f304b26e7 --to sp1-a100-k7warm --path 'proofs/*'
sha256sum sp1-a100-k7warm/proofs/*
# 61317043982c9a52ac7c280d7b5262b75a95d862d8088b63c49a51e717ca3303  proof-rep0.bin
# 8fc6fa8522538ee4fe86caf7974e5e12927306af9b9aff4ec8d5ac1645f8fd14  proof-rep1.bin
# 05699ab98cfaefea80e86495f65f31079b535566174bfc0d41b6362f69c46aaa  proof-rep2.bin
# 53cbd1adbd35920bf9a948f24ba39b8351591e13a1e11ed223064e8540ce0af8  proof-rep3.bin
# 396d5f0863856b4d9021a222656dfbd34fd909d5f359e7338876499480d79341  proof-rep4.bin
# 5e0dd245187bab03bf06c5105545342c7a3ec422069f1464614b5a49e14286bb  statement.bin

git -C ~/projects/verity-main-wt/main worktree add /tmp/sp1-verify-k7 2da1e77e      # skip if you built it for 0835Z
cd /tmp/sp1-verify-k7/backends/sp1
cargo build --release --locked -p veritor-zk-host --features relation-bare
SP1_PROVER=cpu ./target/release/veritor-zk-host info       # expect the elf_sha256 and vk_hash above
for r in 0 1 2 3 4; do
  SP1_PROVER=cpu RUST_LOG=error ./target/release/veritor-zk-host verify \
      --proof sp1-a100-k7warm/proofs/proof-rep$r.bin --statement statement.mine.bin 2>/dev/null | tail -1
done
~~~

`statement.mine.bin` is the statement you reconstruct from the frozen set (procedure in `20260924T0632Z`); it must be
byte-identical to the fetched `statement.bin` (8263 B, sha256 `5e0dd245…`). Expected per rep: `"ok":true`,
`"statement_match":true`, `"verdict":true`, `"unsound":false`,
`"public_values":"5e0dd245187bab03bf06c5105545342c7a3ec422069f1464614b5a49e14286bb01"`, the `vk_hash` above.
If your `elf_sha256` differs, stop and tell me.

## Label

~~~sh
research data label art:7233a6a347b6dfffacb05548aff4c391c1def96dfd61343cf37016f48401c7ac verified accepted --by verify-night --ref <your record>
~~~

Verifying this one also covers `art:fffbf728…` (0835Z) in substance (same ELF, vk and statement); label that one only if
you verify its proofs too. This is sp1-table's last result: the stock prover options are exhausted (the GPU is saturated
after the first shard; the shard size is SP1's compiled `ELEMENT_THRESHOLD`) and the kernel is at this design's floor.
