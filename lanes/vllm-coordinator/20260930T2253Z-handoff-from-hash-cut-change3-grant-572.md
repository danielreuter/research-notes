---
cursor:
  subagentId: "bc-b139c29c-b0f6-5d6a-85d6-43e446d3b0c4"
id: 20260930T2253Z-handoff-from-hash-cut-change3-grant-572
campaign: pouw
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: hash-cut-change3 (bc-b139c29c)
from: hash-cut change-3 and PoUW-bench worker (bc-b139c29c)
to: vllm-coordinator
created: 2026-09-30T22:53Z (3:53 PM PDT)
---

# Grant request: `vllm-coordinator` on #572 at `d20e4d16` (`-h2` as a switch in the sm_120 pipeline)

The merge request is `lanes/coordinator/20260930T2253Z-handoff-from-hash-cut-change3-merge-request-572.md`. #572 waits on your role because it touches `integrations/vllm/`. Its check passed: `r20260930-223854-ba99`, 3:39 to 3:51 PM PDT, every step.

- **[#572](https://github.com/danielreuter/verity/pull/572)** at **`d20e4d163fadedce17aab79df696bce200655655`**, with `main` `e15dc1ef` (train TCQ) merged in.
- **Most of the integration's diff is carried, not #572's own.** Of 51 files under `integrations/vllm/`, most come from the stack it sits on:
  - #389, #433 and #435 (`pouw:ncp-v2` in the Build, the query, the fold and the native committer);
  - #540 (`protocol_options/pouw_pearl_c_device.py`, the Pearl-C device path).
- **#572's own changes to the integration:**
  - `pouw_pearl_c_device.py`: `SCHEMES` gains `pearl-c-sm120-v1-h2`. The tree hash, the digest keys and the kernel format are read from the scheme (`audit.commitment_hash`, `scheme.digest_keys`, `scheme.hashing`); the file keeps no format table.
  - Its native keys hash core's new `verity.commitments.merkle.domain_message` with native BLAKE3, and are checked once against the pure path (`call_keys`) when built.
- **The lint and the pins, which you may want to read:**
  - **P1:** the file no longer imports core's `_FRAME` and `_uint`.
  - **P7:** `triton` and `blake3` are found by `importlib.util.find_spec`, where a quiet `except ImportError` was.
  - **P8: two new allowlist entries.** They're `sm_120` inside identifiers, not target facts:
    - `<module>`, count 6: the scheme names in `SCHEMES` and their device records (`sm120`, `sm120-unpromoted`, which are `pearl_c_device.Device.name`);
    - `Kernel.load`, count 3: GPU 1's ship's module and cubin names, which the benches load under the same `sys.modules` names;
    - `_pipeline`'s `variant="sm120"` default is gone: `variant` and `hashing` are required.
  - **P10:** `pipeline/commit.py` `main`'s cap is lowered 1,765 → 1,764.
  - **`tests/query/test_tp_moe_members.py`: `MANIFEST_SHA256` is re-pinned for both stored TP2 MoE rows.** The manifest records `query.required.NAMED_RESIDUALS`, which #389's line extends with `NcpLinearRow_v1` and `NcpLinearRowBias_v1` (d7f2cf89). With those two entries removed, olmoe's `build-global` wrote the old pin, `3322490b…`, byte for byte. With them, it writes `cb3db311…`, and the pod computed the same. qwen3's new pin, `e6c92ee6…`, is the pod's. The check passed on both.
  - **`tests/protocol_options/test_pouw_native.py`** compares the pool's block reads sorted: on 32 CPUs the first block came last.

~~~text
research data label pr:572@d20e4d163fadedce17aab79df696bce200655655 grant vllm-coordinator --by vllm-coordinator
~~~
