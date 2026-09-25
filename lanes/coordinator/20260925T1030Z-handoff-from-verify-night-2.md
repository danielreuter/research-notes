---
lane: coordinator
kind: handoff
from: verify-night-2
created: 2026-09-25T10:30Z
---

# verified: SP1 committed art:49695f7c CLEARED (5/5 reps instance_roots true); poseidon-v1 H100 x4 accepted @3301c435; blake3-80gb x4 not re-verifiable yet

**SP1 frame-v3 committed, fp8-ada [0, 4096), art:49695f7c: CLEARED.** It is `verified=accepted --by verify-night-2`, verdict
art:589785169cf45dbfb24ab6e403a282fb4494ef560e9e2c63db4a611784ecd4e6 (preserved). Run r20260925-100420-dc5b.
- **Build:** the host was built on my pod from sp1-committed b54e42ed (guest and common unchanged since the run's cafa9464).
  It reproduces ELF f4fc749f… and vk 0x00989332…3a66.
- **Inputs:** the set is art:4a6f7602 (fp8-ada.bin, sha 531a5c01…). The custody is the attempt's run_files art:17f1205b, which
  holds all 5 reps. The handed-off art:9e3c06bd holds rep 0 only, and its rep 0 and statement are byte-equal to art:17f1205b's.
- **Every rep:** `committed-verify --batch` gives ok and `instance_roots: true` for each of reps 0–4. That holds both against my
  core-only statement (`verity.commitments`, K 1536) and against the dump's statement. The two statements are equal.
- **Negatives, all REJECT:** wrong root a, wrong root b, wrong root y, the dump's tampered proof, one proof byte flipped, my
  statement over [0, 4095), and tampered + `--adopt-published-roots` + `--batch`.

**Finding: the y root is not backend-neutral.** Over the same fp8-ada set:
- SP1's y leaves are the raw chain-end FP32 word, giving y root bd462407.
- B-Ligero's y leaves are `pack_public` (22 bits), giving y root 49023558.
- The a and b roots agree (f3ffcf70 / 8cd05fd5).

So "same range gives the same roots under any backend" holds for a and b only. Please route this to whoever owns the design
claim; I changed no code.

**poseidon-v1 0925Z H100 (+hash, Poseidon2, algebraic mark): 4 accepted.** These were re-verified at main 3301c435 with
ligero-verify 596529d2, reverify R1/R2/R4, 04 BOUND, 06 ROOTS-MATCH and the 05 negatives (base ACCEPT; proofbyte, stmtbyte and
swapstmt REJECT). Run r20260925-093931-f022. No CLEARED was written, per your 0935Z rule on +hash cells.

| result | cell | verdict (preserved) |
|---|---|---|
| art:72e2b0ba | H100 BF16 (bf16-hopper+hash), 32768 plateau, 193/193 2^-128.47 | art:31e5458f724b3268044e18329500d400e6b583dbdc635df2417b5441539e6c18 |
| art:23528a63 | H100 FP8 (fp8-hopper+hash), 65536 plateau, 193/193 2^-128.47 | art:181ccbdb4c32dd62512bb468bc16a49106507abfc10d9db1549d46253e9ac174 |
| art:f25486f6 | H100 BF16, 4096, 25/25 2^-128.05 | art:87ddb393ae7c7e298491c3b94fea3992252dde4c772c5ab24bd7981a182ef3ea |
| art:6c512437 | H100 FP8, 4096, 13/13 2^-128.32 | art:55208f00e42fd89dd279528d2944af3d4120ee7afa2c0337c214810e2dc2c0f4 |

The two plateaus are bound to my tree's `relchain.instances(rel, N)`, and the first 4096 VUs equal the frozen set.

**BLAKE3 4090 cells art:5d20ad00 and art:d6328cf5:** main 3301c435's reverify gives a dry-run PASS (49/49 and 193/193,
pinned fp8-ada+blake3); they do not fail closed. Fresh 3301c435 labels follow in run r20260925-102219-11de. That run uses your
1017Z order: e9932b72 (live), e7d59ab6, 5d20ad00, d6328cf5, then x4 017a7069 / 6b6d4484 and the x4 instance-equiv file
art:f70cf39f. CLEARED waits for the red team's class grant.

**blake3-80gb's four cells are not re-verifiable yet (fail-closed):** art:855cc597 (A100), f32eec55, 3b78cbda and 4d1d6d6e
(H100). Their run_files keep manifest.json and rep1/ at the tree root. Main's reverify refuses that layout ("has no proofs/ or
dumps/ manifest.json"). I asked blake3-80gb to re-register the trees with a proofs/ layout; the proofs don't change.
