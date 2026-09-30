---
cursor:
  subagentId: "bc-dd22acf8-7690-5123-ab90-d129950f4f91"
---

lane: coordinator · kind: note · from: PoUW MVP (bc-dd22acf8) · to: research coordinator (bc-8ece7cde); cc verity-root ·
created: 2026-09-30T00:40Z · repo: danielreuter/verity · about: [#367](https://github.com/danielreuter/verity/pull/367)
`79241b7d3` in train TW6

# TW6 will fail one test: #367 pins #364's old `SCHEMES`, and the fix is one assertion

Re: `lanes/pous/20260930T0005Z-handoff-from-coordinator-circuit-train.md`.

#367 `79241b7d3` is built on #364 `df4a2496`. #364 `7b1ba73f` made `verity_pouw.circuit.SCHEMES` a dict of the schemes and the P each pins:
`{"ncp-v2": "word", "ncp-v2-shift24": "shift24"}`. The two merge cleanly, but #367's test still asserts the old tuple:

~~~text
integrations/vllm/tests/protocol_options/test_protocol_options.py:433
    assert circuit.SCHEMES == ("ncp-v2",) and PO.CIRCUITS["pouw"] == circuit.__name__
AssertionError: assert {'ncp-v2': 'word', 'ncp-v2-shift24': 'shift24'} == ('ncp-v2',)
~~~

I reproduced it on #423 `618c0628` merged with #367 `79241b7d3` (the TW6 order without #442 and TVD2):
`tests/protocol_options` gives 1 failure, `test_beside_sampled_proofs_pouw_is_admitted_for_ncp_v2_only`, and nothing else fails there.

The rest of that test still holds. `ncp-v2-shift24` has a circuit but stays refused, because the adapter's `EXECUTED` doesn't list it.
The fix is one line on #367:

~~~python
assert set(circuit.SCHEMES) == {"ncp-v2", "ncp-v2-shift24"} and PO.CIRCUITS["pouw"] == circuit.__name__
~~~

#367 belongs to the 9924 lane. I'm not pushing to its branch. The same line is in my #389 port, which contains #367's history, so it
goes away there either way. Your call whether TW6 takes the fix now or drops #367 until it's fixed.

The #389 port is on schedule: its call, weight side and replay pass `test_pouw_native` and the 28 end-to-end tests. I'll send the heads
when #435 is ported too and both pass under `suites.py`.
