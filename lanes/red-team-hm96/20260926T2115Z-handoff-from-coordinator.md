---
cursor:
  subagentId: "bc-8ece7cde-78d8-5ed9-84b0-a0a81b19f628"
---

lane: red-team-hm96 · kind: handoff · from: coordinator · created: 2026-09-26T21:15Z

# Red-team brief: `hm96-sha256/v1` hiding leaf commitments (PR #88 @ f1df809f)

**Context:** Daniel approved hiding serving leaves at about 19:58Z (`docs/project-context.md`).
- The scheme: Halevi–Micali on SHA-256, statistically hiding and binding from collision resistance alone, with SHA-256 on
  every commitment path.
- Lane salted-leaves built it in PR #88 (branch `cursor/hm96-sha256-leaves-18a8`, head f1df809f). The lane is FINAL.
- It's opt-in and off by default; the switch waits for the re-baseline, which is on hold.
- Daniel puts security first here, so this review gates the merge.

**What to review (code read plus CPU tests; no GPU needed):**
1. **The scheme against the paper:** `packages/verity/src/verity/commitments/hm96/PROTOCOL.md` and `__init__.py`, set
   against Halevi–Micali '96.
   - Parameters: randomness length, the universal-hash family and its seed handling, and output length.
   - The statistical-hiding bound as instantiated, stated as a number.
   - Binding reduces to SHA-256 collision resistance with no extra assumption.
2. **Domain separation and framing:** check that leaf, row, position and run are bound, and that the `vllm-v1` leaf's domain
   and position rules (`verity/commitments/vllm_v1/PROTOCOL.md` §5) still hold under HM96.
   - No cross-leaf or cross-run substitution.
   - Openings can't be equivocated through encoding or length ambiguity.
3. **Randomness:** where it comes from (OS CSPRNG), that it's fresh per leaf, never reused across rows, runs or retries, and
   never derived from committed data.
4. **Openings and verification:** in `integrations/vllm/verity_vllm/commit/hiding.py`, `native_host.py` and
   `native_ranges.py`:
   - What an opening reveals, and that range openings and point openings both check the hiding layer.
   - The off-by-default path is byte-identical to today's, so digests of record don't move.
   - Enabling it changes identities in a named, versioned way.
5. **Vectors:** `hm96/vectors.json` and `vectors.py`. Recompute them independently and add negatives:
   - a wrong nonce, a swapped leaf, a truncated opening, a length-extension-style substitution;
   - the randomness of a different position.

**Deliverable:** GRANT, GRANT WITH CONDITIONS, or REFUSE, with numbered findings (severity, whether each is fixed) in
`lanes/coordinator/<stamp>-handoff-from-red-team-hm96.md`. Budget: CPU only, under $1.
