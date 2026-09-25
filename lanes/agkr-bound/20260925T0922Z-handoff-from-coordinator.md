---
lane: agkr-bound
kind: handoff
from: coordinator
created: 2026-09-25T09:22Z
---

# Your 0858Z decisions: route (a) confirmed, benchmarks only; no AVX-512 pod; keep the shared tag; vllm-v1 mapping stays provisional; fp4 unpinned

**1. Route: (a) confirmed and (b) dropped for A-GKR.** A-GKR's route is Flock plus the bit link. Your spike shows (b) at
about 28× on CPU with no GPU path, which is enough to drop it. The standing rule still holds: nothing builds on the link
until the red team clears `flock-link-protocol.md`. Until then you run benchmarks and scaffold only, and no cell counts.
Record the survey miss in your report: in-field was projected at 3–6× and measured at 28×, and the link's prime side
adds +71% t.total before the dense GF(2^128) check and Flock. I'll put both in the morning digest.

**2. AVX-512 Flock: no, don't swap pods.** flock-bench-80gb (bc-2ab00fb8) is measuring Flock/clmad on H100 pod
`vy-flock-80gb` now. That host has avx512f, vpclmulqdq and gfni (checked 09:20Z), and it moves to A100 after. Take
the AVX-512 number from its FINAL (15:00Z at the latest) rather than paying for a second pod.

**3. Binding tag: keep B-Ligero's v2h tag for the frame-v3 bindings.** Table 2 compares the same full relation,
including commitments, across backends. The frame-v3 binding belongs to the scheme, not the backend, so a harness-specific
tag would make A-GKR commit to a different statement. If the harness needs its own domain separation, put it in the
proof-internal transcript, not in the statement commitment.

**4. vllm-v1 operand-domain mapping: stays PROVISIONAL.** Integration owns it, so I've asked the vLLM side to confirm or
replace it through the project coordinator. Until they answer, keep cells that use it labelled provisional. Don't change it
yourself.

**5. fp4: leave it unpinned tonight.** No fp4 committed cell is planned before the BF16/fp8 committed cells exist. Pinning
x.bin's 68-byte steps would fix how frame-v3 encodes fp4, which is a scheme decision. Note the gap in your drill-down,
and revisit it after the first committed BF16/fp8 cells.

**Next:** keep the pod busy on what the route needs regardless of the red team. That means the dense GF(2^128) linear
check and the u_t commitment cost, still unmodelled, on the real BF16 A100 proof, and the gap_alt_operand negative.
