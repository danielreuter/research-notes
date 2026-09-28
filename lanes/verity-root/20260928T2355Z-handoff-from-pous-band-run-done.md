---
id: 20260928T2355Z-handoff-from-pous-band-run-done
campaign: verity
lane: verity-root
kind: handoff
status: final
repo: danielreuter/verity
origin: pous
---

# Band-codec encoded vLLM run: done, pods terminated, $2.00 spent against the $1.50 cap

Closes `20260928T2240Z-handoff-from-pous-opus-limit-band-pod`, and reports on your 21:32Z approval. From bc-13eada34.

- **Pods:** both are terminated, and no `vy-pous-band-e2e` pod is live.
  - `evz815gmolzxff`, 21:55:22–22:11:52Z: $0.30.
  - `kt87ut6jlqpi81`, 22:19:11–23:52:35Z: $1.70. The local guard terminated it on its deadline.
- **Spend: $2.00, $0.50 over the $1.50 cap.**
  - The guard ran on the agent's VM. That VM was suspended from about 22:45Z to 23:52Z, when the usage limit cut
    the worker off, so nothing enforced the cap or the 60-minute pod limit in that window.
  - The second pod did no work: its launch stalled shipping the source tree over ssh, and the run never started.
  - **Fix on our side:** the next GPU hold runs under your fleet guard rather than a guard on the agent's VM.
- **Run 1, `r20260928-215545-dbac`:** fetched, verified and PRESERVED. Its commit is `30519bac` on #333. It is recorded
  as failed, because two verdicts failed:
  - **Serving from the band-encoded `C` is bit-exact:** tokens and logprobs equal plain serving on all 4 prompts.
    Every load check passed, and the GPU's layer-0 decode equals the reference decode.
  - **The GPU's root did not match `vk`, and the honest audit failed:** every one of 2,640 answers was wrong, though
    every one was on time.
  - **The cause is in the verifier, not the server.** The verifier encoded the band with P3's primitives (the overwrite
    chain) instead of the band's (`DenseChain`). That gives another codeword of the same `W`, which decodes, but not
    the one the GPU computes. It is fixed on #333 (`4f31fc8f`), and the CPU test now checks against the band's
    canonical encoding.
  - The negative control was rejected, as it should be.
  - **The slowdowns in this run used the default kernels**, not the tuned ones, so they are not comparable with P3's
    1,500× and 270×:
    - prefill 2048 × 4: 146,883 → 1,010 tok/s, 145×;
    - decode batch 1: 86.7 → 0.166 tok/s, 524×.

    The rerun passes the band run of record's kernel flags (`30d53306`).
- **Request: one rerun.** One L40S under your fleet guard, about 20 minutes and about $0.40, with a cap of $0.60, from
  #333 at `30d53306`. It measures the audit with the fixed verifier and the tuned slowdowns. The pod is terminated once
  the run is fetched. Please give a window and a balance floor, or say no.
