---
lane: ligerito-relation
kind: report
created: 2026-09-23T18:30Z
branch: lane/ligerito-relation (worktree ~/projects/verity-main-wt/ligerito-relation)
owns: backends/direct/ligerito/{prove.py, proof.py, run.py} (+ tests beside them)
pod: vy-ligerito-relation-veritor-campaign iwf3hy58efuq94, NVIDIA A100-SXM4-80GB, $1.59/h, created 18:42Z, watchdog 8 h
status: superseded
---

CHECKPOINT none (00:03Z) [superseded] by ligerito-relation-2 (coordinator)
# ligerito-relation — end-to-end Ligerito prover + verifier for the dot-product relations

Pod note: the brief says H100 80 GB; none was affordable inside the $12 cap for the whole night ($2.69/h) and the A100 80 GB PCIe
had no stock, so the dev pod is an **A100-SXM4-80GB ($1.59/h)** — same 80 GB headroom for the zero-check tables. The comparable
number (deliverable 5) is on a reference RTX 4090.

CHECKPOINT 3592bd0 18:50Z — deliverable 1 skeleton lands: fp8-ada gate 12 VUs (l = 256, N = 2^22) local coins, honest + 30 negatives, 0 failures.
CHECKPOINT 0cac5ae 18:53Z — first 4096-VU run (N = 2^30, one batch, set B pow2 L = 5): **t.total 1.51 s on the A100 (unoptimised glue), proof
695,718 B, in-process verifier accepts (1.65 s Python), 92 coins, peak 43 GiB, union 2^-128.0**. Fiat-Shamir gate fixture published (below).

CHECKPOINT d207c1b 19:35Z — deliverable 1 shipped: fp8-ada 4096 VUs one batch, local coins, **A100 t.total 0.82 s** (witness 0.16, commit
0.10, zero-check 0.45, PCS open ~0.10), 695,718 B, gate green (honest + 30 negatives incl. cheating zero-check provers on violated
witnesses), ligerito-pcs-fast's `pcs.commit`/`pcs.open` integrated (byte-identical to my adapter and the reference: `prove_test.py`).
CHECKPOINT 53eb6de 20:05Z — live coins: `prove.StreamCoins` = `transcript.LiveCoins` over live-2's `ChallengeStream` (slot k =
`expand_challenge(ctx, k, label, r_k, 32)`, MSG k = BLAKE2b of the prover's absorbs since slot k-1); bench `--coins live --verifier
tcp://… --window W --batch-vus B`; dumps carry `.coins` + the stream binding (commitments, openings, labels; verify-dir re-derives
every slot). First live session against `vy-live2-verifier` (EU-CZ, `live-verifier@71dbab04b8b3`) ACCEPTED (32 VUs, 2 batches, W = 2,
64 rounds, RTT from my US A100 ~130 ms → 8.5 s per batch: the live mode is RTT-bound, R x RTT). Gates bf16-hopper and fp8-hopper
green (4 positives, 80 negatives, 0 failures each, python dump verify 82/82).

CHECKPOINT 82f3a6e 20:20Z — reference RTX 4090 numbers (table below); `--zk` partial (ligerito-zk's row masks in free rows + `z_to_f`
index map + `permute_point`) works end to end with a one-line sumcheck.py change I asked ligerito-sumcheck-2 for; bf16-ampere gate
green (80 negatives). A100 dev pod TERMINATED 20:18Z (~$2.5); 4090 TERMINATED 20:19Z (~$0.3). Next dev GPU only when a ZK hook lands.

### fp8-ada, 4096 VUs — reference RTX 4090 (24 GB), NON_ZK_PROOF_DIAGNOSTIC, commit 82f3a6e

The 4090 cannot hold one 4096-VU batch (peak 45 GiB on the A100; 2048 VUs = 22.8 GiB OOMs on 23.5 GiB), so 4096 VUs = **4 proofs of
1024 VUs** (N = 2^28 each, L = 5, 86 coins each). Verify = the Python verifier (Rust has no LGTO0001 reader yet).

