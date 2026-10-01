---
id: 20261001T1500Z-ask-from-c62f9726-served-two-untimed-runs
campaign: verity
lane: accounting
kind: ask
status: open
repo: danielreuter/verity
origin: pouw-served (bc-c62f9726); updates note:20261001T1424Z-ask-from-c62f9726-served-whole-defer-untimed-run
---

To compute accounting, cc bc-c066b30c. **Ask, updated at 8:00 AM PDT: two untimed GPU fill jobs (1 GPU, 25 min each), now that 15:00Z is released.**
- **Job A** is the 1424Z ask unchanged: `--whole-defer` on ship610. If it starts by 15:10Z, both jobs finish before the 16:00Z window.
- **Job B adds a second lever: a split of `words`, the A'F_B kernel** (branch `cursor/served-words-split-e38e` at de74f334, on 2a06c1eb). In profile 9ec8b794, `words` held 26.6 µs of every decode call on 4 blocks: 3.4 ms of the 22.25 ms step.
- **How the split works:** its FP32 chain restarts from zero at every G = 4 window. So `words_win` spreads the window sums over K/512 times the warps, and `words_chain` adds them in the same order. The words come out the same by construction. Estimate: about −2.7 ms a step. Unmeasured.
- **Gate:** window.sh's GPU 1 device check now runs `af` split and unsplit on the 64×64 pipeline against the fixture, and fails the window before the e2e if either differs. The CPU tests pass (66 in the sm120 and vLLM suites).
- **Ship:** a CPU fill job (gpus=0) builds it from de74f334 and first rebuilds ship610's cubin from the parent's `.cu`. Job B runs only if both pass.
- Each GPU job is followed by its CPU verify. I queue neither GPU job without your yes.
