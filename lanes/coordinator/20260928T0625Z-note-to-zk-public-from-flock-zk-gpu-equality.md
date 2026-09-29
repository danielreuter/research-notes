---
cursor:
  subagentId: "bc-2a9978cc-cafd-5d88-a4de-888a71d85659"
---

lane: flock-zk · kind: note · to: the public-circuit ZK proof (bc-b483c71e) · 2026-09-28 06:25Z · follows
`20260928T0520Z-note-to-zk-public-from-flock-zk-gpu-port.md`

# The GPU `--zk` path passes the differential test

**The device prover gives the CPU prover's proofs and transcripts byte for byte.** It was run for equal seeds and verifier
coins, `gpu_proofs_match_cpu` in `selftest --zk --gpu`, on an RTX 4090 at [PR #229](https://github.com/danielreuter/verity/pull/229)
`623ce3e9`:

| statement | proof per rep | proofs equal | transcripts equal |
|---|---|---|---|
| RoPE, m = 25 | 865,130 bytes | yes | yes |
| GEMM k1536, m = 26 | 836,306 bytes | yes | yes |

- **Nothing in the prover moved after my earlier note.** The fixes before this run were a pointer lifetime in the device
  call, a build flag, and the test harness's witness choice for the dummy-witness case.
- **Your §2.8 row 9** can read: a GPU path exists and is held to the CPU prover's bytes by `gpu_proofs_match_cpu`, which
  closes gap 4 through gap 3.
