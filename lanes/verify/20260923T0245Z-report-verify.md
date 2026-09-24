---
id: r21-verify/verify/20260923T0245Z-report-verify
campaign: r21-verify
lane: verify
kind: report (final; supersedes 20260922T2230Z-report-verify.md)
status: closed 2026-09-23 02:45Z (poll loop ended, both pods terminated, every r21-verify attempt PRESERVED on the remote)
repo: verity-main@65434ad (lane/verify = main at fork; NO code changes, nothing committed)
branch: lane/verify (worktree ~/projects/verity-main-wt/verify)
machines: vy-verify = RunPod dgkx6z1wev7k74 (RTX 4090 24 GB SECURE, 32 vCPU / 125 GB, $0.74/h, 2026-09-22 21:40Z -> 02:15Z) and
          a8oeydbj8h3wbp (RTX 4090 SECURE, 16 vCPU / 62 GB, $0.74/h, 2026-09-23 02:18Z -> 02:35Z, determinism re-runs only)
decision: independent verification of every Table 1 candidate result's proof dumps (three-table contract, verification predicate)
---

# verify: the independent verifier — every candidate result's proof bytes, re-verified by the Rust verifiers on a pod

## 0. Headline

- **114 candidate `bench-result/v1` processed, 114 labelled** (every B-Ligero / A-GKR / SP1 result in the store at 02:12Z, including the
  h100-bestvsbest Q2 results and everything that landed during the poll window): **14 accepted, 5 rejected, 33 not-transferable,
  62 no-dumps**. 8 526 proof files were checked cold from bytes; 78 `r21-verify` attempts (verifications, census, verifier builds) are
  in the store and PRESERVED (`research data push`: 376/376 objects).
- **Rejections (5, all B-Ligero, all deterministic):** 1 × soundness-parameter shortfall (b-sweep 2048 sub-batches: union bound
  2^-127.54 < the declared 2^-128); 1 × b-hopper proved over a system that no pinned verifier accepts (bf16-hopper system with a
  bf16-ampere statement); 3 × r21-ada-fp8-dumps@7bb0ffa dumps in a statement format no pinned verifier reads (§3). None is evidence
  of a forged proof; all are protocol/relation drift between producers and verifiers. Section 3 has every exact error.
- **Table 2 cells populated by *this lane's* labels:** all four Fiat–Shamir drill-down cells (B-Ligero `COMPLETE_HVZK_BACKEND`) —
  A100 first-campaign-target 4.7e7× (`art:f8afd5b6…`), H100 bf16-hopper 1.4e8× (`art:77ef58df…`), H100 fp8-hopper 1.2e8×
  (`art:11bb6de7…`), 4090 fp8-ada 6.3e7× (`art:0553e315…`). On the A100 and 4090 ones `verify` is the **only** asserter of
  `verified=accepted`; the two H100 ones also carry a coordinator `accepted`. The four *headline* B-Ligero cells (A100 4.4e7×, H100
  bf16 1.3e8×, H100 fp8 1.2e8×, 4090 5.9e7×) are populated by the **coordinator's** `verified=accepted` on interactive transcripts
  that this lane labels `not-transferable` (§5.2 — a policy conflict the coordinator must own, not a disagreement about the bytes).
- **B-Ligero's headline class cannot be independently verified from dumps — structural** (§5.1): `COMPLETE_ZK_BACKEND` is interactive,
  and per `ligero-verify/DISCREPANCIES.md` D7 an interactive transcript is live-verifier-only evidence.

## 1. What this lane did

Under the frozen three-table contract a result may only populate Table 2 if a label `verified=accepted` (or
`independently_verified=true`) is asserted by someone who is **not** its producer (`tables._verified_by`: the asserter is not the
attempt's `execution.campaign` and not an asserter of the result's `candidate=`/`label=`/`proof_class=` labels). Every lane had
verified its own proofs; nothing in the store satisfied the predicate. This lane produced no benchmarks: it fetched the proof bytes
each candidate result left behind, verified them with the **independent Rust verifiers** on a pod, published each verification as a
`research run --on vy-verify` attempt (result kind `verification-verdict/v1`, campaign `r21-verify`), and labelled the results
`verified=… verifier=… verifier_seconds=… verify_note=… --by verify --ref <verification run>`. Never `candidate=`, `proof_class=`
or `label=`, so `verify` is a producer of nothing (checked: `verify` appears in no result's producer set in `tables` output).

Verdict vocabulary (label `verified=`):

- `accepted` — every dumped proof re-verified cold from bytes by the independent verifier at the producer's commit (or, for
  relation-named results, by the relation-pinned verifier — §2, "verifier identity").
- `rejected` — the verifier refused the proofs; exact error recorded, re-run once (determinism), reported first (§3).
- `not-transferable` — interactive-mode B-Ligero transcripts: the dump carries the runner's step-0 coins and the verifier accepts the
  transcript against those coins (`--coins`), but per D7 the re-verifier cannot know the coins were the verifier's and not the
  prover's. Not a failure; not transferable evidence either. All 33 are "accepted against the dump's own coins, N/N".
- `no-dumps` — no proof bytes reachable: never dumped, dumped then pruned, or dumped on a pod that no longer exists. Custody rule: a
  single missing or sha256-mismatched file ⇒ `no-dumps` for the whole result (never a partial verdict).

## 2. Method

**Where the bytes actually were.** The spec assumed dumps live in each attempt's `run-files/v1`. For most B-Ligero lanes they do not:
`backends/direct/ligero/bench_result.py` stores only `proofs/manifest.json` (path + sha256 + bytes of every `.stmt/.proof/.coins` and
of `system.bin`); the files stay in the producer pod's `/workspace/research/runs/<run>/proofs/`. Three lanes (r21-a100-dumps,
r21-ada-fp8-dumps, r21-ada-ref — the ones whose names say so) did upload the bytes. So two paths were used:

- **pod-to-pod channel** (fill-a100, b-sweep, b-hopper, b-merge-h100, bestvsbest/vy-bvp): vy-verify holds a dedicated keypair
  (`/root/.ssh/verify_export`); its public key is installed on each live producer pod as an `authorized_keys` **forced command**
  (`/usr/local/bin/verify-export.sh`, `no-pty,no-port-forwarding,no-agent-forwarding`) that answers exactly two verbs: `list` (run
  dirs that have `proofs/`) and `<run id>` (`tar -cf - proofs` of that run). Read-only by construction. Largest transfer: 6.5 GB in
  410 s.
- **store path** (a100-dumps, ada-fp8-dumps, ada-ref): the laptop fetches the `run-files/v1` tree from R2 (`research data fetch`),
  scp's `proofs/` to vy-verify with one stream per top-level entry (the laptop→pod link is ~1 MB/s per stream), deletes its copy.
  0.55–0.83 GB per result, 200–260 s each. Pods never hold store credentials (R2 keys are laptop-only).

In both paths the pod-side driver `verify_dumps.py` **sha256-checks every fetched file and `system.bin` against the result's own
`proofs/manifest.json`** (fetched from the store by the laptop and shipped with the job); custody is recorded in the verdict artifact
(`custody.matched/mismatched/missing`, `system_matches`, `manifest_identical`). Verification: `ligero-verify verify --system system.bin
--stmt X.stmt --proof X.proof [--coins X.coins] --soundness-bits <result's security.target>` per sub-batch proof, 8 processes × 4
threads. `verifier_seconds` = sum of the verifier's own `total` timing over all proofs; `wall` = elapsed for the parallel batch.
`--soundness-bits` is the result's declared target (80/100/128): without it the verifier demands 2^-128 and rejected the 2^-80 and
2^-100 sweep points spuriously (two early `rejected` verdicts, corrected and superseded the same hour — see the ledger's history).

**Verifier identity vs producer commit — "build both, report both".** Every B-Ligero result was checked with the verifier at the
producer's own commit, and, where that verifier could not even read the dump, with the relation-pinned one; every extra build's
verdict is *recorded* in the attempt (`also:` in `detail`, `workload_fingerprint.also`) and never labelled. Facts found:

- fill-a100 915baf9, b-sweep c135a9c, bestvsbest b48dfbb/c013f6f, silicon 4bf0c4f, b-hopper 11f4120, a100-dumps bc039b1:
  `backends/ligero-verify` is **byte-identical** to main@65434ad (`git diff --stat` empty), so `ligero-verify@65434ad` *is* their verifier.
- main's `ligero-verify` (65434ad, and main HEAD e059f14 as of 00:49Z) pins **one** system: the frozen REAL chain (bf16-ampere,
  sys_id 44cb05b9…, table digest c147cc4c…). Every relation-named result (bf16-hopper / fp8-ada / fp8-hopper) proves over a different
  compiled system and is refused with `system file is not the pinned REAL chain system` before any cryptography runs — a coverage
  gap of that build, not a defect of the proofs (confirmed once with `--allow-any-system`: b-hopper's 75/75 verify against the
  system the dump carries, r20260922-231138-a314, diagnostic only).
