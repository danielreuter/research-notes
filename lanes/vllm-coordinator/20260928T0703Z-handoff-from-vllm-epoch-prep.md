---
cursor:
  subagentId: "bc-4da25697-24f7-5a56-831c-91486b81150d"
---

lane: vllm-epoch-prep · kind: handoff · from: vllm-epoch-prep (bc-4da25697) · created: 2026-09-28T07:03Z

# S1b built: the host call-boundary source covers 100% of #74 and #57 on CPU; #57 carries a host-time cost. Push blocked again (auth)

**Pushes.** GitHub auth failed again at 06:59Z. A retry loop pushes every 10 minutes. Until then:
- **S1** (#232) has one new commit, `017e22cf`. `moe_plane_kind`'s five by-name allowlist entries move with it to `query/manifest/format.py`. `tests/test_no_by_name_rules.py` failed at `4e6ce10f` and passes now.
- **S1b** is `cursor/epoch-s1b-host-boundaries-150d` @ `5a423c08`, stacked on S1 `017e22cf`.
- Both are in the store's `artifacts/vllm-epoch-prep-s1-017e22cf-s1b-5a423c08.bundle`. I'll open S1b's PR as soon as the branch is pushed.

**What S1b is.** `acquire/sources/call_boundary_source.py` is attached automatically whenever the manifest names `call_boundaries` identities.
- **Where the words come from:** per module body and committed step, a forward pre-hook reads the module's arguments and weights. It evaluates the body's Program rows on the host through `verity.evaluation.evaluate_batch`, with the row kernels, exact, NaN payloads included. Then it acquires every identity over its element range.
- **The rows:** come from the Build dir whose program digest is the manifest's (`--program-dir` / `--programs-root`).
- **Fails closed:**
  - a body that reads anything but its arguments, weights and literals leaves its identities uncovered, and the Commit exits 3 naming them;
  - an argument of the wrong shape or width is a collector error naming the site;
  - multi-request and multi-rank manifests are refused for now.
- **Coverage on the stored Programs** (static plan):
  - #74 LP73_T1: 576 / 576;
  - #57 LP31_T52: 41,870 / 41,870.
- **One-step host evaluation equals `verity.evaluation.evaluate`:** #74 `down_proj` (73 rows with edge values), and #57's input and post-feedforward norms.
- **Tests** (`tests/acquire/test_call_boundary_source.py`, 7):
  - IR words on every identity;
  - edge words through the #57 chain and `Fp8GroupQuant_v1`;
  - refusals and collector errors by name;
  - the FP8 GEMM replay passes on the host x_s and fails on a flipped one;
  - `CLAIMS`.
- **Lints** (P1–P12, by-name, dead modules): pass. `commit.py` stays at its caps.

**The #39 hook.** `call_boundary_source.CLAIMS` is a list of `identity -> source name | None`. cross-call-check's pre-bias tap appends one claim for its `qkv_proj` pre-bias Gemm identities. The host plan then leaves those identities to the tap, and attaches nothing if every identity is claimed. The tap itself attaches through S3's `taps.SOURCES` / `TapSources` / `row_records.applicable_taps`, like the other taps.

**x_s for S4's `scale_products`.** The source exposes `activation_scales(linear, engine_step)`: the committed x_s words. When S1b sits on S4, S4's `cutlass_scaled_mm` wrapper will take x_s from there instead of the launch's `a_scales`. It's a small commit once S4 is on main, before S1b merges.

**Decision needed: #57's host cost.**
- #57 has a second chain besides the norms: Gemma's final logit softcapping. The pre-softcap `lm_head` Gemm output (K = 2304, N = 256,000) is a Call boundary inside `logits_processor`.
- Evaluating it on the host costs about 48 s per decode step; the norms add about 20 s per step. That's roughly **70 minutes of host time per #57 Commit**, and about 10 GB of transient memory per logits step.
- **Options for S1d:**
  - (a) accept the cost, since #57 runs last and is FAIL class;
  - (b) capture the pre-softcap logits with a tap through `CLAIMS`, like #39's pre-bias tap. Cheap and exact, and it has the same shape as cross-call-check's work.
- **My recommendation: (b), if cross-call-check can take it alongside #39.** Otherwise (a).
- #74 is trivial either way: its Gemm-free quant evaluates in under a second per step.

**What a GPU run must still verify:**
- the real forward arguments match the argument rule (Gemma's norm takes `(x, residual)`);
- no collector errors;
- the consuming replay passes;
- the arena sizing holds (5.9 MB per token on #57);
- the run is eager, since pre-hooks don't fire in CUDA graphs.
