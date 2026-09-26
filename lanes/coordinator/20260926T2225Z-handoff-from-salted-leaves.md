lane: coordinator · kind: handoff · from: salted-leaves · created: 2026-09-26T22:25Z

# E4 ready for review: PR #93 adds hm96-sha512/v1, frame-v3-sha512 and vllm-v1-sha512 (opt-in), stacked on PR #88

- **Merge order:**
  1. PR #88 @ a53900df, as `hm96-sha256/v1` (the C1/C2 handoff of 21:58Z).
  2. [PR #93](https://github.com/danielreuter/verity/pull/93): `cursor/sha512-commitments-18a8` @ cd00f704, based on a53900df.
     Retarget it to main after #88 merges.
- **What it covers:**
  - **E4 for hm96:** `hm96-sha512/v1`, with the same hiding bound. The key is fixed and public: SHA-512 counter mode over a public
    label.
  - **E4 for the frame roots:** SHA-512 variants of both framings (frame-v3 §6, vllm-v1 §10).
  - **E1, in part:** the setup claim for how the pinned keys are derived (hm96 §2a), and `verity.claims` gains `hash-derived-key`.
  - All of it is opt-in, and every SHA-256 default is byte-identical.
- **Evidence:**
  - per-row costs: `r20260926-221723-71aa`, `art:b9bb217f`;
  - tree costs: `r20260926-221754-0cce`, `art:a7a8ccce`.
- **Headline:** hm96-sha512 ANDs per row are 3.01× the keyed-BLAKE3 row at 3 KB, and 1.33× hm96-sha256. It stores +192 bytes per row.
  The SHA-512 framings commit 1.3–1.4× slower on a CPU with SHA-NI.
- **Needs a red team.** It changes the frame-v3, vllm-v1 and hm96 references; the SHA-256 bytes are pinned by the existing vectors.
- **Left for the re-baseline:**
  - the integration's SHA-512 committers, Python and CUDA (vllm-v1 §10 lists them);
  - E2, the GPU hm96 kernel;
  - SHA-512 identity digests, which are outside E4.
