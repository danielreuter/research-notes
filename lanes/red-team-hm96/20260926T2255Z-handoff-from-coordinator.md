---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

lane: red-team-hm96 · kind: handoff · from: coordinator · created: 2026-09-26T22:55Z

# Follow-up review: PR #93 (E4), `hm96-sha512/v1` plus the SHA-512 frame-v3 and vllm-v1 framings, @ cd00f704

PR #88 is merged (main 10726738), with your C1 and C2 met. PR #93 (`cursor/sha512-commitments-18a8`, from salted-leaves) adds,
all opt-in:
- `hm96-sha512/v1`, with the same hiding bound. The key is fixed and public: SHA-512 counter mode over a public label.
- SHA-512 variants of both tree framings: frame-v3 §6 and vllm-v1 §10.
- Part of E1: how the pinned keys are derived (hm96 §2a), and the new `hash-derived-key` claim.

**Please check:**
- the hiding bound as instantiated at SHA-512;
- key derivation, in particular the public-label counter mode and whether it holds in your model (finding 6: the key is
  never a witness);
- domain separation between the SHA-256 and SHA-512 schemes and framings, so there are no cross-scheme collisions or
  substitutions;
- that every SHA-256 default stays byte-identical;
- the vectors, recomputed independently.

Verdict to `lanes/coordinator/`. CPU only, under $1. Daniel puts security first here, and this gates the merge.
