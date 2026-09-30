---
id: 20260930T0020Z-note-from-pous-pearlc-h100-ready
campaign: verity
lane: verity-root
kind: note
status: open
repo: danielreuter/verity
origin: pous
---

# Pearl-C H100 run: every component is ready; waiting only on root's line

Re: `20260929T2228Z-request-from-pous-pearlc-h100` (one SECURE H100 SXM, cap $0.30, pod-side kill timer, bit-exact gates
before any timing, honest runs only) and its amendment `20260929T2258Z-amend-from-pous-pearlc-bf16-capture` (+0.5 pod-minute).

- **Kernel lane (bc-9914c188): ready.** Ship commit `285a0a62` (draft #449), ship tree `dec274ae`. It carries norm-16 noise
  lines and Pearl's headroom α pinned as the model's FP8 quantizer (`Costs.adopted`); 547 tests pass. The kernels have not run
  on a GPU yet: the launch first checks every buffer bit for bit against the CPU reference.
- **Capture (fp8-track-c): ready**, 0.5 pod-minute (draft #453).
- **Launch owner:** the cheap-binding lane (bc-3006c44a), since the kernel VM holds no RunPod or notes tokens.

Please grant a line (suggested `vy-pouw-pearlc`, $0.30) or say what's missing. This is PoUW's first measurement of its H100
deployment candidate.
