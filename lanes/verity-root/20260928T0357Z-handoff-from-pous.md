---
id: 20260928T0357Z-handoff-from-pous-to-verity-root
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# Addendum to 0352Z: same pattern for proof of useful work

Daniel wants proof of useful work (PoUW) packaged the same way as POUS: a fully generic Python PoUW protocol with interfaces, and two implementations of it.

- **Pearl's published protocol:** KW-style low-rank noise, pearl-research-labs/pearl PR #311.
- **Our noise-cancelling construction (NCP).** It checks the running sums of one stacked int8 GEMM. The target is under 1% work gap on an RTX 4090.

Both should plug into vLLM as options, alongside POUS. The owner is bc-dd22acf8-7690-5123-ab90-d129950f4f91.

So the question from 0352Z now covers both protocols. Is there one vLLM "protocol option" hook you'd want, with POUS as a weight-decode hook and PoUW as a hook on every matmul? Where should the generic protocol interfaces live: `protocols/pous`, `protocols/pouw`, or a shared base?

Replies go to lanes/pous/.
