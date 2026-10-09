---
id: proofs/20261009T1745Z-report-flock-os-salts
campaign: recursion
lane: proofs
kind: report
status: open
repo: danielreuter/verity
origin: https://cursor.com/agents/bc-ad20837e-6819-5833-9cc4-68a702c2d504
---


# C-Flock leaf salts from the OS (decision 4(a)): report

Daniel's decision 4(a) (16:01Z, 9 Oct): "Salts from the OS: yes, which removes the PRG premise." The change is done and
pushed. Every C-Flock `hm96-sha512/v1` leaf salt now comes from `getrandom`, never from a ChaCha20 stream. That covers
level 0's, levels 1+'s, the pads tree's and every table's, and both the CPU and GPU provers. It costs no measurable prove
time on the CPU or the GPU at m = 25 and m = 28. It costs +48 MiB of device memory, and on the GPU path about +61 MB of
host RSS at m = 28. The verifier is unchanged: nothing under `verity/ml/flock/verifier/` moved.

## Status

- **Branch:** `cursor/flock-os-salts-95d4`, head `e325135e8`, pushed to origin.
- **Base.** a38fdb621 (#1626) is still not on `origin/main`. `git merge-base --is-ancestor a38fdb621 origin/main` is false
  at 17:00Z, and #1626 is open, not merged. The 80e829d83147 in the job text is node 2's check **tree** hash, not a commit
  on main. So the branch is a38fdb621 merged onto `origin/main` e091532ea (merge commit `c7396ccd3`), and the change sits
  on top in four commits:
  - `fd36cbaf2` C-Flock: read every hm96 leaf salt from the OS, not a ChaCha20 key (decision 4(a))
  - `7449b903c` served_zk: commit rows under OS salts handed to the device, not a ChaCha20 stream
  - `be8bd6ca3` flock-circuit: the leaf-salt comment says the OS's salts reach the device tree by tree
  - `e325135e8` gpu_circuit: drop the salts handed to the device once the prover returns (the gpu build referenced the
    removed key guard)

  Until #1626 lands, a PR of this branch against main also shows #1626's diff. That includes
  `verity/ml/flock/verifier/firewall_agree.py` and `verity/core/service/flock/lean-audit.json`, which are #1626's own.
- **Draft PR: not opened.** This VM has no tool that creates a PR, and `gh` is read-only. The title and body are at the
  end, ready for whoever opens it.
- **`check.py --record --agreement`: not run. The only free check slot was node 2's last free slot, during a landing train.**
  I read `check.py --slots` three times.
  - **16:50Z and 17:19Z.** No slot was free on node 1, node 2 or vy-nebius-cpu-1. Both nodes' slots a and b were held,
    with priority train runs waiting in their lines (tree 4fce1493defa at 17:19Z, r20261009-171318-3476 / -959e /
    -4309). vy-nebius-cpu-1's check a was free but blocked on memory (409 GB free, under the 560 GB a check there may
    peak at).
  - **17:39Z.**
    - Node 1 still held both slots: check a by flock-scope-v2, check b by old-circuits-and-proofs.
    - Node 2's check b was free, with nobody waiting. But it was node 2's last free slot. Check a was taken at 17:36Z by
      the lander's account, bc-8ece7cde (old-circuits-and-proofs, which keeps the merge trains): run
      r20261009-173545-055f, tree 7fb200ae05fc. Its priority train runs had been waiting on all three pods 20 minutes
      earlier.
    - vy-nebius-cpu-1's check a was still blocked on memory (345 GB free).

  Under "don't take node 1's or node 2's last free slot from a landing train", I didn't take node 2's check b. No check
  was queued, and there is no run id. When a slot is free, the command, from a clean checkout of `e325135e8`, is
  `uv run --extra torch-cpu python tools/verity/check/check.py --record --agreement --on auto`.

## What changed

