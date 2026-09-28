---
id: 20260928T1630Z-handoff-from-pous-protocol-options-go
campaign: verity
lane: vllm-coordinator
kind: handoff
status: open
repo: danielreuter/verity
origin: pous
---

# Daniel has asked us to build the POUS and PoUW vLLM options now; please review

Daniel (16:28Z) wants the POUS and PoUW protocol interfaces merged to `main` and integrated with vLLM now, even as placeholders security-wise. Your 05:40Z plan files for both options had no reply, so we're going ahead on your 04:10Z layout and those plans:

- `integrations/vllm/verity_vllm/protocol_options/`, containing:
  - `__init__.py`: the selector and the `PROTOCOL_OPTION = none | pous:<scheme> | pouw:<scheme>` knob, default `none`;
  - `pous.py` and `pouw.py`: thin adapters over `verity_pous` / `verity_pouw`.
- `tests/protocol_options/`, CPU-only.
- The default stays `none`, so nothing changes for existing runs.

Two draft PRs will follow. The POUS scaffold comes first; the PoUW adapter is stacked on it.

Please review them when they're up. If anything in the layout conflicts with the epoch work, say so in `lanes/pous/` or reply here, and we'll adjust before they're marked ready.
