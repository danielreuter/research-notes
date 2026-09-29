lane: coordinator · kind: handoff · from: circuit-checks · created: 2026-09-29T06:45Z · to: research coordinator (bc-8ece7cde)

# Fleet guard request: prefix `vy-cc-upstream-avx2`, $1.50, for the portable upstream Flock rebuild root approved; and a train rule until it lands

## Until this lands: trains touching `backends/flock/` need an AVX-512 check pod

The pinned upstream Flock build (`art:5e8c9749`) was built with `target-cpu=native`, from the bundle's `.cargo/config.toml`, on
an AVX-512 machine. On a CPU without AVX-512 (for example AMD EPYC 7713P, Zen 3), every upstream replay dies of SIGILL and
`lean-agreement` fails 0/N on all 16 sets after about 45 min. Record `check` for those trains on an Intel Xeon or EPYC Zen 4 pod.

## The guard

- **Prefix:** `vy-cc-upstream-avx2`, which is new, so no tripped guard covers it.
- **Cap:** $1.50, root's approval. **Deadline:** 09:45Z. **Balance floor:** $25.
- **The pod:** one US CPU pod, cpu3g, 16 vCPU and 64 GB, about $0.64/h. It must lack AVX-512 (checked before any run), and runs
  `runpod/base:1.3.3-ubuntu2204`. A pod-side dead-man is armed first, failing closed.
- **Why 64 GB:** in `check` the agreement shares the machine with pytest and circuit-check. On 32 GB it already hit the cgroup
  limit while upstream was dying at once.
- **The runs, about 1.5 h and $1.00:**
  1. The rebuild: the same bundle (sha256 `957f5751…`, the same flock commit `b684b125`), Rust 1.98.1 as recorded, and only the
     target changed, to `x86-64-v3` (AVX2), recorded in `BUILD.json`. It fails if any AVX-512 instruction remains. The bundle
     comes from R2 by presigned URL, not through the control pod.
  2. `check` recorded on the PR head (re-pin plus a preflight that replays one real session per upstream binary). That includes
     the full agreement on all 16 sets on the same non-AVX-512 pod.
- **Order:** I create the pod only once you confirm the guard is armed. Please reply in `lanes/circuit-checks/`.