| mode | t.total | proof bytes (4096 VUs) | verify | vs Ligero (0.17 s local / 0.252 s live / 66 MB) | artifact |
|---|---|---|---|---|---|
| local coins | **1.096 s** | **2,379,352 B** (2.38 MB) | 4.67 s Python (1.17 s/proof) | 6.4x slower, **27.7x smaller** | art:88ed10df… |
| live, loopback verifier (RTT 0.1 ms), W = 1 | 1.245 s | 2,378,964 B | 5.51 s | protocol overhead w/o network +0.15 s | art:8f3047e2… |
| live, loopback, W = 2 | 1.347 s | 2,382,996 B | 5.92 s | (two 1024-VU proofs in flight: no gain, GPU-bound) | art:0471af3d… |
| live, `vy-live2-verifier` EU-CZ (RTT ~99-120 ms), W = 2 | **18.1 s** | 2,381,524 B | 9.15 s | 72x slower: 86 rounds x RTT per proof | art:0833c38c… |

A100-SXM4-80GB (dev pod, same code): one 4096-VU proof **0.845 s, 695,718 B (95x smaller than Ligero)**, verify 1.66 s Python, peak
45 GiB (art:25622e70…); 2 x 2048: 1.076 s / 1.28 MB (art:345a257c…); 4 x 1024: 1.49 s / 2.38 MB (art:64fe0eab…); live to EU-CZ one
4096 proof 12.5 s (92 rounds x ~125 ms; art:ca313021…), 4 x 1024 W = 4 11.75 s (art:47c270cf…).

