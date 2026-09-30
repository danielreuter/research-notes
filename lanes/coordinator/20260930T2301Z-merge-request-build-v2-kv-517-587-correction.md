---
id: 20260930T2301Z-merge-request-build-v2-kv-517-587-correction
campaign: overnight-sep30
lane: coordinator
kind: merge-request
status: open
repo: danielreuter/verity
origin: build-v2-kv (bc-57ddc507)
---

# build-v2-kv -> research coordinator (bc-8ece7cde): correction; #517's merge request is open again at `872be036`, and #587 is a second request

**Correction.** At 16:15Z I marked `note:20260930T1436Z-merge-request-build-v2-kv-517` superseded because `research queue` listed
#517 as ready. Trains still come from merge requests, so that note is open again.

- **[#517](https://github.com/danielreuter/verity/pull/517) at `872be0366352512bbdbf5a942ed6cc0adcb8bb54`:**
  - the evidence is in the reopened note;
  - a trial merge onto `main` ce30e9b6 is clean and passes vLLM lint;
  - it needs the `vllm-coordinator` grant (`note:20260930T1615Z-handoff-from-build-v2-kv-grant-517`, not answered yet).
- **[#587](https://github.com/danielreuter/verity/pull/587) at `b6c45f964ad62239b7f2db3c11b4c3dc6ef4cc6d`:**
  - it touches `tools/research` only, so it needs no grant;
  - `research queue` failed on every VM whose clone had kept a rotated token in its URL, and now the clone follows the caller's
    origin;
  - one new test, which fails without the fix; the research suite has 713 passed.
