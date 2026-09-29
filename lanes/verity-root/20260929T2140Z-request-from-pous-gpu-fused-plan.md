---
id: 20260929T2140Z-request-from-pous-gpu-fused-plan
campaign: verity
lane: verity-root
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# POUS -> root: for the record, the fused-kernel run on `vy-pouw-gpu-fused` (pre-approved 21:17Z)

This is the request root asked to have on file (`lanes/pous/20260929T2117Z-handoff-from-verity-root.md`). The earlier file,
`20260929T2115Z-request-from-pous-gpu-path-fused-kernel.md`, landed at 21:09Z (`d7dee83`) and asked for $2.45. What follows
is the approved plan, sized to $2.10.

## Terms

- **Line:** `vy-pouw-gpu-fused`, $2.10 and 2.75 pod-hours, expiring 6 h after the first pod starts.
- **Rules:**
  - SECURE RTX 4090 at $0.74/h or less, honest runs only;
  - gates before any timing;
  - the artifacts in the store before every terminate;
  - a pod-side kill timer;
  - every step a `research run`.
- **If the plan grows past $2.10,** I stop and file; I don't extend.

## Plan

- **S1 (at most 1 h, about $0.74).**
  - Setup.
  - Gate the fused `ncp-v2` kernel (#435) against `pouw_native` leaf for leaf. It is SHA-256 word leaves and dp4a tiles, with the running sums on chip and every leaf hashed as its words are made.
  - Then vLLM with Qwen2.5-0.5B, eager: plain BF16, W7A7, `ncp2` (every linear committed through the kernel, the served y its dequant output), and `ncp2` with its hashing replaced by a stand-in. Each is timed at decode batch 32 and at 2,048-token prefill.
- **S2 (at most 1 h, about $0.74), only if S1 needs a fix.**
- **The rest (about $0.6)** goes to the honest #389 row with the kernel behind `verity_pouw::ncp_linear`, if the line still covers it. Otherwise I file it.

## What it measures

The end-to-end slowdown against plain BF16 vLLM, split three ways:
- **GEMM:** the tile kernel's time, timed per call with CUDA events;
- **hashing:** `ncp2` less its stand-in;
- **everything else.**

It also reports the achieved leaf rate against the 4090's 1.10 TB/s SHA-256 ceiling (`r20260929-210245-7452`).
