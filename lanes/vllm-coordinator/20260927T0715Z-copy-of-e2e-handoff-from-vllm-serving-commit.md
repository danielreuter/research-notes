---
cursor:
  subagentId: "bc-819f6247-2b10-5a85-9352-4e1d932f2125"
---

lane: one-stage-e2e · kind: handoff · from: vllm-serving-commit · created: 2026-09-27T07:15Z · status: final ·
repo: danielreuter/verity · origin: PR #119 (lane/vllm-serving-commit @ efec3ad1; the served run used 384ca95e)

# Run A2: the served files are ready. #101's 183,680 RoPE heads as committed at serving time, with a v1 registration your `R.check` accepts

## Where the four files are

| file | where | sha512 (first 16) | size |
|---|---|---|---|
| `registration.json` (`verity/registration/v1`) | `art:fcc4e54280d19622923462278d9238764b8bfd12ff97342de114e91f96141ae2`, `registration.json` | record digest `2f1b6dabd916aa7d` | 2.6 KB |
| `index.json` | same art, `index.json` (also in the run record at `serving-rows/<row>/index.json`) | `38103fcf3c3c3caf` (= `window.index`) | 0.7 MB |
| `pub-183680.bin` (`rows: false`) | run record `art:4474915ccb3b85231ebfb1a080a3f9ad55c2ca13bfa6faedc10b5413d67378ab`, `m0-files/serving/pub-183680.bin` | `7ddb2832e26ecbe6` (= `leaf_layer`) | 97.7 MB |
| `inst-183680.bin` (prover only) | same run record, `m0-files/serving/inst-183680.bin` | `92faac7d769342ca` | 215 MB |

- **Fetch with** `research data fetch art:4474915c… --to DIR --path 'm0-files/serving/pub-183680.bin'`, and likewise for `inst-183680.bin`.
  The prover's file goes only to the prover process, never to the verifier's directory.
- **The same bundle also has** `registration-v0.json` (your `d27e6941` shape), `window.json` (roots, domains, bindings, timings) and
  `compare.json` (the byte-match record).

## The registration

- **Built after serving** with your `verity_one_stage` at `43122fa5`, exactly per your recipe:
  - `R.served_domain` reproduces serving's three domains;
  - `R.check(rec, prog, q, law, scheme, ports, leaf_layer=...)` returns **ok**, with no codes;
  - the script is `lanes/vllm-serving-commit/evidence/reg_v1.py`.
- **Fields:**
  - `program` `aa68f146…`, `partition` `f6e07626…`, `population` 183,680;
  - `law` `{"law": "subset", "k": 256}`, `scheme` `frame-v3-sha512/hm96-sha512`;
  - `leaf_layer` = SHA-512 of `pub-183680.bin`.
- **Roots** (full hex in the file):

  | port | root | leaves | domain |
  |---|---|---|---|
  | `x` | `c62a5fdedabff06c…` | 183,680 | `5dfb3bfb03d9fc01…` |
  | `cs` | `ee9ed668f1705ff5…` | 183,680 | `00ea5039f6f8196c…` |
  | `out` | `de08eeab57619cdc…` | 11,755,520 | `1f63c0d3b039001e…` |

- **`window`** (serving's source):
  - `kind: served`, `run: r20260927-061338-8809`, committer `384ca95e`;
  - `served_program` `080f3a50…` (#101's Program SHA-512), `served_program_digest` `ccc21347…`;
  - `vllm_v1_run_root` `7adcef49…`, `index` `38103fcf…`, `order` `verity-vllm/serving-rows/order/v0`.
  - `row` is `null` in this run: the hook didn't receive the row number. It's provenance only and outside the domains, and
    `efec3ad1` fixes it for later runs. This is row #101.

## What was checked on the GPU (1× L40S, run `r20260927-061338-8809`; byte-match run `r20260927-065834-9db4`)

- **Scheme off:** #101 equals the record: verdict PASS, program `ccc21347`, manifest `90f81868`, run root `7adcef49`.
- **Scheme on:** verdict PASS, the same program, manifest and `vllm-v1` run root `7adcef49`. Serving committed all 183,680 heads in
  M0's format; every row was read through an opening under that run root.
- **Served rows = the capture:** your 1,024 captured heads (`art:16825154`) were all located in the served population, and their
  `x`, `cs` and `out` equal the capture byte for byte.
- **Served files = M0's `write()`:** M0's `write()` at `e51e2b86`, fed the served rows, serving's salts and serving's domains over
  all 183,680 heads, gives `pub-183680.bin` and `inst-183680.bin` identical to serving's, headers included.
  - The prover file's body was rebuilt from `write()`'s own expression with one `np.concatenate` hoisted: M0's loop is quadratic
    in n, and I've reported it to flock-netlist.
  - The circuit pin is `cdcbd876…` and the class `3927f513…`, as you named them.
- **Serving overhead:**
  - the hook took 14.6 s in the Commit (9.6 s reading, 4.7 s hashing on 16 workers), against a Commit stage of 190 s with the
    scheme on and 193 s off;
  - it hashes 70.5 MB of values, against vllm-v1's roughly 908 MB per run;
  - it keeps 70.5 MB public and 117.6 MB private.

## One note

The salts are in the prover's file, which sits in R2 custody with the run. That's acceptable for this demo because R2 is our own
storage. In production the prover's file never leaves the prover side.
