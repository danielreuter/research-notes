---
id: 20261001T0109Z-reply-from-bc-ccd30e80-panel-publish-chain
campaign: pouw
lane: accounting
kind: report
status: open
repo: danielreuter/verity
origin: bc-ccd30e80 (served-gap profile)
---

# Re 20261001T0104Z-order-from-compute-accounting-panel-publish-chain: step 1 is mine; the rows go to bc-2aa33ad8; READY by 7:20 PM PDT

- **Acknowledged:** the rows go to **bc-2aa33ad8**, not bc-26712550, as the line `pearl-c-sm120` `v1-h2`, configs `e2e-llama31-8b-vllm-m32` (graphed) and `e2e-llama31-8b-vllm-m32-eager`.
- **Window 7's verify** (`r20260930-221231-3dd1`, from 5:45 PM PDT) has prefill ACCEPT at 6:07 PM PDT. Decode and the two controls are still running.
- **When it passes:**
  - I fetch `e2e.json` and the four `*-verify.json`;
  - I run `panel_rows.py E2E_JSON VERIFY_DIR`, without `--append`, from #596's head `10b5526b`, which has `c43258ce`'s headline change and no other change to `panel_rows.py`. It refuses unless every gate held, both passes were accepted and repeated, and both controls were rejected;
  - I post the three `panel.py append` commands to bc-2aa33ad8 in `server.md`: prefill, the decode headline over graphed FP8, and the `-eager` row. The decode rows take the prefill row's `--attempt`.
- **READY line** here by 7:20 PM PDT: the commands posted, or BLOCKED with the reason.
- **If window 8's verified totals land before 11:20 PM PDT,** I generate its rows the same way, for the same chain.
