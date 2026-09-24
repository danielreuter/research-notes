---
lane: verify-night
kind: handoff
from: sp1-tcdot
created: 2026-09-24T06:55Z
---

# sp1-tcdot -> verify-night: independently verify modified SP1 (TC_DOT chip) relation-bare/v2, A100 BF16, B=4096

**The result.** `art:90671b8063bbed09edf6a3a8573733e4501d19e557c875e439daa4c0b8618d6c` (bench-result/v1). Its run-files
are `art:d9a862c505ea78e5aca426edbbac35a0a76aca8b3e31f8c60891fa17a50a0edd` (run-files/v1). Both are PRESERVED.
(`art:abfebfe7…` is the same run registered in the wrong form; it is labelled superseded_by `art:90671b80…`. Ignore it.)

This is a **modified** SP1 (veritor claim register CL10): SP1 6.4.0 plus the `TC_DOT_BF16` precompile. That chip proves
one tc-ampere-bf16 m16n8k16 step per call. It is proved as a core STARK by the fork's own CUDA `sp1-gpu-server` on an
NVIDIA A100-SXM4-80GB. B=4096 VUs of `vu-k1536` from `bench-instances/v1` (manifest `059103cf…`). The median of 3 reps
gives t.total 12.763 s, with 17 shards and 24,898,632 B per proof. Stock SP1 (`art:2a10bc89…`) takes 29.91 s.

Table 2 excludes it for the same reason as stock SP1: a 100-bit target per shard proof, and −95.9 after the union bound
over 17 shards. The coordinator treats SP1 as a drill-down. "Not independently verified" is what this handoff asks you
to settle.

**The statement is byte-identical to sp1-table's.** It is `relation-bare/v2`, statement sha256 `5e0dd245…86bb`, 8263 B,
and the public values are `digest || 01`. If you already wrote `statement.mine.bin` for sp1-table's handoff (step 2
there), reuse it.

## 1. Fetch

~~~sh
research data fetch art:d9a862c505ea78e5aca426edbbac35a0a76aca8b3e31f8c60891fa17a50a0edd --to tcdot-a100 --path 'proofs/*'
sha256sum tcdot-a100/proofs/*
# 757cce919badce25866a8da0e4b0996407092c2773665098d2b055b9947f6b74  proof-rep0.bin
# abb341ebf0b892e9f5f3023a2ed600f6dd4ccc5da431a44bd0f3e05145d6d14b  proof-rep1.bin
# 40e46a165a67d3a4824aaaa7df632f23636db9728b79643e2b29679baf360d5d  proof-rep2.bin
# 5e0dd245187bab03bf06c5105545342c7a3ec422069f1464614b5a49e14286bb  statement.bin   (8263 B)
~~~

## 2. Build the fork's verifier (verity-tcdot-host, CPU only, Linux pod as root)

Build from `lane/sp1-tcdot` @ `572018a3` (in the shared `.git`). `build_fork.sh` does four things:
- installs apt deps, rustup, and `sp1up --version v6.4.0`;
- clones upstream succinctlabs/sp1 at v6.4.0 (`f66b4bff5`, depth 1);
- applies `backends/sp1/tcdot/sp1-patches/0001-0005` with fixed committer identities, then checks the tree against
  `FORK_TREE` (`6d55145f…`, HEAD `fe35cc50…` = `FORK_HEAD`);
- links the checkout at `backends/sp1/tcdot/sp1`.

`SKIP_SERVER=1` skips the CUDA server, which a verifier does not need.

~~~sh
git -C ~/projects/verity-main-wt/main worktree add /tmp/tcdot-verify 572018a3      # or clone/rsync that commit to the pod
cd /tmp/tcdot-verify
SKIP_SERVER=1 SP1_TCDOT_ROOT=/workspace/tcdot-verify bash backends/sp1/tcdot/build_fork.sh
cd backends/sp1/tcdot
VERITY_TCDOT_FORK_HEAD=$(git -C sp1 rev-parse HEAD) CARGO_TARGET_DIR=/workspace/tcdot-verify/target \
  cargo build --release --locked -p verity-tcdot-host         # no `--features cuda`; host/build.rs builds the guest ELF
H=/workspace/tcdot-verify/target/release/verity-tcdot-host
SP1_PROVER=cpu RUST_LOG=error $H info    # expect elf_sha256 01dbe1d9af71c2b1…ba5dc, vk_hash 0x00347dc989cf805d…569bf, fork_head fe35cc50…
~~~

The guest build remaps both machine paths (`host/build.rs`), so the ELF depends only on the tree, `Cargo.lock`, the fork
and the toolchain. If your `elf_sha256` differs, the vk differs too and every proof will be rejected. Report that as a
reproducibility finding, not as a rejection.

## 3. Verify each proof against your own statement bytes

~~~sh
for r in 0 1 2; do
  SP1_PROVER=cpu RUST_LOG=error $H verify --proof tcdot-a100/proofs/proof-rep$r.bin --statement statement.mine.bin
done
~~~

Each run prints one JSON line and exits 0 only if the proof is accepted. Acceptance requires three things:
`ok` (SP1's core verifier accepts under the vk recomputed from the embedded ELF), `statement_match` (public values
`[..32]` = sha256 of your statement file), and `verdict` (byte 32 = 01). Expect `shards` 17, a `verify_seconds` of
about 1.0 s, and a process wall of about 27 s (SP1 CPU setup of the ELF is about 14 s). As a sanity negative,
flipping any byte of a proof must exit non-zero.

## 4. Label

On `art:90671b80…`: `verified=accepted|rejected` and `verifier="verity-tcdot-host verify @ lane/sp1-tcdot 572018a3, fork
fe35cc50 (SP1 6.4.0 + sp1-patches 0001-0005), CPU"`, plus `verifier_seconds` and `same_device=false`. Per the lane
contract, only you write these.

Later hill-climb results from this lane use the same build unless their `software.backend.commit` or `fork_head`
differs. I will note any such change in my report.
