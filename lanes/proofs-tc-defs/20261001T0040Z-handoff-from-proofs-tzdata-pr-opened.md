---
id: 20261001T0040Z-handoff-from-proofs-tzdata-pr-opened
campaign: verity
lane: proofs-tc-defs
kind: handoff
status: open
repo: danielreuter/verity
origin: proofs (bc-8416bc72, Slack @proofs)
---

# Your tzdata fix has a PR now (#617); don't open another

The old research coordinator's train TCX carries your `42ea2831b` (`cursor/research-timefmt-tzdata-ec6a`). It needed a PR
so it could close as merged, and you were mid-run, so I opened
[#617](https://github.com/danielreuter/verity/pull/617). Leave the branch as it is until TCX lands.

Keep to the probes: the E5M2 anchor, NaN and Inf, and the MXFP4 edges. MXFP4 has two open points to cover:
- the `0xFF` scale → NaN rule is carried over from NVF4 and was never measured on MXFP4;
- MXFP4 is pinned on the RTX 5090, not swept on the PRO 6000.
