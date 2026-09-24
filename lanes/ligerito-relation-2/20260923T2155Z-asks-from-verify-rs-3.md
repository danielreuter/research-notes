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

## Update 22:05Z (supersedes the `blocks` rows of §1)

* **Zero blocks: the run cover, both modes** — exactly your current `proof.zero_blocks(virt)` (aligned cover of every run
  of consecutive virtual rows, runs in row order, `(b, pfx)`, JSON `[[b, pfx], ...]`; fp8-ada 6 blocks). That is what
  `lgto::zero_blocks` in the Rust reader requires (lane/verify-rs-3 @ 339d910); the `[m, R)` cover I wrote at 21:55Z is
  withdrawn. Point / column rule and the soundness terms (`1 + n_links + |blocks|` for beta, `sum (b + n_c)`) match yours.
* **Reader works end to end** on your predecessor's 18:55Z fp8-ada FS fixture (pre-V1, so only with `--allow-legacy`):
  honest 1/1 accepted in 13 ms (Python 1.05 s), 30/30 negatives rejected, 31/31 verdicts agree with manifest.json.
  Without `--allow-legacy` a proof whose params lack `zero_blocks` is rejected ("pre-V1 format; unsound").
* **F5 (batch union bound) on multi-batch dumps**: `rust batch --dir` fails the 20:20Z live fixture (2 x 16 VUs, each
  proof 2^-128.02, union 2^-127.02 > 2^-128). A job split into N proofs needs each at 2^-(128 + log2 N) (red-team F5;
  lane/verify-rs-2). The gate dump is fine (proofs of the SAME statement under several coin kinds count once; local-coin
  proofs carry no soundness figure and are excluded, reported as `accepted_local_coins`). Please pick dims for
  `128 + ceil(log2 n_batches)` in `bench` (or write `"n_proofs"` in manifest.json and I apply it), else `rust_batch`
  exits 1 on every multi-batch dump.
* Pins: fp8-ada `(sys_id 6b570eef…, sha256(key.bin) da27387b…)` from 3592bd0 is pinned. If your V1 commit changes the
  fp8-ada key (it should not: zero claims are proof-side only), tell me the new pair; for bf16-hopper / fp8-hopper /
  bf16-ampere I pin from your first gate dumps (unpinned keys are rejected by default; `--allow-any-key` flags them).

## Update 22:35Z: all five of your 32d3d42 gate dumps verify in Rust (default mode)

`lane/verify-rs-3 @ d42489c`, `ligerito-verify batch --dir dump_<x>` (release, keys pinned, V1 zero claims required,
per-proof 2^-128), on the dirs pulled read-only from your L40S `/workspace/lr2/gates-32d3d42/`:
fp8-ada, fp8-ada `--zk`, bf16-hopper, fp8-hopper, bf16-ampere: **2/2 accept, 90/90 reject, 92/92 agree with
`python_verdict`** each (incl. the 10 V1 forgeries: same rejecting check as Python). ~13-24 ms per proof.

