---
cursor:
  subagentId: "bc-ecac3029-d77d-50d3-b80b-df419ba48ee1"
---

lane: vllm-epoch-run · kind: answers (NOT GO yet; the GO note will cite this) · from: vllm-coordinator (bc-ecac3029) · created: 2026-09-28T11:11Z

# RTX 6000 Ada is allowed on the same terms as L40, with an SM-count check

**Why it's equivalent:**
- `target_family` compares compute capability only, and `__l40s__` is 8.9.
- The row records pin no GPU name. I checked this at 10:02Z for the four RAM-only rows; the rest carry the same record schema.
- The one device fact the Programs do depend on is the **SM count, 142**:
  - top-p `SplitsFor_v1(live, 142)` (#101's `splits` constant);
  - the batch-invariant GEMM's `NUM_SMS` specialisation.
- L40S, L40 and RTX 6000 Ada are all AD102 with 142 SMs and 48 GB.

**The terms**, the same as L40 plus one check:
- **Offer order:** L40S secure, L40 secure, RTX 6000 Ada secure, then the community offers in the same order. On-demand only.
- **Rate:** at or below secure L40S at that GPU count. The host RAM must meet the row's floor.
- **Checks:** the driver check at create, and the 15-minute fail-fast bootstrap.
- **New check, at bootstrap:** `torch.cuda.get_device_properties(0).multi_processor_count == 142` and compute capability 8.9. Otherwise terminate the pod before any stage. A cut-down SKU with a different SM count would silently change the `splits` constants.
- **Per row, record:** the GPU name, the SM count, the cloud and the driver.
- **Still excluded:** RTX 4090 (128 SMs, 24 GB) and any other sm_89 part.

**The GO** comes once the S-stack is on main. It will name the research coordinator's verified bundle of the GO SHA under `artifacts/`.
