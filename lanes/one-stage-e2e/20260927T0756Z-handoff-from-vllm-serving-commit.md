---
cursor:
  subagentId: "bc-819f6247-2b10-5a85-9352-4e1d932f2125"
---

lane: one-stage-e2e · kind: handoff · from: vllm-serving-commit · created: 2026-09-27T07:56Z · status: final ·
repo: danielreuter/verity · origin: PR #119 (lane/vllm-serving-commit; the served run used efec3ad1)

# Run A2: the re-served files under the canonical partition `17478e85…`

Replaces `20260927T0715Z-handoff-from-vllm-serving-commit.md` for the canonical A2. The earlier files still stand for your fallback,
which binds the pre-canonical object `f6e07626…`.

## Where the four files are

| file | where | sha512 (first 16) | size |
|---|---|---|---|
| `registration.json` (`verity/registration/v1`) | `art:9ab217a124a442ca2a52ea0f2732f153c06c16966e6ae8ea4f9eea2c61449e52`, `registration.json` | record digest `7b7a1ca392b8735a` | 2.6 KB |
| `index.json` | same art, `index.json` | `32ad110fc48e47b7` (= `window.index`) | 0.7 MB |
| `pub-183680.bin` (`rows: false`) | run record `art:fa1b749f8bb018f1cd3ca154bf62c2cb31c7e142dd3db35b4e272782ac7d6a72`, `m0-files/serving/pub-183680.bin` | `8280be7e932b392b` (= `leaf_layer`) | 97.7 MB |
| `inst-183680.bin` (prover only) | same run record, `m0-files/serving/inst-183680.bin` | `867be781ca76001a` | 215 MB |

- **Fetch with** `research data fetch art:fa1b749f… --to DIR --path 'm0-files/serving/pub-183680.bin'`, and likewise for `inst`.
- **The same bundle also has** `registration-v0.json`, `window.json` and `compare.json`.

## The registration

- **Built with your `verity_one_stage` at `761c4402`** (`evidence/reg_v1.py`). `R.served_domain` reproduces all three domains, and
  `R.check` returns ok with no codes.
- **Fields:**
  - `program` `aa68f146…`, `partition` `17478e85…`, `population` 183,680;
  - `law` `subset:256`, `scheme` `frame-v3-sha512/hm96-sha512`, `leaf_layer` = SHA-512 of `pub-183680.bin`.
- **Roots:**

  | port | root | leaves | domain |
  |---|---|---|---|
  | `x` | `b6f268d77b4b3235…` | 183,680 | `99816a88463c65f7…` |
  | `cs` | `339aae1c9e1a04ec…` | 183,680 | `1eeb2c4e03da9734…` |
  | `out` | `26215244baa6dd94…` | 11,755,520 | `eb90ad437c60d10a…` |

- **`window`:**
  - `kind: served`, `run: r20260927-073101-9c1c`, `row: llama32-1b__bf16__l40s__tp1__b1__i256__o32__mixed__stoch-t0.8-p0.95__bi-eager`
    (#101), committer `efec3ad1`;
  - `served_program` `080f3a50…`, `vllm_v1_run_root` `7adcef49…`, `index` `32ad110f…`, `order` `verity-vllm/serving-rows/order/v0`.

## What was checked (1× L40S, run `r20260927-073101-9c1c`)

- **The row:** #101 with the scheme on, verdict PASS, program `ccc21347`, manifest `90f81868`, `vllm-v1` run root `7adcef49`
  (unchanged).
- **The byte-match:**
  - your 1,024 captured heads are all located, and `x`, `cs`, `out` are byte-equal;
  - M0's `write()` (`e51e2b86`) over all 183,680 served heads, with serving's salts and domains, gives `pub`/`inst` identical to
    serving's;
  - the pin is `517b72e7…`, as you named it.
- **The serving hook:** 15.1 s (9.4 s reading through openings, 5.0 s hashing).

The salts are in the prover's file, which sits in R2 custody. That's acceptable for this demo; in production the prover's file never
leaves the prover side.
