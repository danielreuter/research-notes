---
lane: verify-night
kind: handoff
from: sp1-formats
created: 2026-09-24T07:42Z
---

# sp1-formats -> verify-night: the same four SP1 cells, re-proved from the faster guest at 3510cfcf (B=4096 each)

This follows up my 07:12Z handoff (`20260924T0712Z-handoff-from-sp1-formats.md`). The steps are the same, with a
different commit, ELF and vk. The statement bytes are unchanged: each run's `statement.bin` has the same sha256 as in
the 07:12Z note. Only the guest's arithmetic kernels changed (cycles per VU), so the same step-2 statements verify these
proofs. All artifacts below are PRESERVED (`research data preserved` exit 0).

| row (format id) | bench-result/v1 | run-files/v1 | device | t.total | shards | proof B |
|---|---|---|---|---|---|---|
| RTX 4090 FP8 `fp8-ada` (4) | `art:8d9df3a20d31aca4ec3301a10cd9b3ea74b53add880de41acceb4c9b39f95af5` | `art:8f3a4cfc4008dab6c8970f438819ef877a719d9859635aa7f9cb394dc5448602` | RTX 4090 | 23.53 s | 36 | 54,088,700 |
| H100 FP8 `fp8-hopper` (3) | `art:70e5bd294c3b3e4a47490aea70ff6a9cf0f663fe3107563a9c263e92c94084b5` | `art:4d63c3571dc0f3b14daacd7711cc68097dcb88f220e916e952f4458152596a0f` | H100 80GB HBM3 | 20.74 s | 24 | 36,651,092 |
| H100 BF16 `bf16-hopper` (2) | `art:76d13bb0611579ef087bc2cfe6ac7fbee9ba05a283e66eb060b4c0172b800508` | `art:0cabdd776e842e76b181c7807120510e244357e14ec139863911774edd6537e0` | H100 80GB HBM3 | 24.09 s | 30 | 45,631,224 |
| RTX 5090 NVFP4 `fp4-nvf4` (5) | `art:a8886e22488d2eb3ea0ece0ba3661c11459b7e372bc95d481eaa3066ceac1bd1` | `art:5bd375d2c6a868452f7812d9787fef59e1e0fd6fa203a2a54a89db60cd81f9a8` | RTX 5090 | 7.43 s | 14 | 21,195,336 |

The Table 2 reasons are the same as before: SP1's 100-bit target (achieved −94.83, −95.42, −95.09, −96.19 after the
union bound over shards) and "not independently verified".

## 1. Fetch

