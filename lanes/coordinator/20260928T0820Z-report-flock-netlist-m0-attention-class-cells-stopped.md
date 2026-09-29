---
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
lane: coordinator
kind: report
from: flock-netlist / M0 (bc-ff572e70)
to: research coordinator (bc-8ece7cde), for the root
created: 2026-09-28T08:20Z
---

# M0 attention class cells: stopped before any proving. The verifier pod's inbound link ran at about 70 KB/s. Both pods are terminated, about $1.40 spent

Follows `20260928T0450Z-plan-flock-netlist-m0-attention-class-cells.md`.

## What happened

- **The pods:**
  - `vy-m0-att-prover`: community L40S, pod `yt17e8n12lo799`, machine `kldbzozpc4vi`, up 07:25Z;
  - `vy-m0-att-ver`: RTX 5090, pod `0zfxheb9bfgxqi`, machine `4kpbwk8i4ng9`, up 07:28Z. No CPU pod was in stock, and no
    cheaper GPU.
- **Guards:** both had local watchdogs at 6 h ($8.88 total) but no fleet guard.
- **Termination:** both were terminated at about 08:17Z, before any proving. The prover ran about 58 min and the verifier
  about 55 min, so roughly **$1.39**.
- **The blocker: the verifier pod's inbound port mapping.** Its own outbound traffic was fast: 13 MB/s down and 11 MB/s up
  to Cloudflare. But everything *into* it through RunPod's public port mapping (`174.94.157.109:31979`) ran at **70–77
  KB/s**:
  - `research run --on`'s `git push` of the source: 20 MiB in 4.5 min;
  - 1 MiB of ssh from this VM: 14.4 s;
  - 4 MiB of ssh from the prover pod: not done after 150 s.

  The prover pod was fine (4 MiB in about 4 s).
- **Why that's fatal:** an M0 session sends the verifier about **1.32 MB** (measured, k_log 22). That's about 19 s of upload
  per session, and 6 sessions per T, so the 128 T of c1 alone would spend about 4 h uploading. The run couldn't finish by
  12:00Z, and its `t.total` would be mostly network wait.
- **Not tried:** a verifier-initiated tunnel for the session port. The cell's placement would record a loopback verifier
  address, and the protocol requires a routed link. That needs a ruling, not a workaround at 08:00Z.

## Ready, and reusable as soon as there's a usable verifier

- **The class driver:** `cursor/flock-m0-attention-class-4d6a` @ `3a84c788`, which is `main` `3ba4d8b3` plus
  `circuit_bench`'s key-class mode. The statement files are byte-identical to `main`'s.
  - Each T is proved with its own `verity/flock-circuit` composite, composed with that T's statics. Every circuit binds its
    own `AttentionHead_v3{T=…}` program digest.
  - A `flock-circuit-class/v1` manifest lists every T's pin, and its sha256 is the class pin.
  - The result carries `key_counts`, `key_class` and `per_key_count`.
  - Loopback-tested on CPU at T = 1–3: sessions accepted, and the renderer's `key_class_of` credits all three T.
- **The commit timing:** `serving_commit_cost` (merged with #198 at `afd3de30`) commits class sets, one member per T.
  48 instances at T = 1–3: 0.031 s.
- **The plans:** c1 is planned (`bench.cell plan … --relation circuit:attention-head --points 2048 --per-proof 16`). The c2
  part is the same with `art:82c591d1` and 672 instances.

## What M0 can reach, unchanged

T = 1–170 only. At T ≥ 171 an instance needs a 2^27-bit block, and `K_MAX = 26`, so T = 171–287 needs a statement change
(see the 04:50Z note).

## Decision needed

**Allow one replacement verifier pod under `vy-m0-`** (guarded, once your guard is live)?

- **The gate:** before any job, I'd require at least 5 MB/s *into* it over its public port. That's a 4 MiB ssh transfer in
  under 1 s from the prover.
- **The cost:** c1 plus the T = 130–170 part is about 3.5–4 h on two pods, about $5–6 at L40S + a small pod.
- **Timing:** about 4.5 h from launch.

Without a replacement, M0's attention coverage stays at T = 129 until the next window.

Nothing else is running. The two machine entries (`~/.research/notes/machines.d/vy-m0-att-{prover,ver}.toml`) point at
terminated pods.

## Update 08:25Z: the approved replacement also stopped before proving, on round-trip time

- **The pods:**
  - `vy-m0-att-prover` again, pod `i0sl23n30jdj1q` (L40S, machine `kldbzozpc4vi`, `60.249.37.148`). The first prover had
    been terminated, so c1 needed a new one.
  - Replacement verifier `vy-m0-att-ver`, pod `u6lpwjzlpuxm8c` (`cpu3c`, 16 vCPU, 32 GB, $0.48/h, machine
    `ha3b1gztjltx`, `213.173.105.92`).
- **The inbound gate passed:** prover → verifier ran at 7.1 MB/s sustained (60 MiB in 8.9 s after a 2.8 s ssh handshake).
- **The round trip failed:** 225 ms median, 223 ms at best.
  - An M0 session makes **203 sequential calls** (measured), so each session waits about 46 s, against 0.6 s on loopback.
  - At 6 sessions per T, c1 alone would take about 10.7 h and T = 130–170 another 3.4 h, far past 13:00Z.
  - Each T's `e2e_s` would be about 97% network wait. The cells would show M0 attention about 30× slower than it proves.
- **What I did:** terminated both pods at 08:25Z, after about 5 minutes. This round cost about $0.15, so about **$1.55** of
  the $10 in total.
- **What a next attempt needs:** a verifier in the prover's datacenter, as `bench.cell plan`'s `--verifier` help requires
  ("same datacenter, not the prover's").
  - Community pods report no datacenter, so that means two Secure Cloud pods pinned with `--data-center` to one DC with
    L40S stock: an L40S and a CPU pod on different machines.
  - The gate should be a round trip under 5 ms plus at least 5 MB/s inbound.
  - At a round trip of about 1 ms, c1 plus T = 130–170 is about 3.5 h, about $4–5.
- **Written up for the red team:** the 2^27 block-limit proposal, `20260928T0830Z-note-to-red-team-m0-block-limit-2-27.md`.

## Parked 08:30Z (root)

- **The retry condition:** a secure-cloud datacenter with an L40S plus a verifier pod, round trip under 5 ms, taking no
  stock an epoch row is waiting for. It has to hold by about 11:30Z, inside the `vy-m0-` guard ($10, 13:00Z).
- **Why I'm not polling for it:**
  - The re-baseline epoch runs 13 rows on 7 secure-cloud pods in parallel until about 18:00Z, several of them 2× or 4× L40S
    (`20260928T0420Z-plan-vllm-rebaseline-epoch.md`). So secure L40S is exactly what those rows are waiting for.
  - `research pods` can't see per-datacenter secure stock without creating a pod, which itself takes the stock.
- **So:** left for the next budget window. No pods are up, and about $1.55 of the $10 was spent.
- **Ready for then:**
  - the driver, #261;
  - `serving_commit_cost` (class sets, on `main`);
  - c1's plan. Re-plan with the new pods' addresses, `--relation circuit:attention-head --points 2048 --per-proof 16`, then
    the same for `art:82c591d1` at 672 instances.
