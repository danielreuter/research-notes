---
id: 20260929T0805Z-note-from-pouw-mvp-main-derive-test-fails
campaign: verity
lane: verity-root
kind: finding
status: open
repo: danielreuter/verity
origin: pouw-mvp
---

`integrations/vllm/tests/program/test_derive.py::test_s3_untied_lm_head_loses_sharing_and_is_refused_by_family` fails on current `main` (`610ee10f`, torch 2.14 CPU): `assert rep.program.input_gates > _serve_inputs(C, 3)` gets 7158595 > 7158595, so an untied lm_head no longer adds input gates (#389's recorded vLLM tests deselect it by name, `r20260929-073036-efb8`).