- **`verity/ml/flock/live/src/zk_hooks.rs` (`LeafSalts`).**
  - Each tree's salts (`leaves × 192` bytes) are read from `getrandom` in 64 KiB pieces (`OS_PIECE`) on rayon's
    threads, and each tree is read once.
  - Level 0's are kept for the proof (`LeafSalts::level0`, an `Arc`). The session's `Commit`, both reps and the firewall's
    recheck therefore commit one tree.
  - After `fork()` (the firewall's shadow beside the device), each tree's first draw is kept for the other side, zeroed
    if dropped (`ZeroOnDrop`).
  - The per-proof key (`key()`) and `salt(id, i)` are gone.
  - Only an injected seed (feature `seed-injection`, the selftest harness) still expands salts with ChaCha20. Its key is
    `STREAM_SALT`, blocks `3i..3i+2` with nonce `id`, so a test proof repeats.
  - Tests: fresh salts per tree, proof and table, read once where shared. A fork's two sides get one set of salts. The
    injected-seed tape is pinned.
- **`verity/ml/flock/live/src/bin/flock-circuit.rs`.**
  - Level 0's root, the firewall and the session commit `LeafSalts::level0`.
  - `zk_tables_share_no_randomness` now also requires that the tables share no salt.
  - The GPU selftest `device_salts_match_host` checks the device's leaves, computed from the host's salts, against
    `hm96::leaf`.
- **GPU** (`verity/ml/flock/cuda/sha512.cuh`, `prove_circuit.cuh`, `cuda_sha512_patch.py`, `live/src/gpu_circuit.rs`).
  - The device's ChaCha20 (`Hm96Key`, `hm96_salt`) is removed.
  - The device asks the host for each tree's salts through a callback (`hm96_tree`). It uploads them in 2^18-leaf chunks
    through a 48 MiB device buffer, which is zeroed on free, and copies an opening's salts from the host's bytes.
  - `gpu_circuit` holds every salt it handed out until the prover returns.
- **served_zk** (`benchmarks/pouw/served_zk/rows_bench.py`, `statement.py`, `hm96_rows.cu`, and its test).
  - Each commit's salts are `os.urandom` bytes uploaded to the device, made fresh for each pass (`Commit.fresh_salts`).
  - Its ChaCha20 reference (`chacha20_block`, `salt`, `SALT_KEY`, `SALT_TAG`) is gone.
  - The kernel reads the salts from memory.
- **Text.**
  - `verity/ml/flock/live/PROTOCOL.md`: the salt text in §2 (several tables), §3 (the pads tree), the assumptions, the
    randomness caveat and §10.
  - The `leaf_scheme()` doc in `live/src/circuit.rs` and the comment above `LEAF_SCHEME` in
    `verity/ml/flock/python/verity_flock/circuit.py`.

## What the verifier doesn't see

The verifier never derives a salt. It receives a leaf's 192 salt bytes only when that leaf is opened, and checks
`leaf = SHA-512(leaf_prefix ‖ x ⊕ M(key)·y ‖ SHA-512(salt_prefix ‖ y))` against the Merkle path. Where the bytes came from is
invisible to it, so the verifier, the Lean verifier and every record are unchanged:
- `git diff --stat c7396ccd3..HEAD -- verity/ml/flock/verifier/` is empty.
- No salt is written to any record, as before.

One consequence is left open. META `leaf_scheme.salt_source` still reads "chacha20 expansion of a fresh 256-bit os key per
proof, never reused or stored", which now misdescribes the prover. The Lean verifier pins that object
(`Flock/Tags.lean` `leafSchemeHm96`, `VStar/Compose.lean`), so new text means a new tag set, and that is a verifier change.
I left the string alone and noted why beside it, in `circuit.rs` and in `circuit.py`.

## Costs

All runs used one `--zk` statement, RoPE d64 (`rope-head/d64/neox-bf16`), with `prove --zk --warm 0 --runs 1` against a
loopback `serve --zk`. Before and after builds alternated, three rounds each. Every session was accepted, and every replay
gave the upstream verdict "accepted".

| where | statement | before: prove_total_s | after: prove_total_s | before: peak host RSS | after: peak host RSS |
|---|---|---|---|---|---|
| CPU, this VM (4 cores) | m = 25, 16 instances | 0.615 / 0.611 / 0.643 | 0.603 / 0.613 / 0.620 | 0.997 / 1.003 / 1.004 GB | 1.002 / 0.998 / 1.000 GB |
| CPU, this VM (4 cores) | m = 28, 128 instances | 2.177 / 2.016 / 2.396 | 2.201 / 2.048 / 2.282 | 1.716 / 1.749 / 1.746 GB | 1.715 / 1.725 / 1.696 GB |
| GPU, vy-nebius-1, 1 RTX PRO 6000, 16 cores | m = 28, 128 instances | 2.838 / 2.932 / 2.685 | 2.733 / 2.897 / 2.787 | 1.638 / 1.636 / 1.646 GB | 1.703 / 1.699 / 1.701 GB |

- **CPU.** No difference beyond noise in time or memory. Level 0's salts were already kept for the proof, and a later
  tree's salts live as long as before.
- **GPU** (run r20261009-171209-4678, sm_120, CUDA 13.3).
  - Prove time: the means are 2.82 s before and 2.81 s after, so no difference. Wire bytes are identical (1,735,678).
  - Device memory peak: 2165 MiB before, 2213 MiB after. The +48 MiB is the fixed salt buffer.
  - Host peak RSS: about +61 MB (+3.7%). The host now reads, and holds until the prover returns, the salts of every tree
    the device builds (192 bytes per leaf). The device used to expand them in registers.
  - The after kernel uses fewer registers: `hm96_finish_leaves` 194 against 212, and `sz_finish` has a 1360-byte stack
    against 1584. In exchange it reads 192 bytes of salt per leaf from device memory.
- **The salt draw itself** (a microbenchmark on this VM, 4 threads).
  - Rates: ChaCha20 (the old path) ran at 2.1–2.4 GB/s. OS reads ran at 1.4–1.6 GB/s in 64 KiB pieces, and at about
    0.86 GB/s with one call per leaf.
  - At 2^20 leaves (201 MB of salts): 0.087 s ChaCha20 against 0.144 s OS.
  - At 2^21 leaves (403 MB): 0.182 s against 0.252 s.
  - So per byte the OS read costs about 1.5× ChaCha20. Reading in pieces, not one call per leaf, is what avoids the +96%
    whole-prove cost at m = 33 that led to the 27 Sep key.
  - Neither m = 25 nor m = 28 shows it, so a larger cell is where any cost would show up.
- An earlier GPU attempt, r20261009-170959-906a, stopped in the base tree's build: node 1's CUDA 13.0 `ptxas` doesn't
  know `clmad`. It is not a result.

## Tests

- **C-Flock's Rust** (`verity/ml/flock/check_build.sh` and `check_build.sh test` on the after tree): `cargo check` of
  sha512, sha512+glue and sha512+glue+seed-injection, then the tests.
  - flock-live, features sha512: 102 passed, 1 ignored.
  - flock-live, features sha512,glue,seed-injection: 109 passed, 2 ignored.
  - The flock-core, prover, merkle, transcript and hash crates and the rest: 0 failed.
- **GPU build.** `flock-circuit --features sha512,glue,gpu,seed-injection` compiles and links here (CUDA 13.3, sm_90)
  and on node 1 (sm_120). The nvcc warnings are the base's; the build's one fix is commit `e325135e8`.
- **Selftest `--zk`** (run r20261009-171209-4678, `60-circuit.sh MODE=selftest ZK=1 SELF_N=4`).
  - Only `lincheck_modes_agree` fails: 1 of 46 CPU cases and 1 of 49 GPU cases.
  - It fails identically on the base tree. I ran `selftest --zk --only lincheck_modes_agree` locally on both builds:
    `reencoded_identical: false` in both. Under `--zk`, proof 0 doesn't re-encode as a bare
    `(Commitment, R1csProofLigerito)`. That failure predates this change and isn't about salts.
  - Among the cases that pass: `gpu_proofs_match_cpu` (the device's proofs and transcripts are the CPU's, byte for
    byte), `prover_is_deterministic`, `zk_tables_share_no_randomness`, `record_replays_offline` and the `tables_*` cases.
  - `zkaudit --zk --gpu`: `attributed: true`, `checks_pass: true`.
- **Selftest M0** (`device_salts_match_host`, `opened_salt_altered` and `leaf_salts_from_prover_seed_refused` run only
  without `--zk`): run r20261009-173018-5de8, `60-circuit.sh MODE=selftest ZK=0 SELF_N=4`, on node 1 (sm_120).
  - Every case passes: 41 of 41 on the CPU, 44 of 44 on the GPU.
  - On the GPU that includes `device_salts_match_host` ("the device's leaves from the host's salts equal hm96::leaf"),
    `opened_salt_altered` (rejected), `leaf_salts_from_prover_seed_refused`, `gpu_proofs_match_cpu` and
    `prover_is_deterministic`.
- **Python.**
  - `benchmarks/pouw/tests/test_served_zk_rows_bench.py` with `test_served_zk.py`: 21 passed. The new test checks that
    each row's salts are the OS's, and that the reference leaves use the same bytes.
  - `verity/ml/flock/tests/test_circuit.py` (which pins `LEAF_SCHEME`): 23 passed.
  - `hm96_rows.cu` compiles for sm_120a (before and after), with no warnings.

## What still uses ChaCha20

- **`ProverRng`** (`zk_hooks.rs`): every mask, pad, RS padding coefficient, extra lane and per-table stream is still
  ChaCha20, keyed by the session's OS `ProverSeed`.
  - The PRG premise remains for those, and only those (`live/PROTOCOL.md`, the randomness caveat).
  - Decision 4(a) removes it from the salts. Removing it from the pads and masks too would be another decision of the
    same kind.
- **Test-harness only.** An injected seed (feature `seed-injection`, never a proving build) expands its salts and derives
  its `coin_nonce` with ChaCha20, so the harness's proofs repeat.
- **Text the verifier pins, left as it is.**
  - META `leaf_scheme.salt_source` (above): the open item, a new tag set.
  - `verity/ml/flock/verifier/PROTOCOL.md:1202` ("salts a ChaCha20 expansion of a per-proof OS key"): under
    `verifier/`, so untouched.
  - The identity's `hooks.tables` string ("ChaCha20 streams at purpose | j << 32 and hm96 salt trees from id j << 32"):
    still true, and pinned by `Flock/Zk.lean`.
- **`verity/ml/commitments/hm96/PROTOCOL.md:121`, `:209`.** These are general remarks: hm96 allows salts from the OS or
  from a seeded stream, and models both as uniform.
  - Line 121 also notes that Linux's `getrandom` is itself a ChaCha20-based generator. "No premise on ChaCha20" holds in
    the repository's convention, which treats the OS generator as uniform. A reader who wants none at all would look
    there.
- **Outside C-Flock, not touched.** Each salts its own commitments with ChaCha20 under a salt key:
  - PoUW's hm96 commitments (`verity/core/protocols/pouw/audit.py` `hm96_salt`, Pearl-C's `pearl_c_sm120` `SALT_KEY`);
  - the vLLM serving rows (`integrations/vllm/verity_vllm/commit/serving_rows.py`).
