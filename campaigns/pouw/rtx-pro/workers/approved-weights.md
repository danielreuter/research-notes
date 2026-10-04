---
cursor:
  subagentId: "bc-8412d697-8e5a-51be-834a-b61a695bcc03"
---

# Approved weights on node 2: fill leases and status

Worker bc-8412d697, the approved-weights lane. The report is [`docs/pouw/approved-weights.md`](/cursor/stores/bc-b729c175-2ef6-418e-98fe-10896709028b/docs/pouw/approved-weights.md) (§8, Scale; §8j, the folding cost). The code is `benchmarks/pouw/approved_weights/` on `cursor/approved-weights-gpu-cc03`. Every GPU job here is preemptible fill in node 2's `/workspace/pouw/fill/queue/`, one GPU each, owner `bc-8412d697-8e5a-51be-834a-b61a695bcc03`, collected by a research run.

## Fill leases on node 2 (log)

**The lease terms from 12:15Z:**
- Headers carry `max_min=8 prio=5`: the slot table's chunk cap, below the slot owners' `prio=10`, so owners' chunks start first.
- No `on=` pin. At most about four of my GPU jobs run at once, and the runner keeps GPU 1 free for its owner's `-h1` gate.
- Earlier jobs carried `max_min=25` and no `prio`, with chunks of 4–7 minutes.

| Queued (UTC) | Fill job | GPUs | What | Research run | State |
|---|---|---|---|---|---|
| 07:41 | `aw-gpu-tradeoff-73c72939` | 1 | Qwen2.5-7B rung sweep (§6a) | `r20260930-073807-c5c8` | done 08:24 |
| 09:03 | `aw-relation8k-c701e3e6` | 0 | relation attack, k = 8,192 (§8e) | `r20260930-090219-8711` | done |
| 09:03 | `aw-debit7b-c701e3e6` | 0 | real-activation debit, Qwen2.5-7B (§8f) | `r20260930-090159-c492` | done 11:27 |
| 09:34–09:37 | `aw-advdebit-{a,b,c}-0e4b2442` | 0 | item 4 (§8c) | `r20260930-093222-d933`, `-093230-5fc1`, `-093237-12be` | k = 8,192 done; k = 16,384 queued |
| 09:41 | `aw-act7b-1a62b9d4` | 1 | full activation path, Qwen2.5-7B (§8g) | `r20260930-090543-0199` | done |
| 09:50 | `aw-census-94afd036` | 1 | census, Llama-3.1-70B and Qwen2.5-7B (§8d) | `r20260930-091725-c649` | done |
| 10:02 | `aw-act7bfold-8fd63ddc` | 1 | the same, γ folded | `r20260930-100148-edac` | done |
| 10:09–10:11 | `aw-scale70b-{fp8,nvfp4}-{0,1}`, `-nvfp4cap64-0` | 1 each | Llama-3.1-70B loss (§8b) | `r20260930-100937-f895` to `-101006-5779` | done |
| 10:37 | `aw-act7bx-446475c3`, `aw-act7bx16-446475c3` | 1 each | split rotation, activation path | `r20260930-103527-9620`, `-103546-a1af` | done |
| 10:40, 11:04 | `aw-scale70b-lr1e4-*` | 1 each | 70B recovery at lr 1e-4 | `r20260930-103943-17aa`, `-110420-2a8f` | done |
| 10:51 | `aw-debit7bfold-bbb9521d` | 0 | real-activation debit, γ folded and split | `r20260930-105111-3b9c` | queued |
| 12:02 | `aw-fold-{attr,fix}-{fp8,nvfp4}-899a48fa` | 1 each | §8j attribution and block rotations | `r20260930-120206-8ad3`, `-120227-7dda`, `-120234-4d3b`, `-120241-3bd7` | done 12:11 |
| 12:15 | `aw-fold-rec-{fp8,nvfp4}-13c05e5b` | 1 each | §8j recovery | `r20260930-121511-0710`, `-121531-342d` | done |
| 12:28 | `aw-70b-rotb-{fp8,nvfp4}-d9fd73f7` | 1 each | §8j at Llama-3.1-70B | `r20260930-122846-664f`, `-122906-88e1` | done 14:16Z (NVFP4 bumped to prio 10 by infra) |
| 12:31 | `aw-fold-side-{fp8,nvfp4}-*` | 1 each | §8j side-product rungs | `r20260930-123136-93c4`, `-123143-95ef` | done |
| 14:26 | (a direct research run, CPU at nice 19 on CPUs 96–127, about 2 minutes) | 0 | the fork's noiseless rotated operands for bc-a8466279 (`/workspace/pouw/approved-weights/fork-weights/`) | `r20260930-142609-ffbb` | done |
| 14:38 | (a direct 5-minute preemptible lease, smoke) | 1 | the census's `blk8s` form, one Qwen2.5-7B chunk | `r20260930-143836-0707` | done |
| 14:40 | `aw-census-blk8s-6dc790e4` (prio 10, the slot table's standard) | 1 | the census on the 8-block rotation, Llama-3.1-70B and Qwen2.5-7B (§8j; for the NVFP4 C's) | `r20260930-144029-20cb` | done 14:47Z |
| 14:51 | (a direct 48-second CPU run at nice 19) | 0 | bc-a8466279's `fork_variant.py` on the fork's 7B operands | `r20260930-145124-45e7` | done |
| 15:04 | `aw-zero-cover-36e75bc2` (prio 10) | 1 | the zero-structure reading against the registration check, both models (§8i) | `r20260930-150439-7276` | done 15:07Z |
| 18:37, 18:39 | (direct 6-minute preemptible leases, smoke) | 1 | `aw_change_prob.py`, 8 keys | `r20260930-183734-1d1e`, `-183919-0516` | done |
| 18:42 | `aw-change-prob-7225704b` (prio 10) | 1 | the rotated codes' change probability over 256 keys | `r20260930-184210-0049` | withdrawn 18:43Z (optional once B-OVF covers the fork) |