- `lane/ligero-verify-relations` (857f722; merged to main as 381c045 at ~01:40Z, same code up to doc comments) pins each relation's
  system by sys_id + table digest and reads statement **v4**. It is the primary verifier for relation-named results
  (`verifier=ligero-verify@857f722 +relations`, or `@381c045` once the producer's commit was main itself, ada-ref).
- The producer commits of the relation lanes (b-merge-h100 01fc64f, ada-fp8-dumps 7bb0ffa / a4b0ac7) carry a `ligero-verify` that
  still pins only the REAL chain: those lanes' self-verification necessarily bypassed the pin. Recorded beside every relation verdict:
  `ligero-verify@<producer> (producer commit): rejected 0/N (system file is not the pinned REAL chain system)` and the same for main
  HEAD e059f14. **This is the protocol-drift finding the spec asked for**: proofs that verify under the relation-pinned verifier and are
  refused by the producer's own commit and by main HEAD of the time.
- lane/auth-included's extended verifier (0ddc2c9: `auth.rs`, statement v3 / proof v2, SHA-256 word trees + Merkle multiproof check)
  was built as `/workspace/bin/ligero-verify-auth` and would have been selected for `authentication=included` results
  (`verifier=ligero-verify@0ddc2c9 +auth`); **all 5 auth-included results are `no-dumps`** (vy-auth was gone when they landed), so it never ran on
  real dumps.
- SP1: `backends/sp1` at the producer commit b96edf6 differs from main only in README.md; the CPU-SDK host built with the results'
  guest feature (`unsound-relation-only`) reproduces the producer's guest identity exactly (`elf_sha256 616100249a681540…`,
  `vk_hash 0x00776ea1156af4fa…`), so `veritor-zk-host verify --proof` re-derives the very verifying key the producer proved under.
- A-GKR: `verity-gkr-verify@65434ad` built; nothing to feed it (no A-GKR result has proof bytes anywhere).

Verifier builds (each a `verifier-build/v1` attempt; binaries are not bit-reproducible across the two pods' toolchains — the crate
tree sha256 is the identity that matters, and every `cargo test --release` passed):

~~~text
build attempt            binary                              commit    crate tree sha256   binary sha256        tests
r20260922-214102-8ad9    ligero-verify                       65434ad   (main; bootstrap)   4215e8ab6f35e4c6…   all pass
r20260922-214102-8ad9    verity-gkr-verify                   65434ad                       built, unused
r20260922-215615-95ef    veritor-zk-host (sp1-sdk 6.4.0)     b96edf6   (unsound-relation-only, CPU)  3d44e1a01c8794c5…
r20260922-221543-e49a    ligero-verify-auth                  0ddc2c9   (lane/auth-included)          b15f389d97d97b72…   18/18
r20260923-004945-43b5    ligero-verify-7bb0ffa               7bb0ffa   ca05bed002e25a0d…   88b74ac4bdbb9e9a…   8+6 pass
r20260923-004945-43b5    ligero-verify-857f722               857f722   c4df66fe7a795010…   0574ce1a3cb40d73…   17+7+6 pass
r20260923-004945-43b5    ligero-verify-a4b0ac7               a4b0ac7   8c1ebc9cb899ec34…   9a798165a2910a51…   14+6 pass
r20260923-004945-43b5    ligero-verify-e059f14               e059f14   7851fc8f9019c212…   afed32c42cf3682c…   14+7 pass
r20260923-005545-92fc    ligero-verify-01fc64f               01fc64f   8c1ebc9cb899ec34… (= a4b0ac7)  f4cdffe916b939cc…   14+6 pass
r20260923-014449-a599    ligero-verify-381c045               381c045   70430ded59aad49e…   db3476acdba01b6e…   17+7 pass
r20260923-021820-c5b0    ligero-verify-{7bb0ffa,857f722,e059f14} on pod 2: same crate trees; binaries f0466330…/688a1a12…/af2c8032…
~~~

Laptop-side tooling (all under `/tmp/verify/`, nothing in the repo): `orchestrate.py` (`plan | pass | sp1 | census | run | rerun |
label`), `verify_dumps.py` (pod driver), `verify_sp1.py`, `census.py`, `build_lv_multi.sh`, `bootstrap_*.sh`, `verify-export.sh`,
`install_export.sh`, `poll.sh`, `note.py`; ledger `/tmp/verify/ledger.jsonl` (117 rows, rendered in §7).

## 3. Rejections — first, with the verifier's exact error

All five are B-Ligero; each error was identical for every proof of the batch, and each was reproduced on a second run (determinism).