- **Not a salt:** the coin tree's test tape in `live/src/lib.rs` (`coin_tape`, the server's).

## PR title and body (for whoever opens it, draft, against main)

Title: `C-Flock: hm96 leaf salts from the OS, not a ChaCha20 key (decision 4(a))`

Body:

> Daniel's decision 4(a) (9 Oct): "Salts from the OS: yes, which removes the PRG premise." Every C-Flock `hm96-sha512/v1`
> leaf salt (level 0's, levels 1+'s, the pads tree's, every table's) is now read from the OS (`getrandom`), never from a
> ChaCha20 stream. Each tree is read once: level 0's are kept for the proof, and a tree that both the firewall's shadow
> and the device build is kept for the other side. No salt reaches a record.
>
> Based on #1626 (a38fdb621, merged onto main e091532ea as c7396ccd3). Until #1626 lands, this diff includes #1626's.
>
> **What changed.**
> - `zk_hooks::LeafSalts`: OS reads in 64 KiB pieces on rayon's threads. The per-proof key is gone. Only the selftest
>   harness's injected seed still expands salts with ChaCha20, so its proofs repeat.
> - GPU (`sha512.cuh`, `prove_circuit.cuh`, `gpu_circuit.rs`): no device ChaCha20. The device takes each tree's salts
>   from the host through a callback, in 2^18-leaf chunks through a 48 MiB buffer zeroed on free.
> - served_zk (`rows_bench.py`, `statement.py`, `hm96_rows.cu`): `os.urandom` salts per commit, uploaded to the device.
> - `live/PROTOCOL.md`: the salt text.
>
> **Cost** (RoPE d64 `--zk`, 3 alternating rounds, prove_total_s):
> - CPU, 4 cores, m = 25: before 0.62 s, after 0.61 s.
> - CPU, 4 cores, m = 28: before 2.20 s, after 2.18 s.
> - GPU, RTX PRO 6000, m = 28: before 2.82 s, after 2.81 s.
>
> Peak host RSS is unchanged on the CPU and +61 MB (+3.7%) on the GPU path, where the host now holds the device's trees'
> salts. Device memory is +48 MiB, the salt buffer. Per byte an OS read costs about 1.5× ChaCha20 (403 MB of salts: 0.25 s
> against 0.18 s on 4 threads).
>
> **What the verifier doesn't see.** The verifier never derives a salt. It checks an opened leaf's 192 salt bytes
> against the leaf hash, and where they came from is invisible to it. Nothing under `verity/ml/flock/verifier/` changes,
> and the Lean verifier and the records are unchanged. META `leaf_scheme.salt_source` still names the replaced key,
> because the Lean verifier pins it. New text means a new tag set, which is left to a verifier PR.
>
> **Tests.**
> - C-Flock's Rust tests: 0 failed.
> - `flock-circuit` with the gpu feature builds for sm_90 and sm_120.
> - The M0 selftest passes every case on CPU and GPU (41 and 44), `device_salts_match_host` and `opened_salt_altered`
>   among them.
> - The `--zk` selftest on CPU and GPU: only `lincheck_modes_agree` fails, as on the base. `gpu_proofs_match_cpu`
>   passes, and the device `zkaudit` passes.
> - served_zk tests: 21 passed. `test_circuit.py`: 23 passed.

PR: [#1654](https://github.com/danielreuter/verity/pull/1654) (draft), branch merged up to main 6cea9a973 as b3727bd96.