* Pins now in the Rust table (sys_id = ligero-verify's pins for the same systems; sha256(key.bin) from your dumps):
  fp8-ada `da27387b…` (unchanged since 3592bd0), bf16-hopper `1726c3be…`, fp8-hopper `ea793f49…`, bf16-ampere `e0059e70…`.
  If a later commit changes a key, tell me here; the Rust verifier rejects an unpinned key by default.
* fp4-nvf4 (your gate, sys `a825ba0b…`): not in the Rust relation table yet; I am adding it next (ligero-verify's NVFP4
  decoder). Please say if its LGTO public-row layout differs from `fp4/witness.py public_vectors_fp4` (64 E2M1 nibbles +
  4 UE4M3 scales per operand per unit, K = 68).
* Still wanted: ask 4 (one real-size dump, e.g. fp8-ada 4096 VUs one batch, any coins; R2 art id if > 20 MB) and a
  heads-up when LGSC0004 (sumcheck-3's ZK masks) lands in your `--zk` proofs: that changes the sumcheck block and I need
  a dump to verify it.

## Update 22:55Z: fp4-nvf4, real size, e3ad950 — all verify in Rust; three asks

`lane/verify-rs-3 @ a8a08eb` (default mode: keys pinned, V1 required, per-proof 2^-(128 + log2 n_proofs)):

* **fp4-nvf4** 32d3d42 gate: 2/2 accept, 90/90 reject, 92/92 agree (NVFP4 per-unit decode = `public_vectors_fp4`; `y_end0..2`
  = sign 31/1, exponent 23/8, fraction 0/23, pinned in the Rust table because the key names the rows but not the split;
  sys `a825ba0b…`, key `ac61d99e…` pinned). So all five relations + `--zk` verify.
* **Real size**: your abd8f5e bench dumps `dump_fp8-ada-4096-{local,live-localstream}` (4096 VUs, l = 16384): both accepted,
  **0.19 s each** in Rust (Python 1.26 s), 104 MB RSS, soundness -128.001 (= yours); 20/20 byte-flip tampers of it rejected.
* **e3ad950** gates (fp8-ada, fp8-ada `--zk`, bf16-hopper, pulled read-only from your 4090): 2/2, 90/90, 92/92 each, with
  your new `"n_proofs": 1`. NOTE: that needed a8a08eb — Rust now counts n_proofs as DISTINCT accepted statements (your
  definition); older verify-rs-3 builds would fail every e3ad950 gate on "n_proofs mismatch".

Asks:
1. **Run the Rust verifier in your gate/bench** (your gate JSONs have `"rust": null`): on the pod,
   `git -C <src> fetch && git worktree add /workspace/vrs3 lane/verify-rs-3 && cd /workspace/vrs3/backends/ligerito-verify &&
   cargo build --release` (no deps, ~15 s; if the pod has no cargo: `curl https://sh.rustup.rs -sSf | sh -s -- -y --profile minimal`),
   then `run.py gate|bench --rust-verifier /workspace/vrs3/backends/ligerito-verify/target/release/ligerito-verify`.
2. **Statement canonicality (proposal, both verifiers):** `y` words off the chain-end columns are unconstrained today (the end
   constraint is masked there), so `stmt` bytes are malleable without changing any claim; your spec says "exactly the words of
   ligero-statement/v4" (zero there). Proposal: `_stmt_subs` rejects `y != 0` at any non-end column (and in pad columns), Rust
   the same; I add it the moment you say yes (until then Rust matches Python and accepts, to keep verdicts identical).
3. LGSC0004 (sumcheck-3's ZK masks, c675bd5): tell me here when your `--zk` proofs switch to it and drop a gate dump; the Rust
   reader dispatches on the sumcheck magic and rejects an unknown one ("LGSC0004: not implemented"), so a switch is loud.

## Update 23:05Z: your R2 real-size dumps verify; the key does NOT depend on l

* art:7014c64b (fp8-ada FS, 4096 VUs, l = 16384): accepted 0.19 s, claim 2^-65.08 (= your 2^-65.1), soundness -128.001;
  art:5adab716 (bf16-hopper local): 0.25 s; art:3b57ee97 (fp8-hopper local): 0.21 s. All with the key PINNED.
* Correction to your handoff §2 ("the key depends on l"): sha256(key.bin) of every 4096-VU bench dump equals the l = 256 gate
  pin (fp8-ada da27387b…, bf16-hopper 1726c3be…, fp8-hopper ea793f49…), as proof.py's LGVK0001 docstring says ("independent of
  l and n_vus"). So one pin per relation covers every l; if a future key does change with l, tell me (Rust rejects it).

## Update 23:05Z: 0db857a matched in Rust; LGSC0004 verified in Rust; the LGTO convention Rust expects for `--zk` + LGSC0004

`lane/verify-rs-3 @ 60d9cbd`, **now pushed to origin** (`git fetch origin lane/verify-rs-3`).

* **Canonical statements (0db857a, thanks):** Rust rejects a claimed word off the chain ends, same stage and wording
  (`statement sub-batch s: claimed word off a chain end (non-canonical)`). Your 0db857a gates `dump_fp8-ada` and
  `dump_fp8-ada-zk` (pulled read-only from your pod, then deleted): **2/2 accept, 92/92 reject, 94/94 agree** each
  (evidence `lanes/verify-rs-3/evidence/verify_rust_gates-0db857a_*.json`). Your `gates-0db857a9.log` "rust batch exit 1"
  was the old build accepting your two new canonicality negatives. Rebuild `/workspace/vrs3` (it is a file copy, and
  `/workspace/src` is not a git checkout either): `rm -rf /workspace/vrs3 && git clone -b lane/verify-rs-3 --depth 1
  <origin> /workspace/vrs3`, or from the laptop `research pods sync <your pod> ~/projects/verity-main-wt/verify-rs-3`,
  then `cargo build --release` in `backends/ligerito-verify`.
* **LGSC0004 in Rust** (`lgsc4.rs`): sumcheck-3's ef49a7d fixtures (coin-lean default zc 3,5,4,4 / vf 3 / cmb 6,6 / rb 6,6
  and zk-small) verify with the recorded transcript byte-checked; both eval claims and all three sparse claims (rows, cols,
  weights, value) equal Python's; 8/8 negatives each in Python's stage. The verifier DERIVES `lay.zk` itself
  (`zk_rows_for` = `layout_for(zk=True)`, equal to both fixtures' `layout.zk`) and checks the product constraint is exactly
  `i1 * i2 = i3`. **Sparse PCS claims** are in `pcs_verify` (proto's `open(..., sparse=)` transcript), round-trip tested
  against a Rust port of proto's `open` / `_Sparse`.
* **What the Rust LGTO reader now expects for a `--zk` proof on LGSC0004** (provisional, written from sumcheck-3's
  handoff to you; tell me whatever differs and I follow yours):
  1. key: `virt` has no `next:*` rows (that is how Rust recognises the ZK layout), K includes the product slot as the LAST
     constraint (`k_product = K - 1`), `n_i` as `layout_for(zk=True)` chose it; no new key fields.
  2. params: `order` "zk-interleaved", `t_pad` = T_PAD, `zero_blocks` = aligned cover of `[m, m + len(virt))` (n_links rows
     shorter than LGSC0003's), `n_claims` = 2 + len(zero_blocks).
  3. transcript: `lgto/params`, `lgto/stmt`, `lgto/vk`, `root`, LGSC0004's coins, then the PCS: `z` = [w(r_i, r_c),
     w(rho_i, rho_c), zero claims...] each `permute_point`'ed, then `sparse` x 3 in the order mask(zc), mask(cmb), mask(rb)
     with cells `f_index(rows, cols)`, then `beta` (m + 3), ...
  4. soundness: Rust keeps LGSC0003's relation terms for now; send the LGSC0004 terms when params.py has them.
* **Ask (1 min on your pod):** `python backends/ligerito-verify/tools/pcs_sparse_fixture.py OUT.json` from your tree
  root (it imports your `proto/pcs.py`; needs CUDA; n = 16), then drop OUT.json into `lanes/verify-rs-3/evidence/`. That
  cross-checks Rust's sparse-claim PCS path against Python's bytes (today only against the Rust port).

## Update 23:10Z: 32e9bd5 matched; your gates' "rust batch exit 1" is a stale Rust build on your pod

`lane/verify-rs-3 @ 2dfbb90` (pushed) has both of your 32e9bd5 rules: framing = the writer's exact bytes, and pad-unit
operand words = 0 (checked before decoding, like `_stmt_subs`, so your old `n_vus - 1` forgery now dies there).
Your `gates-32e9bd59` dumps, all six relations (pulled read-only, deleted after): **each accepted, 2/2 proofs,
94/94 negatives, manifest 96/96 agree, 0 problems**, union 2^-128.017 (fp4-nvf4 -128.025, fp8-ada-zk -128.03);
`neg_*_45` -> "claimed word off a chain end (non-canonical)", `neg_*_46` -> "operand word in a pad unit (non-canonical)"
(evidence `lanes/verify-rs-3/evidence/verify_rust_gates-32e9bd5_*.json`). All three problems in your
`gates-32e9bd59.log` (neg_45 accepted, the union 2^-127.0, "n_proofs mismatch: 2 distinct statements") come from
`/workspace/vrs3` predating 0db857a: accepting neg_45 added a second statement to the union. Rebuild it from 2dfbb90.

**One residual in Python's framing check (NIT):** `read_proof` keeps `t_pad` in `canon` whenever the key is present, so a
non-ZK proof with `{"sib_len":[..],"final_len":N,"t_pad":0}` is a second valid encoding (`0 == params.t_pad`). Your writer
only emits the key when `ybar` is non-empty. Rust rejects it: key iff t_pad > 0. Fix, e.g.
`if int(framing.get("t_pad", 0)): canon["t_pad"] = int(framing["t_pad"])`.
Red-team-3's 18 forged fixtures (4 framing re-encodings + 7 + 7 statement tampers) are all rejected by 2dfbb90.

## Update 23:18Z: the sparse-claim PCS cross-check is done without a GPU; the GPU ask shrinks to the padded case

`889343d` (pushed): Rust's reference prover writes a commit-first proof with two sparse terms as proto `Proof.to_bytes`,
and your tree's `proto/pcs.py` `verify_open` (32e9bd5, numpy path, run on my laptop with torch stubbed) **accepts it**. It
rejects all six negatives: value+1, weights+1, cells reversed, term dropped, no terms, eval value+1. Rust `pcs_verify`
accepts the same proof, so the sparse transcript (`b"sparse"` = cells u32 || weights, beta over m + K, `_Sparse`) agrees in
both directions (`backends/ligerito-verify/tools/pcs_sparse_crosscheck.py`; evidence
`lanes/verify-rs-3/evidence/pcs_sparse_crosscheck_python_verify_open.json`). Only sparse terms together with ZK padding
(t_pad 32) remain unchecked against Python. `tools/pcs_sparse_fixture.py` on a GPU still covers that, but it is low
priority: the ybar path is already cross-checked through your `--zk` gate proofs, and the two parts are independent.
* 23:22Z addendum: when you run `tools/pcs_sparse_fixture.py OUT.json` (the t_pad 32 case), check it on the pod with
  `ligerito-verify pcs-sparse --file OUT.json` (lane/verify-rs-3 >= 732e5d5, pushed). Expected: exit 0, t_pad 0 and 32
  honest accepted, 5 negatives rejected each. It reads proto's commit-first `Proof.to_bytes` directly.
