---
id: 20260928T2103Z-handoff-from-pouw-mvp-gpu-request-8192
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pouw-mvp
---

# PoUW MVP -> root: GPU request, the 8192³ headline GEMM timings (one RTX 4090, cap $0.30)

From the PoUW MVP owner (bc-dd22acf8). Daniel wants every PoUW headline number at one size, 8192³, and the colleague
overview needs NCP-INT (`ncp-v1`) and Pearl rows there.

**Ask:** OK to run one short RTX 4090 timing run?

- **Pod:** `vy-pouw-mvp-8192`, one RTX 4090 ($0.74/h), fleet guard, cap **$0.30**, terminated as soon as the run is
  fetched. It needs about 12 minutes of pod time (~$0.15): a 2-minute setup, then one recorded `pouw_gemm` run.
- **Hold window:** start between 21:10Z and 21:35Z, so it finishes before the balance nears the $90 floor (about
  21:45Z to 22:10Z at the current $17–23/h spend by other workstreams). If the balance is under $95 at launch, we
  don't launch.
- **What it measures:** `benchmarks/pouw/gemm_bench.py` at 8192³ only, from a one-shape workload file on a side branch
  (not #218's, which is pinned for D3′). First the bit-identity gates run: NCP's native route-U kernel and Pearl's `ada`
  kernel against their references. Then it times NCP-INT's kernel against cuBLASLt int8, and Pearl's kernel against
  cuBLASLt FP8, on the same card.
- **Spend so far today:** about $8.30. No pods running.

Reply in `lanes/pous/`, as usual.
