---
id: r21-verify/verify/20260922T2230Z-report-verify
campaign: r21-verify
lane: verify
kind: report
status: SUPERSEDED by 20260923T0245Z-report-verify.md (final report; this interim note kept for the record, its placeholders were never filled)
repo: verity-main@65434ad (lane/verify = main, no code changes)
branch: lane/verify (worktree ~/projects/verity-main-wt/verify; nothing committed)
machine: vy-verify (RunPod dgkx6z1wev7k74, RTX 4090 24 GB SECURE, 32 vCPU / 125 GB, $0.74/h, created 2026-09-22 21:47Z)
decision: independent verification of every Table 1 candidate result's proof dumps (three-table contract, verification predicate)
---

# verify: the independent verifier — every candidate result's proof bytes, re-verified by the Rust verifiers on vy-verify

## 1. What this lane did

Under the frozen three-table contract a result may only populate Table 2 if a label `verified=accepted` (or
`independently_verified=true`) is asserted by someone who is **not** its producer (`tables._verified_by`: the asserter is not the
attempt's `execution.campaign` and not an asserter of the result's `candidate=`/`label=` labels). Every lane had verified its own
proofs; nothing in the store satisfied the predicate. This lane produced no benchmarks; it fetched the proof bytes each candidate
result left behind, verified them with the **independent Rust verifiers** on a pod, published each verification as a
`research run --on vy-verify` attempt (result kind `verification-verdict/v1`, campaign `r21-verify`), and labelled the results
`verified=… verifier=… verifier_seconds=… verify_note=… --by verify --ref <verification run>`. Never `candidate=`, `proof_class=`
or `label=`, so `verify` is a producer of nothing.

Verdict vocabulary (label `verified=`):

- `accepted` — every dumped proof re-verified cold from bytes by the independent verifier at the producer's commit.
- `rejected` — a proof the verifier refused; error recorded, re-run once (determinism), reported first. **None occurred.**
- `not-transferable` — interactive-mode B-Ligero transcripts: the dump carries the runner's coins, and the verifier accepts the
  transcript against those coins, but per `ligero-verify/DISCREPANCIES.md` D7 an interactive transcript is live-verifier-only
  evidence (the re-verifier cannot know the coins were the verifier's and not the prover's). Not a failure; not evidence either.
- `no-dumps` — no proof bytes reachable: never dumped, dumped but pruned, or dumped on a pod that no longer exists.

## 2. Method (and what the spec assumed that was not so)

**Where the bytes actually were.** The spec assumed dumps live in each attempt's `run-files/v1` artifact. For B-Ligero they do not:
`backends/direct/ligero/bench_result.py` (used by fill-a100, b-sweep, bestvsbest, silicon) stores only `proofs/manifest.json`
(paths + sha256 + bytes of every `.stmt/.proof/.coins` and of `system.bin`); the proof files themselves stay in the producer pod's
`/workspace/research/runs/<run>/proofs/`. So "fetch to the laptop → scp to the pod" was replaced by a **pod-to-pod channel**:

- vy-verify holds a dedicated keypair (`/root/.ssh/verify_export`); its public key is installed on each live producer pod's
  `authorized_keys` as a **forced command** (`/usr/local/bin/verify-export.sh`, `no-pty,no-port-forwarding,no-agent-forwarding`)
  that answers exactly two verbs: `list` (run dirs that have `proofs/`) and `<run id>` (`tar -cf - proofs` of that run). Read-only by
  construction; nothing else can be executed with that key. Installed on vy-a100c, vy-h100c and (automatically, when its first
  result appeared) vy-bvp.
- The pod-side driver `verify_dumps.py` streams the tar, then **checks the sha256 of every fetched file and of `system.bin` against
  the result's own `proofs/manifest.json`** (fetched from the store by the laptop and shipped with the job). Any mismatch or missing
  file ⇒ `no-dumps` (never a partial verdict). Custody is recorded in the verdict artifact (`custody.matched/mismatched/missing`,
  `system_matches`, `manifest_identical`).
- Verification: `ligero-verify verify --system system.bin --stmt X.stmt --proof X.proof [--coins X.coins]` per sub-batch proof,
  8 processes × 4 threads (`--coins` only for interactive dumps). `verifier_seconds` = the sum of the verifier's own timing
  (`total`) over all proofs; `wall` = elapsed for the parallel batch. A rejection would be re-run once.
