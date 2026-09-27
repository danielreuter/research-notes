---
cursor:
  subagentId: "bc-819f6247-2b10-5a85-9352-4e1d932f2125"
---

lane: one-stage-e2e · kind: handoff · from: vllm-serving-commit · created: 2026-09-27T11:00Z · status: final ·
repo: danielreuter/verity · origin: PR #119 @ b08eda03 (the served code)

# A4 run 2 (P6) is served: #101's whole layer 0, all six templates, GEMM as shared rows (6,771,765 units, partition `631d88f8…`)

## Where the files are

- **Small files:** `art:df875b6a10b681fe8775181cf975bbde93cad1b8ea3de33eb07a161cacbc1830`, with `registration.json` (v1),
  `index.json`, `registration-v0.json`, `window.json` and `members.json` (the byte-match record).
- **Member files:** `m<k>-pub-<n>.bin` and `m<k>-inst-<n>.bin` (about 2.4 GB, mostly M0's per-instance headers) are in the served run's
  record, `art:d2e35dd925dd3aeef17ad6e173ee756068ebc6c861be50fd653728ecfc0f7eca`, under `m0-files/serving/`. Fetch with
  `research data fetch art:d2e35dd9… --to DIR --path 'm0-files/serving/*'`, then put them beside the small files for `a4.py --served`.
  The `inst` files go to the prover only.

| k | template | n | pub sha512 (16) | inst sha512 (16) | inst bytes |
|---|---|---|---|---|---|
| 0 | RMSNorm Triton | 287 | `97d8eb809cacfc79` | `842972c8c74b9114` | 3.8 MB |
| 1 | GEMM K = 2048 (shared rows 861 / 21,504) | 6,171,648 | `1fcd722c0a582afb` | `703796eaa6ded9db` | 1.10 GB |
| 2 | RoPE | 11,480 | `7bc4a940a4f77610` | `35b966a81349f5b5` | 13.5 MB |
| 3 | RMSNorm fused | 287 | `e3984763115d0fe9` | `f66aa844a13fb502` | 6.2 MB |
| 4 | SiLU·mul | 287 | `e4d063212f1b06d8` | `fb36ae576f915222` | 14.2 MB |
| 5 | GEMM K = 8192 (shared rows 287 / 2,048) | 587,776 | `8691d1638e497524` | `14dfb89ddd98860b` | 134 MB |

## The registration

- **Built with your `verity_one_stage` at `e569e84a`** (`evidence/reg_members_v1.py`):
  - `served_domain` reproduces all 19 domains;
  - `leaf_layer` = SHA-512 of the canonical map from descriptor id to pub-file SHA-512 (`5044aea9…`);
  - **`R.check` returns ok with no codes.**
  - Record digest **`0d1f8f84e9ad74b2…`**.
- **Fields:** `program` `9733931f…`, `partition` `631d88f8…`, `population` 6,771,765, law `subset:1024`.
- **GEMM roots:**
  - K = 2048: `/x` `becfe175…` (861 rows), `/w` `10e9e1a1…` (21,504), `/y` `bd8309d0…` (6,171,648);
  - K = 8192: `/x` `c844c219…` (287), `/w` `8c699883…` (2,048), `/y` `4449be2a…` (587,776).
- **Refs:** exactly `verity/one-stage/gemm-grid/v0`, with groups `qkv_proj {287, 3072, 0, 0}`, `o_proj {287, 2048, 287, 3072}`,
  `gate_up_proj {287, 16384, 574, 5120}` and `down_proj {287, 2048, 0, 0}`. Repeated rows (#101's prompt repeats 100 tokens) are
  separate table rows, each with its own salt.
- **`window`:** `kind: served`, `run: r20260927-102240-f954`, `row` #101's key, committer `b08eda03`, `vllm_v1_run_root` `7adcef49…`,
  scope `model.layers.0.`.

## What was checked (1× L40S)

- **#101 with the scheme on:** verdict PASS, program `ccc21347`, manifest `90f81868`, and the `vllm-v1` run root **`7adcef49`,
  unchanged**.
- **Served rows = the capture,** for every captured instance in layer 0, with every port byte-equal (for GEMM, `x`, `w` and `y`
  through the refs):

  | template | captured instances compared |
  |---|---|
  | GEMM K = 2048 | 384 |
  | GEMM K = 8192 | 128 |
  | RMSNorm Triton | 256 |
  | RoPE | 64 |
  | RMSNorm fused | 8 |
  | SiLU·mul | 16 |

- **Served files = M0's writer:** all six members' `m<k>-pub/inst` are byte-identical to M0 **`e226a920`**'s own `write()`, headers
  included. That's the tables-as-given mode for GEMM, the per-instance files for the rest, and the descriptor-id `program_digests`.
- **Serving overhead:**
  - time: the hook took 17.3 s (10.0 s reading through openings, 6.6 s hashing on 16 workers);
  - bytes: public bodies about 84 MB, prover bodies about 158 MB.
- **Records:** served and byte-match run `r20260927-102240-f954` (`art:d2e35dd9…`), PRESERVED.

The salts are in the `inst` files in R2 custody. That's acceptable for this demo; in production the prover's files never leave the
prover side.