| result | producer (campaign, attempt, commit) | verifier | error (verbatim, first proof) | re-run |
|---|---|---|---|---|
| `art:80961c3170534d59` | r21-b-sweep `r20260922-223541-8985` c135a9c, interactive, 2048 sub-batches, target 2^-128 | `ligero-verify@65434ad` (= producer's), r20260922-232639-6998 | `parameters give 2^-127.54 over 2048 sub-batches (per proof 2^-138.54); requested 2^-128` — 2048/2048 | not possible as a second attempt: the bytes existed only on vy-h100c, terminated before pod 2. The check is pure parameter arithmetic (union bound over 2048 proofs), identical on all 2048 files; the lane's own `verified=ligero-verify` self-label on this result must have used a per-proof bound. |
| `art:ea50b6d029316ac8` | r21-b-hopper `r20260922-223827-8b4b` 11f4120, interactive, 75 proofs | primary `ligero-verify@65434ad`: r20260922-230543-6b66; relation-pinned `@857f722`: r20260923-005819-6a49 | 65434ad: `system file is not the pinned REAL chain system` — 75/75. 857f722: `system file is the pinned bf16-hopper system, the statement is a bf16-ampere statement (sys_id 9dcc7cdc1377a00d..., table digest 74ce68a2801e14fb...)` — 75/75 | yes (two builds, two attempts, same outcome); diagnostic `--allow-any-system` accepts 75/75 (r20260922-231138-a314): valid proofs over a system/statement pairing no pinned verifier accepts (statement written as bf16-ampere, system compiled as bf16-hopper) |
| `art:4601022cb223d477` | r21-ada-fp8-dumps `r20260922-233617-4316` 7bb0ffa, Fiat–Shamir, 147 proofs | `ligero-verify@857f722 +relations`: r20260923-011955-18fa, re-run r20260923-023323-4045 | `statement file: truncated file` — 147/147; also `@7bb0ffa (producer commit)`: `system file is not the pinned REAL chain system` 147/147; `@e059f14 (main HEAD)`: same 147/147 | **yes — identical 0/147 on pod 2 with freshly built binaries** |
| `art:53b01a3e6a10a9a0` | r21-ada-fp8-dumps `r20260922-233507-7fb9` 7bb0ffa, interactive, 147 | same, r20260923-012908-19ab, re-run r20260923-023347-a555 | same three errors | **yes — identical** |
| `art:5421786a4aa18172` | r21-ada-fp8-dumps `r20260922-233711-6b9f` 7bb0ffa, interactive, 147 | same, r20260923-014305-5f1c, re-run r20260923-023412-ba23 | same three errors | **yes — identical** |

Reading of the three ada-fp8-dumps rejections (not investigated further, per spec): the dumps sha256-match their manifests, so
they are what 7bb0ffa wrote; 7bb0ffa's statements are pre-v4 (the relation-pinned reader hits EOF), and the only verifier that
would parse them (7bb0ffa's own) refuses the fp8-ada system by pin. The lane's next commit a4b0ac7 emits v4 statements and its
result `art:f247cd15…` (same relation, same pod) is `accepted` 147/147 under 857f722. So: a format-version drift between the
producer's first commit and every pinned verifier, on three results that are in any case superseded by that lane's later runs.

## 4. Counts

| backend | processed | accepted | rejected | not-transferable | no-dumps |
|---|---|---|---|---|---|
| A-GKR | 29 | 0 | 0 | 0 | 29 |
| B-Ligero | 79 | 10 | 5 | 33 | 31 |
| SP1 | 6 | 4 | 0 | 0 | 2 |
| **all** | **114** | **14** | **5** | **33** | **62** |

By producer campaign: fill-a100 1 accepted / 4 not-transferable; bestvsbest 1 / 1 / 9 no-dumps (vy-h100 and vy-bbb gone);
b-sweep 2 accepted / 16 not-transferable / 1 rejected / 9 no-dumps (6 pruned by `--keep-proofs`, 2 not fetchable, 1 pod gone);
b-hopper 1 rejected / 5 no-dumps (vy-h100b gone); b-merge-h100 2 / 4; a100-dumps 1 / 2; ada-fp8-dumps 1 / 2 / 3 rejected;
ada-ref 2 / 4; auth-included 0 / 5 no-dumps (vy-auth gone); silicon 5 no-dumps (no run-files); SP1 4 accepted / 2 no-dumps;
A-GKR 29 no-dumps (no run-files at all, or run-files without a proof).

Verifier time: B-Ligero 861 s of verifier CPU (`total` summed over 8 522 proofs), 123 s wall across all batches; SP1 0.56 s SDK
verify (+ ~21 s `setup` per proof to re-derive the vk). Attempt-metered cost of all verification runs: $0.44.

## 5. Findings for the coordinator

### 5.1 B-Ligero's headline class is not independently verifiable from dumps (structural)

B-Ligero's Table 2 class is `COMPLETE_ZK_BACKEND` = interactive, malicious-verifier ZK. That is exactly the mode whose transcripts
are live-verifier-only (D7): all 33 interactive dumps are `not-transferable`, which `VERIFIED_LABELS` rightly does not accept. The
Fiat–Shamir variant (`COMPLETE_HVZK_BACKEND`) *is* re-verifiable — 10 such results are `accepted` cold from bytes (fill-a100, b-sweep
×2, a100-dumps, bestvsbest/vy-bvp, b-merge-h100 ×2, ada-fp8-dumps, ada-ref ×2) — but it is a drill-down class for B-Ligero. Under the
contract as frozen, an independently verified B-Ligero headline needs an independent **live** verifier session (an independent party
running `ligero-verify` interactively against the producer's prover, choosing the coins), not a re-verification of bytes. Decide:
arrange that, or let the FS/HVZK cell be the independently verified headline.

### 5.2 The four populated headline cells rest on coordinator `verified=accepted` labels on interactive transcripts

`art:0b9acdf5…` (A100 4.4e7×), `art:799bddfe…` (H100 bf16 1.3e8×), `art:caa80d65…` (H100 fp8 1.2e8×), `art:bf3fe88c…` (4090 5.9e7×)
each carry `verified=accepted --by coordinator` ("verified against the runner's step-0 coins") **and** `verified=not-transferable
--by verify`. `tables` accepts the first because `coordinator` is not a producer, and (since 09824bd) footnotes them "interactive
transcript: not transferable evidence per D7". The bytes are not in dispute — both parties accept them against the dump's coins.
What is in dispute is whether "accepted against the runner's own coins" may be called *verified*: D7 says no. This lane's labels
stand; the coordinator owns the policy call. If the answer is "yes for the headline", `VERIFIED_LABELS` should say so explicitly
rather than rely on a label vocabulary collision.

### 5.3 Producers vs verifiers: three drift findings

1. **Relation lanes' commits cannot verify their own proofs under a pin** (b-merge-h100 01fc64f, ada-fp8-dumps 7bb0ffa/a4b0ac7,
   b-hopper 11f4120): their `ligero-verify` pins only the REAL chain system, so their self-verification ran unpinned. The
   relation-pinned verifier reached main only at 381c045 (~01:40Z). Every relation verdict here records the producer-commit and
   main-HEAD refusals beside it.
2. **b-hopper's statement/system pairing** (`art:ea50b6d0…`): a bf16-hopper system with a bf16-ampere statement — no pinned
   verifier, present or future, accepts that pairing unless one is written to.
3. **b-sweep's 2048-sub-batch point** fails the union bound by 0.46 bit (2^-127.54 vs 2^-128) under the batch-level check that
   main's verifier applies; the lane self-labelled it `verified=ligero-verify` (a value outside the `verified=` vocabulary — a second
   collision on that key).

### 5.4 Dumps: who is not leaving verifiable bytes behind

- **A-GKR: nothing, ever.** 29 results, no proof bytes (27 have no `run-files/v1`; the 2 bestvsbest ones have a 5-file tree with no
  proof). `verity-gkr-verify` had nothing to verify. Tell the A-GKR producers to dump `proof.bin` + statement and upload them.
- **b-sweep prunes what it dumped** (`--keep-proofs N`, c135a9c): 6 results kept only `system.bin` + manifest (384–9225 files
  missing vs the manifest); 2 more (820 and 147 proofs) could not be fetched at all before vy-h100c disappeared.
- **Bytes on pod disk only** (fill-a100, b-sweep, b-hopper, b-merge-h100, bestvsbest, silicon, auth-included): reachable only while the
  pod lives. Cost already paid: bestvsbest Q2 (vy-h100, vy-bbb), b-hopper (5 of 6), auth-included (all 5), silicon (all 5) are
  `no-dumps` because the pods were terminated with the bytes on them. The three `*-dumps`/ada-ref lanes show the fix: upload
  `proofs/` as the run-files tree (0.5–0.8 GB per result is fine).
- **auth-included**: the `+auth` verifier exists and is wired in, but no auth-included dump ever became reachable. If that lane
  re-runs, it must push proof bytes, or verify runs before its pod is terminated.

### 5.5 Fingerprint defects that reject results before verification is even consulted

fill-a100 and b-sweep results are rejected for `profile` None, `B` None, `instances` null, `authentication` None (and class HVZK ≠ ZK
for the FS variants); a100-dumps/ada-fp8-dumps/ada-ref/b-merge-h100 carry proper fingerprints. The verified FS results that *are*
complete (`art:f8afd5b6…` a100-dumps, `art:77ef58df…`/`art:11bb6de7…` b-merge-h100, `art:0553e315…` ada-ref) are exactly the ones that
populate the drill-down cells.

### 5.6 Spec issues met

(a) "fetch to the laptop (small) → scp to the pod" was not possible for most B-Ligero results (bytes not in the store; 0.3–6.5 GB per
result) — replaced by the forced-command pod-to-pod channel; where the bytes *were* in the store, the laptop route worked but is slow
(≈1 MB/s per scp stream; parallel streams used) and the laptop had 5–7 GB of disk free, so trees were staged one at a time and deleted.
(b) `research.remote` raises `SystemExit` on a 404'd pod; any loop over producers must catch it. (c) SP1 `verifier_seconds` is the
SDK's `verify_seconds` (0.13–0.14 s); the ~21 s process wall is `setup` (vk from ELF) and is recorded as `verification.wall_seconds`.
(d) `research data pull` of an attempt with thousands of per-proof JSONs hit the ssh argv limit; `verify_dumps.py` now bundles them
into `verdicts.tar.gz` above 200 files. (e) `research data push` from the lane/verify worktree fails with `table replicas has no
column named verified` — the LocalStore schema moved on main after 65434ad; pushes were done with main's `research`. (f) The first
verification attempt of `art:a69285dd…` (r20260922-214537-03c3) recorded a mistyped result-artifact string; superseded by
r20260922-215011-1822, referenced by no label. (g) One store blob (`verification.json` of r20260922-220505-f618) went missing from the
laptop's objects/ during the disk-full episode; restored byte-identically from the pod before it was terminated. (h) Two early
`rejected` verdicts (2^-80 / 2^-100 sweep points) were the verifier's default 2^-128 target, not the proofs; fixed with
`--soundness-bits` and superseded within the hour — they remain in the label history and in §7's superseded rows.

## 6. Table 2 after the labels (main@5a8a744 `tables.py`, 02:41Z)

~~~text
| Device                 | Datatype / target                                                        | A-GKR | B-Ligero     | SP1 |
| NVIDIA A100 SXM4 80GB  | BF16 sm80.mma.m16n8k16.bf16 · first-campaign-target/2026-09-21           | —     | 4.4e7× [2]   | —   |
| NVIDIA H100 SXM5 80GB  | BF16 sm90.mma.m16n8k16.bf16 · bf16-hopper-mma-draft/2026-09-22           | —     | 1.3e8× [4]   | —   |
| NVIDIA H100 SXM5 80GB  | E4M3 sm90.wgmma.m64n8k32.e4m3 · fp8-hopper-wgmma-draft/2026-09-22        | —     | 1.2e8× [6]   | —   |
| NVIDIA GeForce RTX 4090| E4M3 sm89.mma.m16n8k32.e4m3 · fp8-ada-mma-draft/2026-09-22               | —     | 5.9e7× [8]   | —   |
- drill-down B-Ligero COMPLETE_HVZK_BACKEND on first-campaign-target/2026-09-21:    4.7e7× (art:f8afd5b6…, t.total 1.911 s)   <- verify only
- drill-down B-Ligero COMPLETE_HVZK_BACKEND on bf16-hopper-mma-draft/2026-09-22:    1.4e8× (art:77ef58df…, t.total 1.785 s)   <- verify + coordinator
- drill-down B-Ligero COMPLETE_HVZK_BACKEND on fp8-hopper-wgmma-draft/2026-09-22:   1.2e8× (art:11bb6de7…, t.total 0.7431 s)  <- verify + coordinator
- drill-down B-Ligero COMPLETE_HVZK_BACKEND on fp8-ada-mma-draft/2026-09-22:        6.3e7× (art:0553e315…, t.total 2.402 s)   <- verify only
[2],[4],[6],[8]: COMPLETE_ZK_BACKEND, "verified by coordinator against the runner's step-0 coins (interactive transcript: not
transferable evidence per D7; the Fiat–Shamir variant is)"
~~~