- The store never sees credentials: the laptop does store queries/labels only; pods see no R2 key.

**Verifier identity vs producer commit.** For every B-Ligero result processed, `backends/ligero-verify` at the producer's source
commit (fill-a100 915baf9, b-sweep c135a9c, bestvsbest b48dfbb/c013f6f, silicon 4bf0c4f) is **byte-identical** to main's
(65434ad; `git diff --stat <commit> 65434ad -- backends/ligero-verify` empty), so `ligero-verify@65434ad` *is* the verifier at
the producer's commit — the "build both, report drift" clause has nothing to report. The lane/auth-included extended verifier
(0ddc2c9: `auth.rs`, statement v3 / proof v2, Rust SHA-256 word trees + Merkle multiproof check) is built as
`/workspace/bin/ligero-verify-auth` (sha256 `b15f389d97d97b72…`, 18/18 tests pass) and is selected automatically for results whose
fingerprint says `authentication=included` or whose campaign is an auth lane; none had landed by the time of this note.
`backends/gkr/verifier` (`verity-gkr-verify`) is built too; no A-GKR dumps exist to feed it (§4). SP1: `backends/sp1` at the
producer commit b96edf6 differs from main only in README.md; the CPU-SDK host built with the results' guest feature
(`unsound-relation-only`) **reproduces the producer's guest identity exactly** — `elf_sha256 616100249a681540…`,
`vk_hash 0x00776ea1156af4fa…` — so `veritor-zk-host verify --proof` re-derives the same verifying key the producer proved under.

Binaries on vy-verify (from `verify.bootstrap` r20260922-214102-8ad9, `verify.sp1.bootstrap` r20260922-215615-95ef,
`verify.auth.bootstrap` r20260922-221543-e49a):

~~~text
ligero-verify@65434ad                         sha256 4215e8ab6f35e4c6929a55e3a7dad839d3e0e0ad51a236469b6b31137fd4e7fe  (cargo test --release: all pass)
verity-gkr-verify@65434ad                     built; unused (no A-GKR dumps)
veritor-zk-host@b96edf6 (sp1-sdk 6.4.0, CPU, unsound-relation-only)  sha256 3d44e1a01c8794c5501b0f53e51aaaa46c8bc00268c1aa84bdb0cc0ae3214615
ligero-verify@0ddc2c9 +auth (lane/auth-included)                     sha256 b15f389d97d97b725f1a4d5264bd1cb74353900576ee352815ab30d64527fee0
~~~

Laptop-side orchestration: `/tmp/verify/orchestrate.py` (`plan | pass | sp1 | census | run | label`), `verify_dumps.py`,
`verify_sp1.py`, `census.py`, `verify-export.sh`, `install_export.sh`, `poll.sh`; ledger `/tmp/verify/ledger.jsonl` (rendered in §5).

## 3. Counts

COUNTS_TABLE

Rejections: **none**. No proof the verifiers could read was refused.

## 4. Findings for the coordinator

1. **No Table 2 cell is populated, and none was blocked on verification.** After these labels the canonical tables
   (`tables --root ~/.research/store`) reject every one of the candidate results for reasons *other than* verification; the
   string "not independently verified" no longer appears anywhere in the output. The verification predicate is now satisfied for
   the 5 `accepted` results (`reject_reasons` no longer lists it for them); they fail on other frozen rules (below).
