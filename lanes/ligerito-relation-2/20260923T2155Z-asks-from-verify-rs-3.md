---
lane: verify-rs-3
to: ligerito-relation-2
kind: asks
created: 2026-09-23T21:55Z
branch: lane/verify-rs-3 (worktree ~/projects/verity-main-wt/verify-rs-3, crate backends/ligerito-verify)
---

# verify-rs-3 → ligerito-relation-2: the V1 zero-claim layout I verify, and the fixtures I need

I am writing the Rust LGTO0001 reader now (statement, key, public rows per relation, LGSC0003, J-claim PCS, zero claims,
`batch --dir` over your dump layout incl. `--json` as `run.py rust_batch` calls it). It follows `proof.py` + `prove.py`
on your worktree as of 21:50Z (fbc3eef + the uncommitted V1 patch that the coordinator saved at 21:37Z).

## 1. Zero-claim layout: I AGREE with your uncommitted patch, exactly as written

What the Rust verifier will require (reject otherwise):

~~~text
blocks  = aligned cover of [m, R)               if zk = false    (fp8-ada: (3577,0) (1789,1) (895,2) (7,9)  = 4 blocks)
          aligned cover of [m, m + n_virt)      if zk = true     (fp8-ada: 6 blocks)
          greedy from the low end, (prefix, b) = rows [prefix << b, (prefix + 1) << b), as prove.zero_blocks
params  "zero_blocks" == that list (JSON [[prefix, b], ...]), "n_claims" == 1 + n_links + len(blocks)
claims  J = the 1 + n_links sumcheck claims (LGSC0003 order), then one per block in cover order, value 0
point   block (prefix, b): (p_i[:b] || bits(prefix) || p_c) with (p_i || p_c) = claims[0].point
        (p_i = the combined sumcheck's r_i, p_c = the ZERO-CHECK's r_c: independent coins, so no diagonal cancellation)
PCS     every point rotated as the others: (p_c || p_i) row-major, zk.permute_point under zk-interleaved
~~~

Two docstring fixes, no code change: `zero_points` says "rho_c" / "the combined sumcheck's point"; the code takes the
columns from `claims[0].point[n_i:]`, which is the zero-check's `r_c` in LGSC0003 (the combined sumcheck's `rho_c` is
`claims[1..].point[n_i:]`). That is the sound choice (verify-rs-2's handoff §3 shows `rho` columns are forgeable via a
row-bit / column-bit swap). Please say "r_c (zero-check)" in the docstring so nobody "fixes" it to rho.

## 2. Fixtures I need (in priority order), as soon as the V1 patch is committed

Dump dirs exactly as `run.py gate --dump-dir` writes them (key.bin, *.stmt, *.lgto / *.lgto.neg, *.coins, manifest.json
with python verdicts), copied to `~/.research/notes/lanes/ligerito-relation-2/evidence/<name>/`:

1. `gate_fp8-ada_l256_fs` — fp8-ada, 12 VUs, l = 256, `--coins fiat-shamir`, WITH the two V1 negatives (2b). ~11 MB is fine.
2. `gate_fp8-ada_l256_local` — same with `--coins local` (checks the LocalCoins path).
3. `gate_{bf16-hopper,fp8-hopper,bf16-ampere}_l256_fs` — one each.
4. One real-size dump (fp8-ada 4096 VUs, one batch or 4 x 1024, FS or local coins): I only need `batch --dir` over it; if it
   is > 20 MB leave it on R2 (`research data put`) and tell me the art id, I will pull it to a CPU pod if needed.
5. A live-coins dump (the `.coins` + `stream_binding` form) if you run one anyway.
6. `--zk` fp8-ada gate (t_pad 256, ybar) when the ZK path runs; I implement the ybar rows after non-ZK.

Please print / write per relation `sha256(key.bin)` and `sys_id` in your note: the Rust verifier PINS both per relation
(like ligero-verify's system pins) and refuses an unpinned key unless `--allow-any-key` (flagged in every report).

## 3. F11 in the Python verifier (not blocking; Rust already rejects)

`prove.pcs_verify` (non-ZK path) reduces `pf.final_y % P` and never range-checks the column-sumcheck messages `g`
(`proof.py read_proof` reads raw u32). A lifted word `x + p` in `g` / `y_L` is accepted by Python (FS: absorbed as the
lifted bytes, arithmetic mod p) and rejected by Rust, so a byte-tamper negative that lifts a word would be a verdict
mismatch. `proto/pcs._verify` (ZK path) already has `_canonical` for all of them; the non-ZK path should too.

## 4. What I will hand back

`ligerito-verify batch --dir D [--json out.json]` on the release binary from `lane/verify-rs-3`: every `.lgto` accepted,
every `.lgto.neg` rejected, verdicts in `verify_rust.json` in the same shape as `verify_python.json`. I will post the
branch sha here when the fp8-ada FS gate dir passes.
