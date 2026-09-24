---
lane: verify-night
kind: handoff
from: sp1-table
created: 2026-09-24T06:32Z
---

# sp1-table -> verify-night: independently verify SP1 stock relation-bare/v2, A100 BF16, B=4096

**The result.** `art:2a10bc89d0ed17aabda90d319aa0818c57c32cef2df7a3d9351c6ddce179addd` (bench-result/v1). Its run-files
are `art:a659f5eedbdcafd07f0d3cc4d91c4f427a7f9139de5af8301f7e7ac5b5e5420d` (run-files/v1). Both are PRESERVED.

It is stock SP1 6.4.0 (a core STARK from the CUDA prover) on an NVIDIA A100-SXM4-80GB. B=4096 VUs, `vu-k1536` of
`bench-instances/v1` (manifest `059103cf…`). The median of 3 reps gives t.total 29.91 s. Each proof is 54,922,124 B.

Table 2 renders it out on the frozen 2^-128 rule: SP1's security target is 100 bits, and the achieved level after the
union bound over 36 shards is −94.83. The coordinator put that decision to the user for the morning. The one other
reason is "not independently verified", which is what this handoff asks you to settle.

**The statement.** Public: the format (bf16-ampere = 1), the instance-set identity, and the 4096 output words `y`.
Private: every VU's x row and W row. The guest commits 33 bytes, `sha256(statement bytes) || verdict`. A verifier
accepts only `digest || 01` under the pinned verifying key, where `digest` is the hash of statement bytes it wrote
itself.

## 1. Fetch

~~~sh
research data fetch art:a659f5eedbdcafd07f0d3cc4d91c4f427a7f9139de5af8301f7e7ac5b5e5420d --to sp1-a100 --path 'proofs/*'
sha256sum sp1-a100/proofs/*
# 2fc84c49f50efc63d61adf39aa8aeb1aaf469714de20d0d80cfbfd2b7216e928  proof-rep0.bin
# 57ab8e99374b7998b4ff2bd4d12069206de37ba6d7b945a930c6d1b1a2b189d6  proof-rep1.bin
# 370d6b26f94b50cba3ecc697ba3f3669bd77b6f8cb45d4b0bf5644651b2d52e2  proof-rep2.bin
# 5e0dd245187bab03bf06c5105545342c7a3ec422069f1464614b5a49e14286bb  statement.bin   (8263 B)
~~~

## 2. Write the statement yourself (from the committed y words; no x/W arrays needed)

~~~python
import hashlib, struct
y = open("fixtures/bench-instances/v1/vu-k1536.y.u16", "rb").read()          # committed, 8192 B
ident = b"bench-instances/v1|vu-k1536|0|4096|059103cf9bd55ee83cbd4bb14ae6db2f60db2cb4ddf85cdc22b1cecee6e4eeea"
st = (b"verity/sp1/relation-bare/v2" + struct.pack("<I", 1) + hashlib.sha256(ident).digest()
      + struct.pack("<II", 1536, 4096) + y)
open("statement.mine.bin", "wb").write(st)
print(len(st), hashlib.sha256(st).hexdigest())   # 8263 5e0dd245187bab03bf06c5105545342c7a3ec422069f1464614b5a49e14286bb
~~~

Check that it equals the run's `statement.bin`. Use yours in step 4.

## 3. Build the verifier (veritor-zk-host, CPU)

Build from the lane branch `lane/sp1-table` at commit `b5e1ed5f` (in the shared `.git`, `~/projects/verity/.git`).
Build on a Linux pod, not the laptop. It needs `sp1up --version v6.4.0` (i.e. `cargo prove` and the `succinct`
toolchain), `clang`, `cmake` and `protobuf-compiler`. `backends/sp1/pod_bootstrap.sh` installs all of these;
`SP1_HOST_FEATURES=relation-bare` gives a CPU-only host.

~~~sh
git -C ~/projects/verity-main-wt/main worktree add /tmp/sp1-verify b5e1ed5f
cd /tmp/sp1-verify/backends/sp1
cargo build --release --locked -p veritor-zk-host --features relation-bare    # also builds the guest ELF (host/build.rs)
SP1_PROVER=cpu ./target/release/veritor-zk-host info
# expect: "elf_sha256":"cffc5eff15cc24862c1e94266b037370cffa98d8eb48bc17001e8f32ebddd701",
#         "vk_hash":"0x000503d6bb7a3c42e224d801b751f46bd6b38afba82bec9006e1e6d1675674eb", "guest_features":["relation-bare"]
~~~

The guest build is reproducible without Docker: `host/build.rs` remaps paths and builds `--locked`. So the ELF, and
with it the verifying key, is a function of the source tree alone. If your `elf_sha256` differs, stop and tell me.

## 4. Verify (each rep)

~~~sh
for r in 0 1 2; do
  SP1_PROVER=cpu RUST_LOG=error ./target/release/veritor-zk-host verify \
      --proof sp1-a100/proofs/proof-rep$r.bin --statement statement.mine.bin 2>/dev/null | tail -1
done
~~~

Expected (the last line of each; rep 1 shown, captured on the producer pod 06:33Z; ~30 s per process, 2.3 s of it
the verify call):

~~~json
{"backend":"sp1","ok":true,"public_values":"5e0dd245187bab03bf06c5105545342c7a3ec422069f1464614b5a49e14286bb01","statement_digest":"5e0dd245187bab03bf06c5105545342c7a3ec422069f1464614b5a49e14286bb","verdict":true,"unsound":false,"vk_hash":"0x000503d6bb7a3c42e224d801b751f46bd6b38afba82bec9006e1e6d1675674eb","statement_match":true,"verify_seconds":2.312529926}
~~~

Accept only when all of these hold: `ok` is true (`client.verify` under the key of your build), `statement_match` is
true (the committed digest is sha256 of your statement bytes), `verdict` is true, and `unsound` is false.

A quick negative: change one byte of `y` in `statement.mine.bin`. Then `statement_match` must be false.

## 5. Label

~~~sh
research data label art:2a10bc89d0ed17aabda90d319aa0818c57c32cef2df7a3d9351c6ddce179addd verified accepted --by verify-night --ref <your record>
~~~

The renderer's producers set for this result is empty (no candidate/label labels), so a label by `verify-night`
counts.

**Later results.** I am hill-climbing until 12:00Z. Any faster registered result goes to you as a follow-up handoff
with the same shape: new art ids, possibly a new commit and `elf_sha256`/`vk_hash` if the guest kernel changed, and
the same statement bytes. The baseline above stands on its own.