Every drill-down cell is a Fiat–Shamir proof set this lane re-verified cold from bytes (75/75, 25/25, 13/13, 147/147). "not
independently verified" now appears for exactly one candidate (`art:5421786a…`, one of the rejected ada-fp8-dumps@7bb0ffa results) —
every other candidate is either verified or rejected on other grounds.

## 7. Ledger (result → dumps → verifier → verdict → seconds)

Verdict artifacts are the `outputs.result` of each verification attempt (kind `verification-verdict/v1`; `verifier`, `detail`,
`custody`, `also`, per-proof JSON in `verdicts/` or `verdicts.tar.gz`). Labels carry the same facts (`research data labels ART`).

| result | backend | producer attempt (campaign, machine) | mode / class | dumps | verification attempt | verifier | verdict | verifier s | wall s | other builds (recorded, not labelled) |
|---|---|---|---|---|---|---|---|---|---|---|
| `art:95e361b3cdd885dd` | A-GKR | `r20260922-014657-999b` (—, vy-cpu) | — / ARITHMETIC_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:44e92b89e5f115a4` | A-GKR | `r20260922-014821-560c` (—, vy-cpu) | — / ARITHMETIC_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:56ea1a896700a3e4` | A-GKR | `r20260922-014938-14b3` (—, vy-cpu) | — / ARITHMETIC_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:4f2b858159c39229` | A-GKR | `r20260922-020045-0ac2` (—, vy-cpu) | — / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:a1a4fca4053a5085` | A-GKR | `r20260922-020115-8b4e` (—, vy-cpu) | — / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:1083a89aebea2e59` | A-GKR | `r20260922-020128-bb50` (—, vy-cpu) | — / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:b174b5966e6eac33` | A-GKR | `r20260922-053451-03f9` (—, vy-cpu2) | — / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:1fce9758b84efc0c` | A-GKR | `r20260922-053757-3b76` (—, vy-cpu2) | — / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:69bf6e5aa0297a4d` | A-GKR | `r20260922-055358-9f6b` (—, vy-cpu2) | — / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:99b92ffabe52f92e` | A-GKR | `r20260922-064308-006f` (—, vy-cpu2) | — / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:da16570752f70d53` | A-GKR | `r20260922-064620-cf4c` (—, vy-cpu2) | — / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:25143414a8ff3334` | A-GKR | `r20260922-065112-d687` (—, vy-cpu2) | — / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:499d6b7dfead44d4` | A-GKR | `r20260922-065844-2b84` (—, vy-cpu2) | — / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:15387820627a9ee1` | A-GKR | `r20260922-072400-3993` (—, vy-cpu2) | — / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:5c08ad5e713c769a` | A-GKR | `r20260922-073027-abc0` (—, vy-cpu2) | — / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:69b68e039f61157f` | A-GKR | `r20260922-073131-bfd0` (—, vy-cpu2) | — / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:30f5530dda179707` | A-GKR | `r20260922-074606-be7b` (—, vy-cpu2) | — / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:4d4ef873af2e0d88` | A-GKR | `r20260922-075211-dc70` (—, vy-cpu2) | — / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:18c371e8efc6fe48` | A-GKR | `r20260922-075743-78b5` (—, vy-cpu2) | — / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:cbc038aeee5ca35f` | A-GKR | `r20260922-075822-5076` (—, vy-cpu2) | — / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:150f745b126b5115` | A-GKR | `r20260922-080202-8e4d` (—, vy-cpu2) | — / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:9f8962a324423997` | A-GKR | `r20260922-080548-b67d` (—, vy-cpu2) | — / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:0f8347af1a66ba1a` | A-GKR | `r20260922-081106-6067` (—, vy-cpu2) | — / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:32034bbc71a389c0` | A-GKR | `r20260922-101533-20c4` (—, vy-cpu) | — / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:7bb83827de9b0658` | A-GKR | `r20260922-102013-2931` (—, vy-cpu) | — / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:580ddb5fa71cfa10` | A-GKR | `r20260922-102556-cdcc` (—, vy-cpu) | — / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:2fe8ed0c815b72bf` | A-GKR | `r20260922-110557-b462` (—, vy-cpu) | — / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:1d00e1331249eb29` | A-GKR | `r20260922-180844-e013` (r21-bestvsbest, vy-h100) | non-interactive (SHA-256 Fiat-Shamir), non-ZK / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:8b898a8a1eae5b76` | A-GKR | `r20260922-181404-e39d` (r21-bestvsbest, vy-h100) | non-interactive (SHA-256 Fiat-Shamir), non-ZK / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:4199981da3b3863e` | B-Ligero | `r20260922-230746-bd32` (r21-a100-dumps, vy-a100d) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 75 proofs / 413682946 B in store run-files art:0d7c7f77ab... | `r20260923-001652-e5c4` | ligero-verify@65434ad | **not-transferable** | 13.346 | 1.88 | — |
| `art:f8afd5b673ba3968` | B-Ligero | `r20260922-230823-104f` (r21-a100-dumps, vy-a100d) | fiat-shamir / COMPLETE_HVZK_BACKEND | 75 proofs / 577329846 B in store run-files art:2d53baadf1... | `r20260923-004053-cbf2` | ligero-verify@65434ad | **accepted** | 17.744 | 2.49 | — |
| `art:0b9acdf5b4b83f9d` | B-Ligero | `r20260922-231224-54dc` (r21-a100-dumps, vy-a100d) | interactive / COMPLETE_ZK_BACKEND | 75 proofs / 448699208 B in store run-files art:1613a6058b... | `r20260922-235638-b4dd` | ligero-verify@65434ad | **not-transferable** | 13.398 | 1.90 | — |
| `art:53b01a3e6a10a9a0` | B-Ligero | `r20260922-233507-7fb9` (r21-ada-fp8-dumps, vy-ada8) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 147 proofs / 0 B already on vy-verify (from vy-ada8:r2026... | `r20260923-023347-a555` | ligero-verify@857f722 +relations | **rejected** | 0.258 | 0.13 | ligero-verify@7bb0ffa (producer commit): rejected 0/147 (system file is not the pinned REAL chain system x147); ligero-verify@e059f14 (main HEAD): rejected 0/147 (system file is not the pinned REAL chain system x147) |
| `art:4601022cb223d477` | B-Ligero | `r20260922-233617-4316` (r21-ada-fp8-dumps, vy-ada8) | fiat-shamir / COMPLETE_HVZK_BACKEND | 147 proofs / 0 B already on vy-verify (from vy-ada8:r2026... | `r20260923-023323-4045` | ligero-verify@857f722 +relations | **rejected** | 0.259 | 0.15 | ligero-verify@7bb0ffa (producer commit): rejected 0/147 (system file is not the pinned REAL chain system x147); ligero-verify@e059f14 (main HEAD): rejected 0/147 (system file is not the pinned REAL chain system x147) |
| `art:5421786a4aa18172` | B-Ligero | `r20260922-233711-6b9f` (r21-ada-fp8-dumps, vy-ada8) | interactive / COMPLETE_ZK_BACKEND | 147 proofs / 0 B already on vy-verify (from vy-ada8:r2026... | `r20260923-023412-ba23` | ligero-verify@857f722 +relations | **rejected** | 0.269 | 0.14 | ligero-verify@7bb0ffa (producer commit): rejected 0/147 (system file is not the pinned REAL chain system x147); ligero-verify@e059f14 (main HEAD): rejected 0/147 (system file is not the pinned REAL chain system x147) |
| `art:df1f99631dddee3b` | B-Ligero | `r20260922-235542-295b` (r21-ada-fp8-dumps, vy-ada8) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 147 proofs / 551096801 B in store run-files art:c5dff3c62... | `r20260923-013057-3937` | ligero-verify@857f722 +relations | **not-transferable** | 13.325 | 1.92 | ligero-verify@a4b0ac7 (producer commit): rejected 0/147 (system file is not the pinned REAL chain system x147); ligero-verify@e059f14 (main HEAD): rejected 0/147 (system file is not the pinned REAL chain system x147) |
| `art:f247cd1550880e40` | B-Ligero | `r20260922-235643-98f7` (r21-ada-fp8-dumps, vy-ada8) | fiat-shamir / COMPLETE_HVZK_BACKEND | 147 proofs / 832923794 B in store run-files art:66c0ac67f... | `r20260923-014248-b064` | ligero-verify@857f722 +relations | **accepted** | 19.053 | 2.70 | ligero-verify@a4b0ac7 (producer commit): rejected 0/147 (system file is not the pinned REAL chain system x147); ligero-verify@e059f14 (main HEAD): rejected 0/147 (system file is not the pinned REAL chain system x147) |
| `art:8d03e01e21907106` | B-Ligero | `r20260922-235746-0929` (r21-ada-fp8-dumps, vy-ada8) | interactive / COMPLETE_ZK_BACKEND | 147 proofs / 585773489 B in store run-files art:4a37603fb... | `r20260923-011801-d25f` | ligero-verify@857f722 +relations | **not-transferable** | 13.402 | 1.92 | ligero-verify@a4b0ac7 (producer commit): rejected 0/147 (system file is not the pinned REAL chain system x147); ligero-verify@e059f14 (main HEAD): rejected 0/147 (system file is not the pinned REAL chain system x147) |
| `art:4d1d86de6a16b1c2` | B-Ligero | `r20260923-013530-6693` (r21-ada-ref, vy-ada-ref) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 147 proofs / 551109188 B on vy-ada-ref:r20260923-013530-6... | `r20260923-014956-8f16` | ligero-verify@381c045 (main = producer commit; relation-pinned) | **not-transferable** | 13.048 | 1.87 | ligero-verify@857f722 (lane/ligero-verify-relations, same code): not-transferable 147/147 |
| `art:0553e315be32fe37` | B-Ligero | `r20260923-013832-dea1` (r21-ada-ref, vy-ada-ref) | fiat-shamir / COMPLETE_HVZK_BACKEND | 147 proofs / 832936212 B on vy-ada-ref:r20260923-013832-d... | `r20260923-014750-438e` | ligero-verify@381c045 (main = producer commit; relation-pinned) | **accepted** | 18.778 | 2.68 | ligero-verify@857f722 (lane/ligero-verify-relations, same code): accepted 147/147 |
| `art:bf3fe88c905f07a0` | B-Ligero | `r20260923-013925-3a9e` (r21-ada-ref, vy-ada-ref) | interactive / COMPLETE_ZK_BACKEND | 147 proofs / 585785882 B on vy-ada-ref:r20260923-013925-3... | `r20260923-015128-05af` | ligero-verify@381c045 (main = producer commit; relation-pinned) | **not-transferable** | 13.461 | 1.95 | ligero-verify@857f722 (lane/ligero-verify-relations, same code): not-transferable 147/147 |
| `art:5988587ea5209794` | B-Ligero | `r20260923-014018-6e60` (r21-ada-ref, vy-ada-ref) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 147 proofs / 551109176 B on vy-ada-ref:r20260923-014018-6... | `r20260923-015537-3de7` | ligero-verify@381c045 (main = producer commit; relation-pinned) | **not-transferable** | 13.099 | 1.87 | ligero-verify@857f722 (lane/ligero-verify-relations, same code): not-transferable 147/147 |
| `art:98e4fabc4ed9b15c` | B-Ligero | `r20260923-014113-4a0c` (r21-ada-ref, vy-ada-ref) | fiat-shamir / COMPLETE_HVZK_BACKEND | 147 proofs / 832936234 B on vy-ada-ref:r20260923-014113-4... | `r20260923-015719-7ea8` | ligero-verify@381c045 (main = producer commit; relation-pinned) | **accepted** | 18.823 | 2.68 | ligero-verify@857f722 (lane/ligero-verify-relations, same code): accepted 147/147 |
| `art:191ff942a70c4972` | B-Ligero | `r20260923-014211-f9b7` (r21-ada-ref, vy-ada-ref) | interactive / COMPLETE_ZK_BACKEND | 147 proofs / 585785880 B on vy-ada-ref:r20260923-014211-f... | `r20260923-015348-c70f` | ligero-verify@381c045 (main = producer commit; relation-pinned) | **not-transferable** | 13.377 | 1.92 | ligero-verify@857f722 (lane/ligero-verify-relations, same code): not-transferable 147/147 |
| `art:aa3b1ab471a95625` | B-Ligero | `r20260922-225547-7ab5` (r21-auth-included, vy-auth) | interactive / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260923-003453-6f86` | — | **no-dumps** | 0.000 | — | — |
| `art:13017f7d6eb81a4e` | B-Ligero | `r20260922-230019-edaa` (r21-auth-included, vy-auth) | fiat-shamir / COMPLETE_HVZK_BACKEND | none reachable | `r20260923-003453-6f86` | — | **no-dumps** | 0.000 | — | — |
| `art:b6bd5c1eb7f5b7be` | B-Ligero | `r20260922-230845-6c99` (r21-auth-included, vy-auth) | interactive / COMPLETE_ZK_BACKEND | none reachable | `r20260923-003453-6f86` | — | **no-dumps** | 0.000 | — | — |
| `art:a6dbb3b8d46c7eea` | B-Ligero | `r20260922-231353-9010` (r21-auth-included, vy-auth) | interactive / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260923-003453-6f86` | — | **no-dumps** | 0.000 | — | — |
| `art:090f9b8054d9dc76` | B-Ligero | `r20260922-231552-d579` (r21-auth-included, vy-auth) | fiat-shamir / COMPLETE_HVZK_BACKEND | none reachable | `r20260923-003453-6f86` | — | **no-dumps** | 0.000 | — | — |
| `art:ea50b6d029316ac8` | B-Ligero | `r20260922-223827-8b4b` (r21-b-hopper, vy-h100b) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 75 proofs / 0 B already on vy-verify (from vy-h100b:r2026... | `r20260923-005819-6a49` | ligero-verify@857f722 +relations | **rejected** | 0.340 | 0.15 | ligero-verify@65434ad (identical crate tree to producer commit 11f4120): rejected 0/75 (system file is not the pinned REAL chain system x75); ligero-verify@e059f14 (main HEAD): rejected 0/75 (system file is not the pinned REAL chain system x75) |
| `art:0ad68da7243f8008` | B-Ligero | `r20260922-224340-8b34` (r21-b-hopper, vy-h100b) | fiat-shamir / COMPLETE_HVZK_BACKEND | none reachable | `r20260923-003453-6f86` | — | **no-dumps** | 0.000 | — | — |
| `art:759fcf5830aa4add` | B-Ligero | `r20260922-224750-e360` (r21-b-hopper, vy-h100b) | interactive / COMPLETE_ZK_BACKEND | none reachable | `r20260923-003453-6f86` | — | **no-dumps** | 0.000 | — | — |
| `art:ea8bd418bd8b7854` | B-Ligero | `r20260922-230038-1f2a` (r21-b-hopper, vy-h100b) | interactive / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260923-003453-6f86` | — | **no-dumps** | 0.000 | — | — |
| `art:0d0cd47914e6aa9e` | B-Ligero | `r20260922-230307-ee44` (r21-b-hopper, vy-h100b) | fiat-shamir / COMPLETE_HVZK_BACKEND | none reachable | `r20260923-003453-6f86` | — | **no-dumps** | 0.000 | — | — |
| `art:0800188b4ab0fc8c` | B-Ligero | `r20260922-230538-19a5` (r21-b-hopper, vy-h100b) | interactive / COMPLETE_ZK_BACKEND | none reachable | `r20260923-003453-6f86` | — | **no-dumps** | 0.000 | — | — |
| `art:98a0052c6173b13a` | B-Ligero | `r20260923-004423-c660` (r21-b-merge-h100, vy-h100m) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 25 proofs / 133647110 B in store run-files art:63cf870c8f... | `r20260923-012228-ae12` | ligero-verify@857f722 +relations | **not-transferable** | 4.439 | 0.75 | ligero-verify@01fc64f (producer commit): rejected 0/25 (system file is not the pinned REAL chain system x25); ligero-verify@e059f14 (main HEAD): rejected 0/25 (system file is not the pinned REAL chain system x25) |
| `art:77ef58dfb38d5c48` | B-Ligero | `r20260923-004643-5f80` (r21-b-merge-h100, vy-h100m) | fiat-shamir / COMPLETE_HVZK_BACKEND | 25 proofs / 186135246 B in store run-files art:ab4cfa7516... | `r20260923-013136-c7f7` | ligero-verify@857f722 +relations | **accepted** | 5.672 | 0.96 | ligero-verify@01fc64f (producer commit): rejected 0/25 (system file is not the pinned REAL chain system x25); ligero-verify@e059f14 (main HEAD): rejected 0/25 (system file is not the pinned REAL chain system x25) |
| `art:799bddfe3556d34f` | B-Ligero | `r20260923-005105-d308` (r21-b-merge-h100, vy-h100m) | interactive / COMPLETE_ZK_BACKEND | 25 proofs / 145296808 B in store run-files art:c5ad954c0d... | `r20260923-013324-8b25` | ligero-verify@857f722 +relations | **not-transferable** | 4.479 | 0.77 | ligero-verify@01fc64f (producer commit): rejected 0/25 (system file is not the pinned REAL chain system x25); ligero-verify@e059f14 (main HEAD): rejected 0/25 (system file is not the pinned REAL chain system x25) |
| `art:1d80213c4c9510d5` | B-Ligero | `r20260923-005151-a30d` (r21-b-merge-h100, vy-h100m) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 13 proofs / 70911370 B in store run-files art:98b2506468a... | `r20260923-012844-d5ab` | ligero-verify@857f722 +relations | **not-transferable** | 2.909 | 0.49 | ligero-verify@01fc64f (producer commit): rejected 0/13 (system file is not the pinned REAL chain system x13); ligero-verify@e059f14 (main HEAD): rejected 0/13 (system file is not the pinned REAL chain system x13) |
| `art:11bb6de716303fd6` | B-Ligero | `r20260923-005225-f447` (r21-b-merge-h100, vy-h100m) | fiat-shamir / COMPLETE_HVZK_BACKEND | 13 proofs / 98700541 B in store run-files art:5a0a09cd1ac... | `r20260923-012448-622f` | ligero-verify@857f722 +relations | **accepted** | 3.609 | 0.61 | ligero-verify@01fc64f (producer commit): rejected 0/13 (system file is not the pinned REAL chain system x13); ligero-verify@e059f14 (main HEAD): rejected 0/13 (system file is not the pinned REAL chain system x13) |
| `art:caa80d65faf3e626` | B-Ligero | `r20260923-005253-3ff6` (r21-b-merge-h100, vy-h100m) | interactive / COMPLETE_ZK_BACKEND | 13 proofs / 76972751 B in store run-files art:831f1f9a202... | `r20260923-013648-2ff3` | ligero-verify@857f722 +relations | **not-transferable** | 2.857 | 0.47 | ligero-verify@01fc64f (producer commit): rejected 0/13 (system file is not the pinned REAL chain system x13); ligero-verify@e059f14 (main HEAD): rejected 0/13 (system file is not the pinned REAL chain system x13) |
| `art:bae3fcc1f86869d7` | B-Ligero | `r20260922-213247-f7b4` (r21-b-sweep, vy-h100c) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 294 proofs / 1044851786 B on vy-h100c:r20260922-213247-f7... | `r20260922-215748-495f` | ligero-verify@65434ad | **not-transferable** | 22.026 | 3.08 | — |
| `art:4641e267ab631994` | B-Ligero | `r20260922-213354-0e56` (r21-b-sweep, vy-h100c) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 75 proofs / 413695421 B on vy-h100c:r20260922-213354-0e56... | `r20260922-220054-063c` | ligero-verify@65434ad | **not-transferable** | 13.313 | 1.90 | — |
| `art:505294c96af6d4ed` | B-Ligero | `r20260922-213734-86df` (r21-b-sweep, vy-h100c) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 21 proofs / 282565461 B on vy-h100c:r20260922-213734-86df... | `r20260922-221309-a6ad` | ligero-verify@65434ad | **not-transferable** | 12.731 | 1.89 | — |
| `art:a43efa19d60ecb3f` | B-Ligero | `r20260922-213812-eae9` (r21-b-sweep, vy-h100c) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 12 proofs / 288870034 B on vy-h100c:r20260922-213812-eae9... | `r20260922-221412-ca19` | ligero-verify@65434ad | **not-transferable** | 14.270 | 2.48 | — |
| `art:20f80d2fa4103751` | B-Ligero | `r20260922-214058-42e6` (r21-b-sweep, vy-h100c) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 39 proofs / 318426978 B on vy-h100c:r20260922-214058-42e6... | `r20260922-221510-a593` | ligero-verify@65434ad | **not-transferable** | 12.538 | 1.70 | — |
| `art:992705772db9add2` | B-Ligero | `r20260922-214252-b33c` (r21-b-sweep, vy-h100c) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 39 proofs / 318426988 B on vy-h100c:r20260922-214252-b33c... | `r20260922-221607-27dc` | ligero-verify@65434ad | **not-transferable** | 12.480 | 1.69 | — |
| `art:d9887391c2098c63` | B-Ligero | `r20260922-214319-c226` (r21-b-sweep, vy-h100c) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 75 proofs / 413695414 B on vy-h100c:r20260922-214319-c226... | `r20260922-221703-ccdd` | ligero-verify@65434ad | **not-transferable** | 13.206 | 1.87 | — |
| `art:74fb7e4045c2224d` | B-Ligero | `r20260922-214421-6be7` (r21-b-sweep, vy-h100c) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 12 proofs / 97619588 B on vy-h100c:r20260922-214421-6be7/... | `r20260922-222058-5a96` | ligero-verify@65434ad | **not-transferable** | 3.744 | 0.66 | — |
| `art:d746ccba0bd2c618` | B-Ligero | `r20260922-214449-6fea` (r21-b-sweep, vy-h100c) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 147 proofs / 1205996537 B on vy-h100c:r20260922-214449-6f... | `r20260922-222140-ef86` | ligero-verify@65434ad | **not-transferable** | 46.841 | 6.32 | — |
| `art:4a029a9a9fb4a215` | B-Ligero | `r20260922-214610-4de4` (r21-b-sweep, vy-h100c) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 1 proofs / 8545490 B on vy-h100c:r20260922-214610-4de4/pr... | `r20260922-222338-9ce6` | ligero-verify@65434ad | **no-dumps** | — | — | — |
| `art:bde11a76222f0f1e` | B-Ligero | `r20260922-214847-0a45` (r21-b-sweep, vy-h100c) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 1 proofs / 8841363 B on vy-h100c:r20260922-214847-0a45/pr... | `r20260922-222420-2f6e` | ligero-verify@65434ad | **no-dumps** | — | — | — |
| `art:566b388e98a64e70` | B-Ligero | `r20260922-215700-5bc1` (r21-b-sweep, vy-h100c) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 1 proofs / 9904188 B on vy-h100c:r20260922-215700-5bc1/pr... | `r20260922-223133-d28b` | ligero-verify@65434ad | **no-dumps** | — | — | — |
| `art:0db4c28569d82455` | B-Ligero | `r20260922-222741-f7ea` (r21-b-sweep, vy-h100c) | fiat-shamir / COMPLETE_HVZK_BACKEND | 75 proofs / 577342343 B on vy-h100c:r20260922-222741-f7ea... | `r20260922-224726-d857` | ligero-verify@65434ad | **accepted** | 17.088 | 2.41 | — |
| `art:da1168f4f09f14ee` | B-Ligero | `r20260922-222822-2f22` (r21-b-sweep, vy-h100c) | interactive / COMPLETE_ZK_BACKEND | 75 proofs / 448711718 B on vy-h100c:r20260922-222822-2f22... | `r20260922-224848-82c7` | ligero-verify@65434ad | **not-transferable** | 13.209 | 1.86 | — |
| `art:b0eb9f5fa41dde2a` | B-Ligero | `r20260922-222900-192f` (r21-b-sweep, vy-h100c) | fiat-shamir / COMPLETE_HVZK_BACKEND | 39 proofs / 430593755 B on vy-h100c:r20260922-222900-192f... | `r20260922-224956-2542` | ligero-verify@65434ad | **accepted** | 15.518 | 2.09 | — |
| `art:d33ee4c2652d0fe6` | B-Ligero | `r20260922-222938-936a` (r21-b-sweep, vy-h100c) | interactive / COMPLETE_ZK_BACKEND | 39 proofs / 351391036 B on vy-h100c:r20260922-222938-936a... | `r20260922-225104-98f1` | ligero-verify@65434ad | **not-transferable** | 12.526 | 1.71 | — |
| `art:b3888b8bf1ae4577` | B-Ligero | `r20260922-223005-ebe2` (r21-b-sweep, vy-h100c) | fiat-shamir / COMPLETE_HVZK_BACKEND | 1 proofs / 11430755 B on vy-h100c:r20260922-223005-ebe2/p... | `r20260922-225159-b230` | ligero-verify@65434ad | **no-dumps** | — | — | — |
| `art:b5440e7db3964f54` | B-Ligero | `r20260922-223242-d449` (r21-b-sweep, vy-h100c) | interactive / COMPLETE_ZK_BACKEND | 1 proofs / 9406218 B on vy-h100c:r20260922-223242-d449/pr... | `r20260922-225242-75a7` | ligero-verify@65434ad | **no-dumps** | — | — | — |
| `art:6e80c1ff82cd5651` | B-Ligero | `r20260922-223447-90bc` (r21-b-sweep, vy-h100c) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 75 proofs / 296736519 B on vy-h100c:r20260922-223447-90bc... | `r20260922-230302-a655` | ligero-verify@65434ad | **not-transferable** | 8.590 | 1.24 | — |
| `art:2c02d4d4c0d35614` | B-Ligero | `r20260922-223514-57dd` (r21-b-sweep, vy-h100c) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 75 proofs / 368861918 B on vy-h100c:r20260922-223514-57dd... | `r20260922-230219-3698` | ligero-verify@65434ad | **not-transferable** | 12.845 | 1.80 | — |
| `art:80961c3170534d59` | B-Ligero | `r20260922-223541-8985` (r21-b-sweep, vy-h100c) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 2048 proofs / 6127694796 B on vy-h100c:r20260922-223541-8... | `r20260922-232639-6998` | ligero-verify@65434ad | **rejected** | 8.521 | 2.63 | — |
| `art:373d523200e38ca9` | B-Ligero | `r20260922-223948-6358` (r21-b-sweep, vy-h100c) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 1230 proofs / 3796132321 B on vy-h100c:r20260922-223948-6... | `r20260922-230651-7b6a` | ligero-verify@65434ad | **not-transferable** | 63.452 | 9.03 | — |
| `art:2d46e6b1026a4f36` | B-Ligero | `r20260922-224216-f153` (r21-b-sweep, vy-h100c) | fiat-shamir / COMPLETE_HVZK_BACKEND | 1 proofs / 13362657 B on vy-h100c:r20260922-224216-f153/p... | `r20260922-232743-560b` | ligero-verify@65434ad | **no-dumps** | — | — | — |
| `art:7f9260bd9eeb5ccb` | B-Ligero | `r20260922-230654-9512` (r21-b-sweep, vy-h100c) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 75 proofs / 296736514 B on vy-h100c:r20260922-230654-9512... | `r20260922-232830-3076` | ligero-verify@65434ad | **not-transferable** | 8.848 | 1.26 | — |
| `art:9418e28097585dce` | B-Ligero | `r20260922-230741-8ea0` (r21-b-sweep, vy-h100c) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 75 proofs / 368861920 B on vy-h100c:r20260922-230741-8ea0... | `r20260922-232927-253d` | ligero-verify@65434ad | **not-transferable** | 13.002 | 1.82 | — |
| `art:076adaa95e9526a7` | B-Ligero | `r20260922-230808-6267` (r21-b-sweep, vy-h100c) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 820 proofs / 2481166309 B on vy-h100c:r20260922-230808-62... | `r20260922-233029-14eb` | ligero-verify@65434ad | **no-dumps** | — | — | — |
| `art:5494ea3cfd95f995` | B-Ligero | `r20260922-231034-0693` (r21-b-sweep, vy-h100c) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 147 proofs / 1205996541 B on vy-h100c:r20260922-231034-06... | `r20260922-233112-db98` | ligero-verify@65434ad | **no-dumps** | — | — | — |
| `art:6f6e1b52a34b372b` | B-Ligero | `r20260922-231134-43fa` (r21-b-sweep, vy-h100c) | interactive / COMPLETE_ZK_BACKEND | none reachable | `r20260923-003453-6f86` | — | **no-dumps** | 0.000 | — | — |
| `art:dc0b4706b2944653` | B-Ligero | `r20260922-180223-cda6` (r21-bestvsbest, vy-h100) | interactive / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:f2b7b1701884b7fc` | B-Ligero | `r20260922-180414-0585` (r21-bestvsbest, vy-h100) | interactive / COMPLETE_ZK_BACKEND | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:651ac482b87fb129` | B-Ligero | `r20260922-180748-ba52` (r21-bestvsbest, vy-h100) | fiat-shamir / COMPLETE_HVZK_BACKEND | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:0e871445e523a17a` | B-Ligero | `r20260922-182131-5066` (r21-bestvsbest, vy-h100) | interactive / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:86aabd913a7f3255` | B-Ligero | `r20260922-182217-284a` (r21-bestvsbest, vy-h100) | interactive / COMPLETE_ZK_BACKEND | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:b98c1f10dea90c2f` | B-Ligero | `r20260922-182302-3cb0` (r21-bestvsbest, vy-h100) | fiat-shamir / COMPLETE_HVZK_BACKEND | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:56dbfbe30f48122d` | B-Ligero | `r20260922-215131-f3ca` (r21-bestvsbest, vy-bvp) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 75 proofs / 413695342 B on vy-bvp:r20260922-215131-f3ca/p... | `r20260922-222937-05b0` | ligero-verify@65434ad | **not-transferable** | 13.272 | 1.89 | — |
| `art:b2bb25da39c57c98` | B-Ligero | `r20260922-215602-220d` (r21-bestvsbest, vy-bvp) | fiat-shamir / COMPLETE_HVZK_BACKEND | 75 proofs / 577342263 B on vy-bvp:r20260922-215602-220d/p... | `r20260922-223032-2fff` | ligero-verify@65434ad | **accepted** | 17.209 | 2.43 | — |
| `art:34cf7371340969bc` | B-Ligero | `r20260922-233616-f94b` (r21-bestvsbest, vy-bbb) | interactive / COMPLETE_ZK_BACKEND | none reachable | `r20260923-003453-6f86` | — | **no-dumps** | 0.000 | — | — |
| `art:a69285ddd118ca0b` | B-Ligero | `r20260922-212805-8174` (r21-fill-a100, vy-a100c) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 75 proofs / 413695342 B on vy-a100c:r20260922-212805-8174... | `r20260922-215011-1822` | ligero-verify@65434ad | **not-transferable** | 13.530 | 1.92 | — |
| `art:b62c775df94ee1ee` | B-Ligero | `r20260922-213205-0322` (r21-fill-a100, vy-a100c) | interactive / COMPLETE_ZK_BACKEND | 75 proofs / 448711639 B on vy-a100c:r20260922-213205-0322... | `r20260922-215636-b6fa` | ligero-verify@65434ad | **not-transferable** | 13.373 | 1.90 | — |
| `art:1d35a94625bb938a` | B-Ligero | `r20260922-213320-80ff` (r21-fill-a100, vy-a100c) | fiat-shamir / COMPLETE_HVZK_BACKEND | 75 proofs / 577342236 B on vy-a100c:r20260922-213320-80ff... | `r20260922-215934-1fc0` | ligero-verify@65434ad | **accepted** | 16.997 | 2.42 | — |
| `art:81112d8998634a63` | B-Ligero | `r20260922-213412-5f0b` (r21-fill-a100, vy-a100c) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 291 proofs / 1617179869 B on vy-a100c:r20260922-213412-5f... | `r20260922-220204-53e5` | ligero-verify@65434ad | **not-transferable** | 51.405 | 6.96 | — |
| `art:07b352443f94f132` | B-Ligero | `r20260922-213639-6359` (r21-fill-a100, vy-a100c) | interactive / NON_ZK_PROOF_DIAGNOSTIC | 1158 proofs / 6485357368 B on vy-a100c:r20260922-213639-6... | `r20260922-220505-f618` | ligero-verify@65434ad | **not-transferable** | 204.470 | 27.23 | — |
| `art:d801e894471adfe3` | B-Ligero | `r20260922-181917-0877` (r21-silicon, vy-sp1) | interactive / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:aeced929ee1ccfdb` | B-Ligero | `r20260922-182131-1099` (r21-silicon, vy-sp1) | interactive / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:e97ae368df39071b` | B-Ligero | `r20260922-182930-bf16` (r21-silicon, vy-sp1) | interactive / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:26771e6d5442a724` | B-Ligero | `r20260922-183241-a43e` (r21-silicon, vy-sp1) | interactive / NON_ZK_PROOF_DIAGNOSTIC | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:76defa04fef78d53` | B-Ligero | `r20260922-183412-7a35` (r21-silicon, vy-sp1) | fiat-shamir / COMPLETE_HVZK_BACKEND | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:7c43f5bb02d65d54` | SP1 | `r20260921-225340-3d24` (—, vy-sp1) | — / NO_PROOF | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |
| `art:109b72f99e9dcdb8` | SP1 | `r20260922-050209-3eb1` (—, vy-sp1) | core / ARITHMETIC_DIAGNOSTIC | proof.bin 2799064 B in run-files art:316f07125f3585ef | `r20260922-220321-580b` | veritor-zk-host@b96edf6 | **accepted** | 0.142 | 21.13 | — |
| `art:c6a91193bacdb625` | SP1 | `r20260922-050349-3373` (—, vy-sp1) | core / ARITHMETIC_DIAGNOSTIC | proof.bin 2799064 B in run-files art:734e2aec9212c19b | `r20260922-220444-171e` | veritor-zk-host@b96edf6 | **accepted** | 0.134 | 21.16 | — |
| `art:d2826d6c187a1c17` | SP1 | `r20260922-050533-2010` (—, vy-sp1) | core / ARITHMETIC_DIAGNOSTIC | proof.bin 2799064 B in run-files art:aa1dc6ad1dd52857 | `r20260922-220605-2b9c` | veritor-zk-host@b96edf6 | **accepted** | 0.136 | 21.13 | — |
| `art:f301c615a2ce1e17` | SP1 | `r20260922-050711-86b5` (—, vy-sp1) | core / ARITHMETIC_DIAGNOSTIC | proof.bin 2792784 B in run-files art:521ff9a2fe132b52 | `r20260922-220727-97ce` | veritor-zk-host@b96edf6 | **accepted** | 0.144 | 21.48 | — |
| `art:7661874c7392012d` | SP1 | `r20260922-050847-415f` (—, vy-sp1) | — / NO_PROOF | none reachable | `r20260922-220002-d5a6` | — | **no-dumps** | 0.000 | — | — |

Superseded verifications (earlier rows for the same result; the labels carry every assertion, `research data labels ART --history`):

- `art:2c02d4d4c0d35614`: `r20260922-225420-1e08` ligero-verify@65434ad → rejected — 75/75 proofs rejected by ligero-verify: rep1/sub_00.proof: parameters give 2^-100.45 over 25 sub-batches (per proof 2^-105.10); requested 2^-128; rep1/sub_01.pr
- `art:4601022cb223d477`: `r20260923-011955-18fa` ligero-verify@857f722 +relations → rejected — 147/147 proofs rejected by ligero-verify: rep1/sub_00.proof: statement file: truncated file; rep1/sub_01.proof: statement file: truncated file; rep1/sub_02.proo
- `art:53b01a3e6a10a9a0`: `r20260923-012908-19ab` ligero-verify@857f722 +relations → rejected — 147/147 proofs rejected by ligero-verify: rep1/sub_00.proof: statement file: truncated file; rep1/sub_01.proof: statement file: truncated file; rep1/sub_02.proo
- `art:5421786a4aa18172`: `r20260923-014305-5f1c` ligero-verify@857f722 +relations → rejected — 147/147 proofs rejected by ligero-verify: rep1/sub_00.proof: statement file: truncated file; rep1/sub_01.proof: statement file: truncated file; rep1/sub_02.proo
- `art:6e80c1ff82cd5651`: `r20260922-225324-9305` ligero-verify@65434ad → rejected — 75/75 proofs rejected by ligero-verify: rep1/sub_00.proof: parameters give 2^-80.11 over 25 sub-batches (per proof 2^-84.75); requested 2^-128; rep1/sub_01.proo
- `art:ea50b6d029316ac8`: `r20260922-230543-6b66` ligero-verify@65434ad → rejected — 75/75 proofs rejected by ligero-verify: rep1/sub_00.proof: system file is not the pinned REAL chain system; rep1/sub_01.proof: system file is not the pinned REA

## 8. Pods and cost

- vy-verify #1 `dgkx6z1wev7k74`: RTX 4090 24 GB SECURE, 32 vCPU / 125 GB (`nproc` on the pod reports the host's 256), $0.74/h,
  21:39:48Z → 02:15Z = **275 min ≈ $3.39**. 74 attempts. Terminated with 36 GB of fetched dumps on it (the store holds the sha256s and
  verdicts; the bytes belong to the producers).
- vy-verify #2 `a8oeydbj8h3wbp`: RTX 4090 SECURE, 16 vCPU / 62 GB, $0.74/h, 02:18Z → 02:35Z = **17 min ≈ $0.21**, created only to
  give the three ada-fp8-dumps rejections their determinism re-run after #1 was already down (the bytes for those three are in the
  store; the b-sweep rejection's bytes died with vy-h100c). 4 attempts.
- Total **≈ 292 pod-minutes, ≈ $3.60**; never more than one `vy-verify` pod at a time; $50/h ceiling untouched. Both terminated;
  `~/.research/machines.toml` `[machines.vy-verify]` is marked DEAD.