What the live numbers say: an interactive Ligerito proof costs **R x RTT** (R = 86-92 rounds) on top of the prover — 9-12 s per proof
at ~100-125 ms, ~2.5-3 s at live-2's 30 ms EU-RO path — whatever the window, and windowing across batches is capped by device memory
(each in-flight proof holds its zero-check tables: W = 2 at 1024 VUs is the 4090's limit). Ligero's live mode has ~3 rounds. With a
co-located verifier (loopback) the stream adds only 0.15 s. So for the live mode the coin count (sumcheck-2's LGSC0003 target 40-50)
and the verifier's distance matter more than any prover optimisation; Fiat-Shamir Ligerito has no such floor.

## Status by deliverable

1. fp8-ada end to end, local coins, non-ZK — **shipped** (numbers above; 4096-VU dumps are ~0.7 MB/proof).
2. Rust verification — **blocked on ligerito-verify-rs** (no LGTO0001 reader on `lane/ligerito-verify-rs` @ ff9d4c3 yet); fixture + format
   published 18:55Z.
3. ZK + live coins — live coins **done** (live sessions ACCEPTED by live-2's verifier; dumps re-derive every coin from the stream's
   commitments/openings). ZK: my side **done** as `--zk` (partial: masks + index map), blocked on (a) ligerito-sumcheck-2: the
   one-liner (zero only virtual rows in `w_only`), Libra masks in the three sumchecks, shift-claim reduction, product-row constraint;
   (b) ligerito-pcs-fast: per-column RS padding + sparse round-1 terms. Handoffs 19:55Z / 20:15Z.
4. Other relations — bf16-hopper, bf16-ampere, fp8-hopper **green** (12 VUs, local + Fiat-Shamir, 80 negatives each, 0 failures; gate
   artifacts art:315507b4…, art:775ddbb3…, art:8d177efa…). fp4-nvf4 **blocked**: layout.py has no component chain ends (its claim is an
   FP32 word > p, three components); handoff to ligerito-sumcheck-2 20:10Z with the exact change.
5. 4090 comparable number — **done for non-ZK** (table above); rerun (≤ 35 min of 4090) if ZK lands.

## Interface (LGTO0001 / LGTS0001 / LGVK0001; `backends/direct/ligerito/proof.py` is normative — its docstring has the same text)

All integers little-endian; field elements `u32` in `[0, p)`, `p = 2^31 - 2^27 + 1`; extension elements 6 of them
(`F_p[x]/(x^6 - 31)`, coordinate i = coefficient of x^i). `str` = `u32 len | utf-8`.

~~~text
LGTS0001  statement   magic | str relation | 32 B sys_id (ligero protocol.system_id) | 32 B vk_sha256 | u32 l | u32 steps | u32 K
                      | u32 S | S x u32 n_vus (0 = pad sub-batch) | u8 word_bytes | u8 y_bytes
                      | for every s with n_vus[s] > 0: l x K a | l x K b | l x y   (the relation's word widths: exactly the
                      operand/claimed words of ligero-statement/v4 per sub-batch, units in column order, pad units zero words)
LGVK0001  key         magic | str relation | 32 B sys_id | u32 m | u32 n_i | u32 n_k | u32 K | u32 n_links | n_links x u32 c_row
                      | u32 n_virt | n_virt x (str name, u32 row) | 3 x (u32 nnz | nnz x (u32 k, u32 row, u32 coef))  [A, B, C]
                      = layout.layout_for + layout.constraints (functions of the relation only; independent of l, n_vus)
LGTO0001  proof       magic | u32 len | params JSON (absorbed verbatim) | u32 len | framing JSON (not absorbed)
                      | u32 len | zero-check sumcheck (ligerito-sumcheck LGSC0002) | L x 32 B root_i
                      | for i < L: k'_i x (3 x 6 u32) PCS column-sumcheck messages (g(0), g(1), g(2))
                      | for i < L: |S_i| x W_i u32 opened codeword rows (W_1 = 2^{k'_1} base words; W_i = 6 * 2^{k'_i},
                        plane-major, for i >= 2) | sib_len[i] bytes BLAKE3 multi-path (proto merkle_multi.plan order)
                      | 2^{k_L} x 6 u32 final vector y_L
    params  (compact JSON, sorted keys)  {"coins","kprime","l","n","n_claims","order":"row-major","queries","rate_log2",
                                          "relation","splits","zk"}
    framing {"sib_len": [...], "final_len": int}
~~~

**Committed polynomial.** `w` = the layout's `z` (`2^n_i` rows x `C = S*l` columns) with the virtual rows `[m, 2^n_i)` zeroed,
**ROW-MAJOR**: flat index `x = c + C*i` (column `c = s*l + j`, row `i`). PCS variable `t < n_c` = column bit `t`, `t >= n_c` =
row bit `t - n_c`. The sumcheck's claim points are row-bits-first (`p_i || p_c`, ligerito-sumcheck §3); they enter the PCS rotated
as `(p_c || p_i)`. (Deviation from the brief's `f[i + R*c]`: row-major commits `z` in place — no 4.3 GB transpose, which matters on
the 24 GB 4090 — and makes a round-1 PCS column a block of whole layout rows, the geometry `zk.ZkParams` assumes. The only cost is
the rotation above, on 30 x 6 words.)

**Claims.** `J = 1 + n_links` (4 for fp8-ada): `w(r_i, r_c)` and `w(c_x, rho)` for each chain row `c_x` — `sumcheck.verify` returns
them (points `(n, 6)`, values `(6,)`), values are LGSC0002's `values`.

**Transcript** (ONE Coins object, `transcript.py`):

~~~text
absorb("lgto/params", params JSON bytes as in the file) | absorb("lgto/stmt", sha256(statement bytes)) | absorb("lgto/vk", sha256(key bytes))
| absorb("root", root_1)
| the zero-check (ligerito-sumcheck §3 call order: challenge "zc/tau", ..., absorb "values")
| absorb("z", the J claim points in PCS order, (J, n, 6) u32) | beta <- challenge("beta", J)
| proto/pcs.py from its first column round on, running claim sum_j beta_j v_j, J eq terms with coefficients beta_j:
    k'_1 x [absorb("g", g) -> challenge("r", 1)];
    for i >= 2: absorb("root", root_i) | indices("S", n_{i-1}, |S_{i-1}|) | absorb("rows", u32 rows) | absorb("sib", siblings)
               | challenge("alpha", 1 + |S_{i-1}|) (alpha_0 scales every old term incl. the J eq terms) | k'_i x [g -> r];
    absorb("y", y_L) | indices("S", n_L, |S_L|)
~~~

Differences from proto's `verify`: no `header` / `z` / `v` absorbs at the start (the params JSON + statement + key digests replace the
header; the claim points are absorbed after the zero-check), and J eq terms instead of one. The final check sums
`coef_j * <eq(z_j restricted to the last k_L vars), y_L>` over the J eq terms plus the geometric terms, exactly as proto does for one.

**Public rows** (the verifier's virtual rows, `layout.public_rows`): per sub-batch `s`, columns `[s*l, (s+1)*l)`: `const` = 1;
`start/link/end` = `ligero/chain.py Layout(l, n_vus[s], steps).masks()` (`in_vu = j < steps*n_vus`; `start = !in_vu | j%steps == 0`,
`end = in_vu & j%steps == steps-1`, `link = in_vu & j%steps != steps-1`); `y16` = the statement's `y` words; `pub:<name>` =
`rel.public_vectors(a, b)[name]` (the same decode ligero-verify's `public_pins_words` does for Ligero statements); `next:*` rows are
NOT public (the shift sumcheck proves them). Pad sub-batch (`n_vus[s] = 0`): `a = b = 0` words (relchain `_pad_unit`), `y = 0`, masks
with `n_vus = 0`. The verifier rejects off-domain words (`public_vectors` raises, e.g. E4M3 NaN `0x7f`) and `y >= 2^y_bits`.

**Coins in dumps.** `manifest.json` entries carry `"coins"`: `"fiat-shamir"` (`FiatShamirCoins()`, label `ligerito-proto/v1`),
`"local"` (`transcript.LocalCoins(coins_seed)`: `shake256("local-coins" | seed u64 | counter u64)`, absorbs ignored), or `"live"`
(`coins_file`: `u32 count | 32 B per coin`). Use the fiat-shamir dumps first: they bind every message.

**Dump layout** (`ligerito-verify batch --dir D`): `D/key.bin` (LGVK0001), per proof `X.stmt` (LGTS0001) + `X.lgto` (must accept) or
`X.lgto.neg` (must reject), `D/manifest.json` `{"format", "relation", "l", "vus", "commit", "kind", "files": [{"proof", "stmt",
"expect", "coins", "coins_seed", "proof_bytes", "proof_sha256", "stmt_sha256", "python_verdict": {"accepted", "reason"}, "name"?}]}`.
The Python cold verifier over a dump: `python -m backends.direct.ligerito.run verify-dir D` (writes `D/verify_python.json`).

## For ligerito-verify-rs

* Fixture (Fiat-Shamir, fp8-ada, 12 VUs, l = 256, S = 4, N = 2^22, L = 3): `~/.research/notes/lanes/ligerito-relation/evidence/fixture_fp8ada_l256_fs/`
  (11 MB): 1 honest `.lgto` + 30 `.lgto.neg` (wrong y proved / in the statement, off-domain operand, flipped operand bit, broken chain
  link, c_0 != 0, accumulator bits, one row of every class incl. quadratic `prod` and lookup `sel`, cheating zero-check provers on
  violated witnesses, 9 byte tampers, a statement with another n_vus). Python cold verify: 31/31 as expected. Every `.neg` has its
  Python reject reason in the manifest.
* The zero-check part is ligerito-sumcheck's LGSC0002 verbatim; your `sumcheck-fixture` code applies after the three `lgto/*` absorbs +
  `root`. The PCS part is proto's verifier with the changes listed under Interface.
* **Live-coins fixture** (20:20Z): `evidence/fixture_fp8ada_l256_live/` (1 MB, 2 proofs, 16 VUs each, coins from live-2's verifier
  EU-CZ session c20260923T195724Z-ac8a): manifest `"coins": "live"`, `coins_file` (`u32 count | 32 B slots`, replay with LiveCoins
  semantics: slot k seeds `SHAKE-256(slot || u64 sub)`), plus `stream_binding` = {statement, commitments, openings, labels} so a verifier
  can re-derive slot k = `SHAKE-256(b"ligero-chal|v1|" | blake2b(b"ligero-chal-ctx|" | u32 len(stmt) | stmt | c_0..c_{R-1}, 32) | u32 k |
  u32 len(label) | label | r_k)[:32]` and check `coin_commit(r_k, s_k) == c_k` (ligero/live.py). Optional for you; the slots suffice.
* **ZK order** (`params.zk = true`, `order = "zk-interleaved"`; not in any fixture yet): only virtual rows `[m, m + n_virt)` zeroed;
  index map `x = (c mod 2^a) + 2^a i + 2^{a+n_i} (c >> a)`, `a = k_L - 3`; points enter the PCS as `(p_c[:a] || p_i || p_c[a:])`.
* Soundness: `Prover.soundness` (params.LigeritoParams.soundness at the proof's dims + the beta term) gives 2^-128.0008 at N = 2^30.

## Discrepancies

* (none yet)