- **Held for GPU 3's CPU queue** (Root, 10:17Z): the four CPU jobs, 10:19–11:09Z. Infra released them on its runner fix; `/workspace/pouw/approved-weights/held/hold.log` has every step.

## Lessons

- **Write checkpoints atomically and yield within one step.** A 70B job killed mid-projection at 10:13Z, 10 s after SIGTERM, would otherwise leave a truncated state file that reads as finished.
- **A queued job's code can move to a newer shipped tree between chunks** (`repoint.sh`): take the script out of `queue/` by a rename, edit it, and put it back.
- **A job is held by moving its script out of `running/`.** The runner requeues `running/<job>` only if the file exists; `release_held.sh` puts it back.
- **Compare quantized models over the whole test split, with paired deltas.** A one-window, 1,024-token comparison of rotations moves by about 1% from the random rotation alone.

## Needs

- The 13:55Z bump of `aw-70b-rotb-nvfp4-d9fd73f7` is done (thanks, bc-efe47341); the job finished at 14:16Z.
- Otherwise none. The sparse FP8 `mma.sp` capture (`tc-model/sm120-e4m3-sp-k64`) stays GPU 0's, if anyone needs it for rungs 6–7.

## Reply to compute-accounting's 0055Z order (6:00 PM PDT, 30 Sep): posted (research-notes `53cd3d18`)

This VM can read research-notes but can't push to it (HTTP 403). The old accounting lane copied the reply below into `lanes/accounting/` as `20261001T0100Z-reply-from-bc-8412d697-approved-weights-ack.md` (notes `53cd3d18`). Future replies are staged under their lane filename in the store's `internal/pouw-fp8/accounting-outbox/`, which it copies over every 10 minutes.

> # Re 0055Z order: acknowledged. The approved-weights lane holds no goal-critical job tonight; its work in hand
>
> To compute-accounting (bc-e90634dd), cc old-accounting (bc-b729c175, advisor) and bc-6289d8b0.
>
> - **Acknowledged.**
>   - I take orders from compute-accounting, as of Daniel's 5:52 PM PDT ruling.
>   - I read `lanes/accounting/` for `*-order-from-compute-accounting-*` on every wake, and reply here.
> - **No goal-critical job is mine.** I'm not in tonight's table, so I owe no READY line. If you hand me goal-critical work, I'll write its READY line 20 minutes before its mark and keep a timer of 30 minutes or less while I hold it.
> - **Where the approved-weights work stands** (the report is the store's `docs/pouw/approved-weights.md`; the rows are `internal/pouw/approved-weights-rows.md`):
>   - **Rung 3, the keyed 8-block rotation, is adopted for FP8 v1 and v2** (Daniel, 1:36 PM PDT).
>     - The report and the rows are marked adopted, and the FP8 `tt-out-aw` rows are ready for bc-69c09d42's copy into `assumptions.md`.
>     - Pearl-C4's rows stay pending on #580, the F1′ fix enforced.
>     - The fork's NVFP4 credit carries B-OVF's β(n): about 0.1% of credit at 3B and 7B, and 0.01% at 70B.
>   - **The keyed V/O rotation plus head interleave** (Daniel's yes at 5:52 PM PDT, for Pearl-C4, inside the 8-block rotation only). bc-6289d8b0 marks it adopted in `approved-weights.md` and `keyed-transforms.md`; I'm making no edit there.
>   - **Still running on node 2, not goal-critical:** four of my CPU fill jobs, slowly, in the shared CPU queue. They publish as attempts when done, and I'll fold them into the report's §8 unless you say otherwise.
>     - Item 4's adversarial-activation debit at k = 16,384, with the Haar modes: 19 of 27 cells done (`aw-advdebit-{a,b,c}-0e4b2442`; runs `r20260930-093222-d933`, `-093230-5fc1`, `-093237-12be`).
>     - The real-activation debit with γ folded and the split rotation: 5 of 6 chunks (`aw-debit7bfold-bbb9521d`, run `r20260930-105111-3b9c`).
>   - **Withdrawn:** the optional per-code change-probability check (B-OVF covers the fork instead), at 11:43 AM PDT, before any chunk finished.
> - **Available if you want it:**
>   - glue recovery at Llama-3.1-70B with the V/O fold and the interleave added to `aw_scale.py`, if bc-6289d8b0's node-2 evals show a cost there;
>   - any re-run of the approved-weights census on a changed transform.
> - **Access:** SSH and `research run --on vy-nebius-2` work from this VM, and node 2 has the Qwen2.5-7B and Llama-3.1-70B checkpoints the jobs need.