2. **B-Ligero cannot satisfy the frozen contract from dumps — structural.** B-Ligero's Table 2 class is `COMPLETE_ZK_BACKEND`
   (interactive, malicious-verifier ZK). That is exactly the mode whose transcripts are live-verifier-only (D7): every interactive
   dump here is `not-transferable`, which `VERIFIED_LABELS` rightly does not accept. The transferable Fiat–Shamir variant
   (`COMPLETE_HVZK_BACKEND`) *is* re-verifiable — the one FS result, fill-a100 `art:1d35a946…` (B = 4096 A100, 75/75 proofs accepted
   cold from bytes), is the only B-Ligero result in the store an independent party has ever verified — but it is only a drill-down
   class for B-Ligero. Under the contract as frozen, B-Ligero's headline cell needs an independent **live** verifier session
   (an independent party running `ligero-verify` interactively against the producer's prover, choosing the coins), not a re-verification
   of bytes. Decide: arrange that, or let the FS/HVZK cell be the independently-verified headline.
3. **fill-a100 and b-sweep results are rejected on fingerprint fields, not on verification.** The verified FS result is rejected for:
   `profile` missing (None), `B` None (the label says `batch=4096` but the fingerprint does not), `instances` null, `authentication`
   None, and (class) HVZK ≠ ZK. 24 of the 62 candidate results fail first on `profile None`. Those lanes' `bench_result.py`
   fingerprints are incomplete for the tables; they need `profile`, `B`, `instances` (the frozen set) and `authentication=excluded`.
4. **Nobody uploads proof bytes.** `bench_result.py` puts only `proofs/manifest.json` in `run-files/v1`; the bytes stay on the pod.
   Consequence already paid: every h100-bestvsbest Q2 result (6 B-Ligero + 2 A-GKR) and every r21-silicon B-Ligero result is
   `no-dumps` because vy-h100 / vy-sp1 were terminated with the bytes on them. Live pods were reachable only through the export
   channel above. If independent verification is to be routine, lanes must push the proof files (or the verify lane must run before
   pods are terminated).
5. **b-sweep prunes what it just dumped.** `--keep-proofs N` (c135a9c) deletes the `.stmt/.proof/.coins` after the lane's own
   verifier passes; for the two largest sweeps (193 and 769 sub-batches; `art:4a029a9a…`, `art:bde11a76…`) only `system.bin` +
   manifest remained → `no-dumps`. The manifest still lists every sha256, so this is detectable, but nothing is verifiable.
6. **A-GKR lanes dumped nothing.** All 27 A-GKR results from vy-cpu / vy-cpu2 have no `run-files/v1` artifact at all; the two
   bestvsbest A-GKR results have a run-files tree (5 files) with no proof. `verity-gkr-verify` had nothing to verify.
7. **SP1's four proofs verify, but attest little.** All four `proof.bin` (core mode, sp1 6.4.0) verify under the re-derived vk, with
   public values equal to the producer's expected `sha256(input) || sha256(output word) || 0xEE`. The guest is the
   `unsound-relation-only` DIAGNOSTIC build (`unsound=true`), K = 1536 or 16, B = 1, ran on an RTX 4090: valid proofs of the wrong
   relation for Table 2 (`ARITHMETIC_DIAGNOSTIC`, B = 1, no `security.target`, no `instances`, wrong SKU). `software.git` / `backend.commit`
   are null in their fingerprints; the commit came from the attempt's `source.commit`.
8. **Which running lanes are NOT dumping proofs** (as of this note): A-GKR producers (none dump); b-sweep dumps then prunes above
   `--keep-proofs`; fill-a100 / b-sweep / bestvsbest dump to pod disk only (no upload). No `auth-included` or `b-hopper`
   `bench-result/v1` had landed in the store during the poll window, so nothing is known about their dumps.
9. **Spec nits.** (a) "fetch to the laptop (small) → scp to the pod" is not possible for B-Ligero (bytes not in the store; 0.3–6.5 GB per
   result — the biggest fetch, 6.5 GB, took 410 s pod-to-pod). (b) `research.remote` raises `SystemExit` on a 404'd pod, which needs
   catching in any loop over producers. (c) The SP1 `verifier_seconds` label is the SDK's `verify_seconds` (0.13–0.14 s); the process
   wall (~21 s) is dominated by `setup` (deriving the vk from the ELF) and is recorded in the verdict artifact as
   `verification.wall_seconds`. (d) The first verification attempt of `art:a69285dd…` (r20260922-214537-03c3) recorded a mistyped
   result-artifact string (correct producer run, wrong artifact id); it is superseded by r20260922-215011-1822 and is not referenced
   by any label.

## 5. Ledger (result → dumps → verifier → verdict → seconds)

LEDGER_TABLE

Verdict artifacts are the `outputs.result` of each verification attempt (kind `verification-verdict/v1`; `verifier`, `detail`,
`custody`, per-proof JSON in `verdicts/` for B-Ligero). All r21-verify attempts and their artifacts are PRESERVED on the remote
(`research data push <run ids>`, 122/122 objects verified).

## 6. Table 2 after the labels

TABLES_SECTION

## 7. Pod

POD_SECTION
