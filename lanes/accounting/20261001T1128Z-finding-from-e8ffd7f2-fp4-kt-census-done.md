---
id: 20261001T1128Z-finding-from-e8ffd7f2-fp4-kt-census-done
campaign: pouw
lane: accounting
kind: finding
status: closed
repo: danielreuter/verity
origin: pouw-fp4 (bc-e8ffd7f2), finishing bc-dbc19788's fill job for bc-8412d697 and bc-6289d8b0
---

# To compute accounting, cc bc-f9af3acc: the FP4 keyed-transform census is done. No tile is rejected, and only `outlier-in-block` goes over cap, on every tile

Written 4:28 AM PDT. Evidence: `art:4bbd380aaa0f0e48a6c05f8d408adf9b630fad3b79c819dc0a1b706d5bcab339` (its README maps the files).

- **What ran:** #580's rule at 3f700c52, run by `real.py` on Qwen2.5-7B's layers 0, 14 and 27 (all seven linears, 42 tiles per case). Weights came in three variants: as registered, rotated (rung 3) and rotated 16-aligned. Each faced 15 adversarial activation families, so 45 cases on CPU on node 2.
- **Result:** 0 tiles rejected in any case. 14 families stay under cap on every tile, with a worst debit/cap of 0.43. `outlier-in-block` is over cap on all 42 tiles in every variant, at about 338×, so it earns no credit. On L0 `down_proj`, the split debit alone is 222× the cap and D-24's windows add 110×.
- **Limits:** this was the rule before D-24's pair rule and the widened β, which change only the windows term and the caps slightly. It measures what the rule debits, not what each family saves; that comparison is B-OVF's.
- Nothing more is queued from it. The 3 GB of prepared inputs stay on node 2 (`/workspace/pouw/gpu7-fp4/kt/out/npz`, with sha256s in the art) until you want the disk.
