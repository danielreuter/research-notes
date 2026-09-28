lane: coordinator · kind: handoff · from: circuit-checks · created: 2026-09-28T21:09Z · to: research coordinator (bc-8ece7cde)

# Please re-arm the vy-circuit-checks guard: about $1.50 for measured cold and warm check runs (verdict caching follow-up)

- **What for:** Daniel's two approved calls, warm Lean dependencies per pod and verdict reuse across commits, as a follow-up PR on
  #134. The merge request needs measured cold and warm `check` times.
- **Pods:** one 32 GB CPU pod (8 vCPU, about $0.37/h) for about 3 hours:
  - a cold `check`, about 35 min;
  - two or three warm `check` runs on changed and unchanged trees, 5 to 15 min each;
  - fixes between runs.

  Estimate $1.10 to $1.50. Pods are named `vy-circuit-checks-*`, checkpointed while in use, and terminated after each session.
- **The guard's deadline passed at 20:00Z yesterday,** so a new pod under the prefix would be terminated. Please re-arm it until
  about 03:00Z. I'll build and test locally until then.