~~~sh
research data fetch art:8f3a4cfc4008dab6c8970f438819ef877a719d9859635aa7f9cb394dc5448602 --to fp8-ada     --path 'proofs/*'
research data fetch art:4d63c3571dc0f3b14daacd7711cc68097dcb88f220e916e952f4458152596a0f --to fp8-hopper  --path 'proofs/*'
research data fetch art:0cabdd776e842e76b181c7807120510e244357e14ec139863911774edd6537e0 --to bf16-hopper --path 'proofs/*'
research data fetch art:5bd375d2c6a868452f7812d9787fef59e1e0fd6fa203a2a54a89db60cd81f9a8 --to fp4-nvf4    --path 'proofs/*'
sha256sum */proofs/*
# fp8-ada     36e1f5da0f2f8d99327abf54d750364998de76fe081e1c53e3c871e6e00db811 proof-rep0.bin
#             95daa31b3b37257c6c231e1f37f3ae57efefd1f15719e90c6e56bc135e967b62 proof-rep1.bin
#             e6fe9db5989749d17e5f88a10c1eee90c18b3bf779d0b48dbc11954311a2b2eb proof-rep2.bin
#             bef41cb5433fa4a6e6c8166c7445bd80d9e19d53a77e846a217a64246198bd28 statement.bin (16455 B, as at 07:12Z)
# fp8-hopper  e16f9b90b13d1e1ff49bc68ec54dd3a4fcf2dde5a7c6762c553e8201a98f798b proof-rep0.bin
#             dc99486d81ee46d4f4e8b6865bd8a16eb4ff26064ada714bb9ee8cd137d1c2a3 proof-rep1.bin
#             894f82088b4f3911df424596781a6a5717a37d045c0351e568075b4f73f4d1db proof-rep2.bin
#             302a2d61422e6267677054e43a7ce36ab462c2d1af880f9fe7ec44e94d629783 statement.bin (16455 B, as at 07:12Z)
# bf16-hopper b322be7e36328aca985097fa84e7d32147071e56320c9cc24e6f46bcf117be42 proof-rep0.bin
#             f2888868316b188c01e3e72d5b26b1e2f0f375d7538821f490e7f10651a894dc proof-rep1.bin
#             6d6e62cac03260ca483923d4ad472012c2587fc40f66353a349675fc029f3a63 proof-rep2.bin
#             2aba4b68852af391dd22e25eadbcc52b9e4f1662960f31791acf3ce389c71179 statement.bin (8263 B, as at 07:12Z)
# fp4-nvf4    3761268b7b4e38807baa26bee3ba7b874148c1ae5c7452d0be006da9fe1852c1 proof-rep0.bin
#             419b172ddc3457563e27a8508731c187cb884cd71b6784e8f69fd0c38e806398 proof-rep1.bin
#             34c8ffb3fca9fb8134e5dd5dd5fd35c7b9cfd88fb8c2b3455115f857ba48768e proof-rep2.bin
#             e247d4903d9eddd27dae2b12eb9f58707b6c0edc8851cb551caeb270c2705cf7 statement.bin (16455 B, as at 07:12Z)
~~~

## 2. Statements

These are the step-2 statements from the 07:12Z note, unchanged. If you already wrote `<fmt>.mine.bin`, reuse it.

## 3. Build the verifier at 3510cfcf

`3510cfcf` = `2581406f` + one commit touching only `common/src/{groupsum,tc_fp8,nvfp4,bare}.rs`: the fp8 and nvfp4
kernels, and the nvfp4 arm now passing both views. Build it the same way, in a fresh target dir:

~~~sh
git -C ~/projects/verity-main-wt/main worktree add /tmp/sp1f-verify-3510 3510cfcf
cd /tmp/sp1f-verify-3510/backends/sp1
CARGO_TARGET_DIR=/tmp/sp1f-verify-3510/target cargo build --release --locked -p veritor-zk-host --features relation-bare
SP1_PROVER=cpu /tmp/sp1f-verify-3510/target/release/veritor-zk-host info
# expect "elf_sha256":"48bb5913616779ac7d6149ff94548dbb9a3f5ffe4adf2ef4f1a82118be3c783a",
#        "vk_hash":"0x00a42aa336fca4dcddeb8c001f4ee90fed545d5fc9e51a492990f3e45f25a599", "guest_features":["relation-bare"]
~~~

The same caveat applies: I built with `--features cuda,relation-bare` (host sha256 `9b36a54e…`). If the CPU build's
`elf_sha256` differs, report that as a reproducibility finding, not as a rejection.

## 4. Verify (twelve proofs)

~~~sh
H=/tmp/sp1f-verify-3510/target/release/veritor-zk-host
for f in fp8-ada fp8-hopper bf16-hopper fp4-nvf4; do for r in 0 1 2; do
  SP1_PROVER=cpu RUST_LOG=error $H verify --proof $f/proofs/proof-rep$r.bin --statement $f.mine.bin 2>/dev/null | tail -1
done; done
~~~

The acceptance rule is the same as before, except that `vk_hash` must be `0x00a42aa3…a599`. The producers'
`verify_seconds` were 2.59 s (fp8-ada), 1.20 s (fp8-hopper), 1.63 s (bf16-hopper) and 0.62 s (fp4-nvf4). A flipped `y`
byte in a `.mine.bin` must give `statement_match` false.

## 5. Label

~~~sh
research data label <bench-result art> verified accepted --by verify-night --ref <your record>
~~~

If you have time for only one set, take this one: it supersedes the 07:12Z cells as the headline SP1-stock numbers for
these rows. Both sets stand on their own.
