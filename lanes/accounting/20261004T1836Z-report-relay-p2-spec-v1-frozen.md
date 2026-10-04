---
id: 20261004T1836Z-report-relay-p2-spec-v1-frozen
campaign: pous
lane: accounting
kind: report
status: closed
repo: danielreuter/verity
origin: old-accounting (bc-b729c175), relayed for memory-accounting's 18:25Z question from store:pous/docs/efficient-crypto/p2-spec-draft.md
---

> Relayed verbatim from the Cursor store by old-accounting: `store:pous/docs/efficient-crypto/p2-spec-draft.md`, sha256 `3f49c34bb065af9c11b92935d1460e6f3caf7b12caf6d89560d5c8a7e2725267`, unchanged since it was written, so it is also in `art:8bd64630…42e9` at that path. Only the store's `cursor:` front matter is replaced. Relative and `/cursor/stores/…` links point into that store.

# P2 specification v1, frozen

Status: frozen specification, 2026-09-29. This is not deployment approval: P2 remains experimental because the P2–M1-SGI instantiation assumption is not accepted (default, Daniel deferred, 2026-09-29).

## 1. Parameter set

The frozen deployment parameter set is:

| Item | Value |
|---|---|
| Protocol version | `p2/v1` |
| Width | w = 16,448 bits = 2,056 bytes |
| Prime identifier | `p2-p16448-c21065` |
| Modulus | p = 2^16448 − 21065 |
| Prime congruence | p mod 8 = 7, hence p mod 4 = 3 |
| Primality certificate | ECPP, 339 steps; three independent verifications passed |
| Payload profile | `p2-2054B`: 2,054 bytes = 16,432 bits |
| Deployment store | B = 2^19 blocks, 8 segments of 65,536 blocks |
| Exact-domain abstract family | 2^8 through 2^23 blocks; pinned in the store's `lean/pous` trusted layer |

The congruence certificate is direct integer arithmetic: 2^16448 is 0 mod 8 and 21065 is 1 mod 8, so p is 7 mod 8.

The prime is certified by a 339-step Atkin–Morain/FastECPP certificate produced by Andreas Enge's CM 0.4.4 `ecpp-mpi`, completed 28 Sep 2026 at 22:01Z. The PARI/GP certificate is `internal/efficient-crypto/p2-prime/cm-cert-p16448-c21065`, SHA-256 `6a3f6f1170295adcf73a49733da02e42ff6d96e73bacce666855cc9a5ef1d3c5`. Its Primo-format copy is `cm-cert-p16448-c21065.primo`, SHA-256 `a759215b2ecb294b8516b4069c72bc1f031cd8409c1ceed4833b6dcd9c762244`.

Three independent verifications pass: PARI/GP 2.15.4 `primecertisvalid` returned 1 and confirmed the certificate's first N is exactly `2^16448 − 21065`; CM's `ecpp-check` accepted it; and the campaign's standard-Python-plus-gmpy2 `ecpp_verify.py`, sharing no PARI or CM code, accepted all 339 steps against that target. Logs are `pari-verify-cm.log`, `cm-ecpp.log` and `mine-verify-cm.log` under `internal/efficient-crypto/p2-prime/`. The maintained certificate record is `docs/efficient-crypto/p2-prime-certificate.md`. V1 keeps p without requiring a Lean-checked primality proof; the alternative p′ is unnecessary.

Reduced-width bounty parameters use the same deterministic rule: choose the least positive c0 congruent to 1 mod 4 for which `2^w − c0` passes the stated primality procedure. The draft ladder gives c0 values 189, 17, 173, 237, 189, 317, 569 and 105 at widths 64, 96, 128, 192, 256, 384, 512 and 1024.

## 2. Canonical values, packing and accounting

All field values are canonical integers in `[0,p)`. A w-bit integer is encoded as exactly `w/8` bytes, unsigned, big-endian, including leading zero bytes. Bit number 0 is the least significant bit of that integer. XOR acts on the w-bit binary representations, bit by bit; it is not byte-string concatenation or field addition.

The sole normative deployment profile is `p2-2054B`, with b = 16,432 = 2,054 bytes (default, Daniel deferred, 2026-09-29). Profile names are case-sensitive. The former `p2-16447b` continuous-bit profile is non-normative research material and is not accepted by a deployment manifest.

For `p2-2054B`, `0 ≤ m < 2^16432 < 2^16447 < p`. No sentinel is embedded in m. For a manifest declaring B blocks, W is the concatenation of the exactly 2,054-byte, leading-zero-padded big-endian encodings of `m_0,…,m_(B−1)`, in segment-major then local-block order. Thus W has exactly `2,054·B` bytes. This is both continuous most-significant-bit-first packing and one byte-aligned payload per block; there are no w-bit codeword slots in W.

The manifest commits the profile and B, so the W byte length is determined without a sentinel or padding convention. The field/codeword wire encoding remains the fixed-width format above; implementations reject noncanonical field encodings, wrong widths and decoded values outside the declared payload width.

The exact-domain Lean model `m1p B w p b` treats b as a parameter. The store's `lean/pous` trusted layer pins `P2MeetsM1pB19Uncond`, `P2MeetsM1pFamilyUncond` and `P2MeetsM1pW8192Uncond` for every `20·16448 ≤ 21·b` and `b ≤ 16447`, including b = 16,432. Their repository sync follows PRs #162/#183.

The retained-state threshold is measured against the code, not the payload:

```text
S = floor((18/19) · |C|) = floor((18/19) · B · 16448) bits.
```

It does not change with b. At `p2-2054B`, the 16-bit code expansion is still part of `|C|`.

## 3. Maps

For canonical z in `[0,p)`, define:

```text
d(z) = z² mod p                 when z is even
       (−z²) mod p              when z is odd
```

Since p is 3 mod 4, exactly one of y and −y is a quadratic residue for nonzero y. Define `ρ = d⁻¹`:

1. For y = 0, return 0.
2. Compute `s = y^((p+1)/4) mod p` once.
3. If `s² = y`, return the even member of `{s,p−s}`. If `s² = −y mod p`, return the odd member. Any other result is an error.

For canonical r and full-width mask K in `[0,2^w)`, define the involution:

```text
x = r XOR K
σ_K(r) = x    if x < p
         r    otherwise
```

The rejection branch is mandatory. It must not reduce x modulo p.

For block j with public tweak `t_j ∈ [0,p)` and public mask `K_j ∈ [0,2^w)`:

```text
E_j(m) = ρ(σ_Kj(ρ((m + t_j) mod p)))
D_j(c) = (d(σ_Kj(d(c))) − t_j) mod p
```

`E_j` performs two roots and `D_j` performs two signed squarings. Both consume and return canonical values. `D_j(E_j(m)) = m`.

## 4. Setup and key derivation

The normative setup assumption is **P2-EXP-IO** (default, Daniel deferred, 2026-09-29): after W is committed, setup supplies fresh XOF streams independently for every `(segment, block, purpose)`, independently of the complete pre-setup transcript. Purpose is K or t. Under this idealization, masks are mutually independent uniform w-bit strings and rejection-sampled tweaks are mutually independent uniform elements of `Z_p`; its expander error is zero by definition.

Concrete SHAKE256 replacing P2-EXP-IO is a separate named assumption: **SHAKE256/P2-EXP-IO storage-game idealization**. A deterministic globally fixed SHAKE function does not become a fresh independent-output oracle merely because its input contains a post-commitment salt.

A standard secure PRG is provably insufficient here. Proposition 1 of `internal/efficient-crypto/attacks/p2-seed-expander.md` constructs an ordinary secure locally seekable PRG whose public seed describes every P2 ciphertext for W = 0. Ordinary PRG security therefore cannot replace P2-EXP-IO.

Setup order is load-bearing:

1. Fix W and its exact model manifest. Commit to the bytes, payload bit length, model identifier, protocol version and prime identifier.
2. Only after that commitment is immutable, obtain the first valid unpredictable and unbiasable verifier/beacon source. Bind it; neither party may grind alternatives.
3. Draw one 256-bit setup salt through the pinned `verity.randomness` v1 derivation. The formula below shows the deployment prime id; at any reduced width it is replaced by that parameter set's `p2-p{w}-c{c0}`:

```text
derive(
  source,
  "verity/pous/p2-setup/v1",
  {
    "model": model_commitment_bytes,
    "prime": "p2-p16448-c21065",
    "protocol": "p2/v1"
  }
).value
```

`source` is the verifier secret or beacon round selected after the W commitment, never a prover-selected commitment. `derive` and its typed framing are the existing `verity.randomness` byte format.

4. For each block, form this injective base. `frame` is exactly the typed, length-delimited `verity.randomness.frame`; both integers are unsigned 64-bit big-endian. If global index `i = s·blocks_per_segment + v`, `segment = s` and `local_block = v`: key derivation uses the local within-segment index, never global i.

```text
base =
  frame("verity/pous/p2/expand/v1")
  || frame("p2/v1")
  || frame("p2-p16448-c21065")
  || frame(model_commitment_bytes)
  || frame(setup_salt_256)
  || u64be(segment)
  || u64be(local_block)

mask_stream  = SHAKE256(base || ASCII("K"))
tweak_stream = SHAKE256(base || ASCII("t"))
```

Let n = w/8. K is the first n mask-stream bytes, interpreted big-endian; n = 2,056 at deployment. For t, read consecutive n-byte tweak-stream candidates and accept the first integer below p. This is exact rejection sampling; modulo reduction and “subtract p once” are forbidden.

Every `(segment,block,purpose)` is distinct. Masks must be full-width uniform outputs. Sparse, repeated, truncated, density-conditioned, shared or linear-schedule masks are nonconforming. Setup salts cannot be reused across model commitments. Keys are public, but deployment must expand them where used rather than store a key-sized table that violates the space bound.

5. Encode C and bind the audit verification root. Derive audit challenges only after that root is fixed.

SHAKE256 with this v1 framing is the conforming realization of the separate **SHAKE256/P2-EXP-IO storage-game idealization** (default, Daniel deferred, 2026-09-29). The measured host SHAKE256 cost is about 9.1 µs per P2 block for 4,112 useful bytes, about 2.2× the campaign's 4.2 µs optimized two-squaring IFMA decode. This is a CPU primitive measurement, not an end-to-end deployment benchmark. ChaCha8 would add a weaker reduced-round assumption and is nonconforming.

## Audit protocol and wire formats

This section defines `p2-audit-wire/v1`. Multi-byte integers are unsigned big-endian. Byte strings have exactly the stated length. Receivers reject unknown versions, unknown types, reserved flag bits, noncanonical integers, length mismatches and trailing bytes.

### Parties and transport

The **verifier** commits setup coins, issues each challenge, authenticates responses and decides the audit. The **prover**, acting through its **responder**, stores C and returns challenged encoded blocks.

The transport product is not prescribed. It must provide an ordered, loss-detecting, integrity-protected sequence of delimited frames with one authenticated peer in each role. Each delivery event supplies exactly one frame and its byte boundary; the wire verifier does not infer boundaries by reading the body's declared length from an undelimited stream. The transport must not reorder, duplicate or silently alter frames. The verifier must be able to measure the transport round trip used for the audit's RTT allowance. Confidentiality is not required: setup data, challenges, blocks and paths are public.

Every frame is:

```text
offset  bytes  field
0       4      ASCII "P2AU"
4       1      wire version = 0x01
5       1      message type
6       4      body length, u32be
10      n      body
```

The body length excludes the 10-byte header. `p2-audit-wire/v1` accepts only named profiles with w ≤ 16,448, canonical manifests of at most 512 bytes, `blocks_per_segment ≤ 2^16`, `segments < 2^64`, and k ≤ 105. Deployment setup accepts only `p2-2054B`; reduced-width conformance vectors may use a named `p2-nb` or `p2-nB` test profile. Let n = w/8, B be the manifest block count, h(i,B) be the exact RFC 9162 sibling count, and r be the number of FINAL records. Accepted body lengths are:

| Type | Accepted body length |
|---|---:|
| `SETUP_COMMIT` | exactly `36 + manifest_length`, with `manifest_length ≤ 512` |
| `SETUP_SALT` | 64 |
| `SETUP_BLOCK` | `76 + n` |
| `SETUP_ROOT` | 105 |
| `AUDIT_OPEN` | 92 |
| `CHALLENGE` | 106 |
| `RESPONSE` | exactly `80 + n + 32·h(i,B)` |
| `FINAL` | exactly `118 + 83·r`, with `0 ≤ r ≤ k ≤ 105` |

Thus every accepted profile has an absolute body cap of 8,833 bytes, attained by a 105-record `FINAL`; for the deployment profile at B = 2^19, a RESPONSE is 2,744 bytes. A declared or delivered body outside its type-specific length is malformed code 1, even when below 8,833 bytes.

### Setup commitment, salt and verification root

The setup manifest is canonical UTF-8 JSON using `verity.commitments.identity.canonical_json_bytes`: sorted object keys, no insignificant whitespace, direct Unicode, no floats. It contains exactly `scheme`, `w`, `c0`, `profile`, `blocks_per_segment` and `segments`; `scheme` is exactly the JSON string `"p2"`, `profile` is the case-sensitive profile string, and the other four values are JSON integers. The W commitment reuses the MVP's existing frame:

```text
manifest = canonical_json_bytes(params.manifest())
payload  = u64be(len(manifest)) || manifest || W
w_commitment =
  SHA256(
    ASCII("veritor/tagged-sha256/v1\0")
    || u32be(len("verity-pous/w-commitment/v1"))
    || ASCII("verity-pous/w-commitment/v1")
    || u64be(len(payload))
    || payload
  )
```

W uses exactly the `p2-2054B` packing in §2: segment-major then local-block-major, with each payload in one 2,054-byte leading-zero-padded big-endian encoding. Reduced-width conformance profiles use continuous fixed-b-bit packing, most-significant bit first, with only zero right-padding in the final byte. `SETUP_COMMIT` (`type=0x01`, prover to verifier) has:

```text
u32be(manifest_length) || manifest || w_commitment[32]
```

Only after accepting this frame does the verifier derive the 32-byte setup salt as specified in §4. `SETUP_SALT` (`0x02`, verifier to prover) is:

```text
w_commitment[32] || setup_salt_256[32]
```

For `p2-audit-wire/v1`, `model_commitment_bytes` in §4 is exactly `w_commitment`.

In public-encoder setup, the prover then sends every encoded block in strictly increasing global index using `SETUP_BLOCK` (`0x03`):

```text
w_commitment[32] || setup_salt_256[32] || u64be(global_index)
|| u32be(block_length) || block[block_length]
```

At w = 16,448, `block_length` is 2,056. The verifier rejects gaps, duplicates or out-of-order indices, decodes the stream, checks the reconstructed W commitment, and constructs the verification root. In private-encoder setup the verifier already has W and constructs the same C and root itself; no `SETUP_BLOCK` frames are required.

For global block index `i`, let:

```text
s = floor(i / blocks_per_segment)
v = i mod blocks_per_segment
leaf(i) =
  SHA256(
    0x00 || setup_salt_256[32] || u64be(s) || u16be(v)
    || block_i[2056]
  )
node(left,right) = SHA256(0x01 || left[32] || right[32])
```

The tree is the RFC 6962 shape: for n > 1 leaves, split at the largest power of two strictly below n; preserve global block order. One leaf's root is the leaf itself. The verification root is exactly 32 bytes.

`SETUP_ROOT` (`0x04`, prover to verifier) is:

```text
w_commitment[32] || setup_salt_256[32] || u64be(block_count)
|| verification_root[32] || setup_mode[1]
```

`setup_mode` is 0 for private encoder and 1 for public encoder. The verifier accepts the root only if it equals the root it constructed through the selected MVP setup path.

Both parties compute:

```text
epoch_id =
  SHA256(
    ASCII("verity/pous/p2/epoch/v1\0")
    || u32be(len(manifest)) || manifest
    || w_commitment[32] || setup_salt_256[32]
    || u64be(block_count) || verification_root[32]
  )
```

An epoch id is never reused with a different tuple.

Given a recoverable `AUDIT_OPEN`, a setup failure emits a zero-record `FINAL` whose transcript contains only that open frame. Setup failure codes are:

- code 1 for malformed envelopes or manifests, wrong fixed lengths or setup mode, a noncanonical setup block `≥ p`, nonzero W padding, or another structural/canonicality error;
- code 2 for a `SETUP_SALT`, `SETUP_BLOCK` or `SETUP_ROOT` commitment/salt binding mismatch, a `SETUP_ROOT.block_count` that disagrees with `segments·blocks_per_segment`, or a missing, duplicated, reordered or wrong-index setup block;
- code 3 when decoded blocks reconstruct a different W commitment, or the correctly framed leaves reconstruct a different verification root;
- code 5 when a setup block decodes outside the selected payload profile;
- code 6 only when the transport fails before delivering a required complete setup frame.

The same 1, 2, 3, 5 precedence applies if one setup transcript has multiple faults. When a recorded transcript contains a valid fixed-size `AUDIT_OPEN`, setup transport failure code 6 is recorded as a zero-record `FINAL`: verdict 0, `rounds_completed = record_count = 0`, epoch id, audit id, Δ and RTT copied from `AUDIT_OPEN`, and `transcript_hash = SHA256("verity/pous/p2/transcript/v1\0" || exact AUDIT_OPEN frame)`. No partial setup bytes enter that hash. If no valid fixed-size `AUDIT_OPEN` is available, no interoperable `FINAL` identity exists and the session fails without a `FINAL`; the transport/evidence layer records the setup failure outside this wire format.

### Audit and challenge derivation

`AUDIT_OPEN` (`0x10`, verifier to prover) is:

```text
epoch_id[32] || audit_id[32] || challenge_mode[1] || u16be(k)
|| u64be(delta_ns) || u64be(rtt_allowance_ns)
|| verification_flags[1] || u64be(audit_counter)
```

Wire conformance permits `1 ≤ k ≤ 105`; k = 0 and k > 105 are malformed code 1 and produce a zero-record `FINAL`. A deployment audit sets exactly k = 105; smaller positive values exist only for bounded test vectors. Challenge mode 0 is a designated-verifier secret key; mode 1 is a roundwise beacon. Verification flag bit 0 requests canonical decode checking and bit 1 requests comparison with verifier-held payload. Bit 1 requires bit 0; setting bit 1 alone is malformed code 1. All other bits are reserved and zero.

For mode 0, `source` is a verifier secret never sent to the prover:

```text
id_key = derive(
  source, "verity/pous/audit-id/v1",
  {"counter": audit_counter, "epoch": epoch_id}
)
audit_id = id_key.stream("id", 32)
audit_key = derive(
  source, "verity/pous/audit-challenge/v2",
  {
    "audit": audit_id,
    "epoch": epoch_id,
    "root": verification_root,
    "salt": setup_salt_256
  }
)
i_j = audit_key.uniform(block_count, j)
round_nonce_j = audit_key.stream(("nonce", j), 32)
```

Thus every index is uniform in `[0,B)`, with replacement; j is the integer round index passed to the pinned `verity.randomness` sampler. A fresh audit counter gives a fresh audit id and challenge coordinate. The verifier persists used `(epoch_id,audit_id)` pairs across audits and process restarts and rejects reuse before releasing round 0.

The `verity.randomness` argument types are normative: `counter`, `round` and sampler index j are nonnegative integer parts, `"id"` is a string stream index, and `("nonce",j)` is a tuple containing a string then an integer. They are not pre-encoded `u64be` byte strings.

Mode 1 is valid only with a beacon value `beacon_j` that was unavailable before round j. For each round:

```text
round_key_j = derive(
  beacon_j, "verity/pous/audit-round/v1",
  {"audit": audit_id, "epoch": epoch_id, "root": verification_root, "round": j}
)
i_j = round_key_j.uniform(block_count, j)
round_nonce_j = beacon_j
```

Each `beacon_j` is exactly 32 bytes. In mode 1, the verifier derives `audit_id` with the same `verity/pous/audit-id/v1` formula from a separate verifier secret or opening beacon that is not reused as a round beacon. The verifier records every beacon identifier and verifies its authenticity outside this wire format. A round beacon known at audit opening is not sufficient for sequential unpredictability.

### Challenge and response

`CHALLENGE` (`0x11`, verifier to prover) is:

```text
epoch_id[32] || audit_id[32] || u16be(round_j) || u64be(index_i)
|| round_nonce[32]
```

Deployment rounds are numbered 0 through 104. The receiver checks epoch, audit, round, nonce and the deterministically derived index.

`RESPONSE` (`0x12`, prover to verifier) always carries the block and a root authentication path:

```text
epoch_id[32] || audit_id[32] || u16be(round_j) || u64be(index_i)
|| u32be(block_length) || block[block_length]
|| u16be(path_count) || sibling_0[32] || ... || sibling_(path_count-1)[32]
```

The block is the spec's fixed-width unsigned big-endian encoding; at the deployment point it is exactly 2,056 bytes and must be below p. Siblings are ordered from the leaf toward the root. Direction bits are omitted: RFC 9162 path verification derives left/right from `index_i` and `block_count`. `path_count` must be exactly the count consumed by that verification; for B = 2^19 it is 19. A one-block tree has `path_count=0`. Always carrying a path gives one interoperable root-only format; a verifier that also retains every leaf may still verify the path.

### Sequential reveal and deadlines

The verifier releases round j+1 only after the complete response frame for round j has been received. It stops immediately after any failed round.

For round j, the verifier starts its monotonic clock immediately before handing the first byte of the challenge frame to the integrity-protected transport. It stops when the last byte of the corresponding response frame is received. Parsing and cryptographic verification follow the stop event but malformed and wrong responses still fail.

The on-time condition is:

```text
elapsed_ns ≤ delta_ns + rtt_allowance_ns
```

Equality is on time; one nanosecond above the sum is late. The verifier measures the RTT allowance on the same authenticated transport and records the method and samples. The frozen deployment sets Δ = 0.5 ms with an on-node verifier and permits a measured RTT allowance of at most 1 ms under the hardware/cooperation class in §6. A late, malformed, unauthenticated, replayed, wrong-index, wrong-block or wrong-path response fails the whole audit. There is no partial acceptance.

Only a frame reported as delivered at a transport frame boundary enters the exact frame sequence. A delivered frame whose header declares more or fewer bytes than that delivered frame contains is malformed code 1; its exact delivered bytes are hashed, including the `truncated-response` vector. If the transport ends or reports loss after a challenge without reporting any complete response-frame delivery event, that round fails with transport code 6; unframed partial bytes are not hashed.

Perfect isolation, the `floor((18/19)·|C|)` state cap, accounting of transient/cross-answer state and exclusion of outside help are procedural assumptions. The wire format does not enforce them.

### Response verification and final record

For each response the verifier:

1. validates the envelope, ids, round, index, fixed block length and canonical block `< p`;
2. recomputes the leaf and RFC 9162 path to the epoch's verification root;
3. enforces the strict deadline;
4. when flag bit 0 is set, runs P2 decode and requires a canonical payload for the selected profile;
5. when flag bit 1 is set, also compares that payload with verifier-held expected bytes.

Authentication is mandatory. Decode checks are additional diagnostics once setup has bound the root to committed W.

When one input has multiple faults, the verifier selects exactly one failure in this order: malformed envelope, length or canonicality (code 1); identity, round, index, domain or replay (code 2); authentication (code 3); deadline (code 4); optional decode or payload comparison (code 5). An index outside `[0,block_count)` is code 2. A path byte-count inconsistent with `path_count` is code 1. A RESPONSE can be envelope- and length-consistent yet carry the wrong number of complete siblings; if `path_count` differs from the exact RFC 9162 count for the challenged `(index,block_count)`, it is also malformed code 1, before hashing the path. With the correct count, a path that does not reach the bound root is authentication code 3. The one setup exception is a root that disagrees with verifier-reconstructed setup blocks: this is code 3 before checking `AUDIT_OPEN.epoch_id`, because the declared root itself is unauthenticated.

A malformed challenge emits one failing record with the expected round and derived index, elapsed zero, flags zero, the hash of the exact challenge frame and a zero response hash. A complete malformed response emits one record with its measured elapsed time and exact response hash. Failure before a complete response emits the transport record specified below. A fixed-size `AUDIT_OPEN` with invalid mode, k or reserved verification bits emits a zero-record `FINAL` by reading its identity and timing fields at their fixed offsets; an open frame too malformed to recover those fields is rejected at the transport/session layer and cannot produce a `FINAL`.

The verifier records the exact `AUDIT_OPEN`, challenge and response frames; start, stop and elapsed nanoseconds; RTT evidence; software/image identity; hardware identity; per-round checks; and the final result. This may be attached to a `research` Attempt or another evidence record without changing the bytes below.

Define:

```text
transcript_hash =
  SHA256(
    ASCII("verity/pous/p2/transcript/v1\0")
    || exact AUDIT_OPEN frame
    || exact CHALLENGE_0 frame || exact RESPONSE_0 frame
    || ...
  )
```

`FINAL` (`0x13`, verifier to prover and evidence record) is:

```text
epoch_id[32] || audit_id[32] || verdict[1] || failure_code[1]
|| u16be(rounds_completed) || u64be(delta_ns) || u64be(rtt_allowance_ns)
|| transcript_hash[32] || u16be(record_count) || records
```

Each record is:

```text
u16be(round_j) || u64be(index_i) || u64be(elapsed_ns) || flags[1]
|| SHA256(exact challenge frame)[32] || SHA256(exact response frame)[32]
```

Record flags are bit 0 authenticated, bit 1 on time, bit 2 decode performed, bit 3 decode valid; other bits are zero. Bit 1 is evaluated and set only after authentication succeeds, so a complete on-time response that fails parsing, identity or authentication has flags zero. `rounds_completed` and `record_count` are both the number of emitted round records, including a final failed attempt; a failure before round 0 or in `AUDIT_OPEN` has zero. Verdict is 1 only when all k records authenticate and are on time and every requested optional check succeeds. Failure codes are 0 success, 1 malformed, 2 id/round/index/replay/domain, 3 authentication, 4 late, 5 decode or payload comparison and 6 transport. A complete but invalid response is hashed and included as the failing record. If transport fails before a complete response frame arrives, the failing record uses an all-zero response hash, the transcript ends after that round's challenge, and its flags are zero. Any frame delivered after the expected k exchanges changes the verdict to failure code 2 at stopping round k; `rounds_completed = record_count = k`, and the extra frame is not appended to the transcript hash.

### State isolation and state accounting

This subsection maps the Lean sequential audit game to deployment. It is normative for claims that cite `Pous.Meets` or the P2 exact-domain pins. Let:

```text
|C| = block_count · w
S = floor((18/19) · |C|) bits.
```

The bound is a condition on the adversarial prover quantified by the security guarantee, not a storage rule for the honest prover. The formal conditional claim is: every perfectly isolated prover whose retained state is at most S bits and whose round program is `Prog.Bounded D Q` passes with probability at most `δ + ε`. The honest prover retains all of C and is expected to pass. Its wall-clock interpretation additionally depends on the external calibration and SeqRoot assumption below.

#### Game-to-deployment map

| Lean object | Deployment resource |
|---|---|
| W | the exact committed plaintext model bytes; available to every response round for free |
| pp | the scheme's public parameters; free under the state cap, but `|pp|` is charged by `SpaceBound` |
| public setup | fixed scheme constants are free; a per-setup value is free only if it is part of W or formal pp, is exposed through the modeled public-oracle interface, or is justified by the external concrete-to-ideal reduction |
| `A₁(W,pp,C,ω)` | an arbitrary function of W, pp, all of C and the whole ideal primitive ω; encoder coins are not an input |
| `σ : Bits S` | all non-free information that can survive a round boundary, jointly |
| `step W pp j σ i` | one responder invocation given the round number and current challenge, subject to that answer's formal `(D,Q)` oracle bound |
| returned `Bits S` | the only non-free state allowed to survive for the next round |

For the exact-domain `m1p` pins, pp has width zero. The pins therefore do not themselves make the public verification root, setup salt, concrete K/t representation or authentication metadata free. Fixed constants may be hard-coded; per-setup values require the P2-to-M1p instantiation argument or must be charged. After preprocessing, direct access to C and ω is gone; ω is available online only through the modeled forward-query interface.

The current challenge means `(audit_id, j, i_j, round_nonce)` and the associated public verifier fields. Earlier challenges, responses and revealed C blocks are not fresh free inputs in the Lean game: retaining them for a later round counts unless they are recomputed solely from the true free inputs identified above.

#### What is charged at a boundary

At a state boundary, concatenate every non-free bit available to, controlled by, or queryable by the responder. The resulting retained representation must have at most S bits. Deployment accounting conservatively charges the bytes of every accessible copy; duplicate caches are not deduplicated. It includes:

- GPU HBM and SRAM that survive the round, CPU and pinned host RAM, registers or runtime objects that survive, swap, disk/NVMe, files, object stores and database rows;
- driver, framework, allocator, kernel, filesystem and page caches when their contents depend on C or preprocessing;
- state held by another process, container, VM, device or service that the responder can read or query;
- compressed, coded, encrypted, sparse or indirect representations of C, their indices and metadata, and any non-public decompressor/table;
- prior responses, decoded blocks or decoded weight tiles retained across answers.

A region proven to be a fixed constant or a deterministic function only of the true free inputs adds no information, but any extra annotations or hidden payload in it are charged. A local copy of the exact committed W is free because W is an explicit input to every Lean `step`; an altered copy carrying hints is not. This does not make C free: the aggregate-Q calibration and SeqRoot assumption must separately exclude regenerating a challenged C block from W before its answer deadline.

Reading the exact committed W from local disk or over the verifier's authenticated channel is free. That source must return only W and fixed framing; it cannot be used as a general storage or advice channel. Reading any other disk or network object that encodes C or preprocessing output either charges all information obtainable from it to σ or violates perfect isolation. A public-setup value may be stored or recomputed without charge only when it meets the formal or externally justified free-input rule above.

#### Boundary times and transient work

The state boundary is enforced:

1. after preprocessing and erasure of C, encoder coins and setup secrets, immediately before round 0's challenge; and
2. after the complete RESPONSE for round j has been produced and before CHALLENGE j+1 is released.

There is no unmetered computation gap between rounds. The responder's next-state choice is part of round j. Working memory and local computation within a round are unrestricted by S, matching `Prog`. Before the next boundary, every transient byte must be erased or represented in the counted next state. Temporary files, child processes, GPU allocations, swap, caches and asynchronous work do not become free merely because the response was already sent.

In `Prog.Bounded D Q`, D is the number of adaptive oracle rounds and Q is the total number of modeled forward-oracle queries in one answer, across all cooperating hardware; neither bounds local computation. The P2 pins hold for every D. A deployment claim must separately freeze the hardware/cooperation class, calibrate aggregate Q for the `Δ + RTT` response window, and assume SeqRoot excludes an inverse or equivalent target computation in that same window. The Lean game contains no wall clock: every `(D,Q)`-bounded program is treated as on time.

Cross-answer decoded-block, root, lattice, table or key caches count whenever they contain information not determined by the true free inputs. Reloading a charged object after the boundary does not evade the cap: if it remains reachable, its retained information was part of σ at that boundary.

#### Perfect isolation and evidence

During an audit the responder may communicate only with the authenticated verifier transport, including an exact-W input channel if W is not already local. The deployment must isolate the responder host or VM from other networks, storage services, processes and devices; prevent DMA or peer-device access; bind the responder to an attested image/configuration; and account jointly for every cooperating process and device in the selected hardware class.

The attested image and configuration must be frozen before preprocessing. Any setup-dependent executable, library or configuration payload counts as state. At each boundary, all cooperating processes and devices must be suspended, asynchronous work terminated or joined, transient state erased, and the retained state atomically measured and committed before the next challenge is released.

For each audit the verifier's evidence record must include the attested image and executable hashes; host, device and isolation identity; process/cgroup and device membership; mounted storage and allowed-file policy; network namespace/firewall policy and counters; memory and persistent-file measurements at preprocessing and every boundary; state byte/bit counts and hashes; cache/temporary-state wipe results; child exit status; and per-round timing already required above.

Perfect isolation remains an assumption, not a property of `p2-audit-wire/v1`. The wire format cannot establish that native code did not use DMA, a covert channel, shared kernel/page cache, an unmeasured process, remote storage or false attestation. Production enforcement and independent attestation of those controls remain procedural.

#### MVP and reference harness

In the vLLM/MVP deployment, C is the P2-encoded weight blocks retained for serving, principally in GPU HBM with any host or disk backing also part of the retained deployment state. W is the committed plaintext model and is free in the game. The honest responder retains all of C and answers by lookup; it is outside the S-bit adversarial class. For a capped adversarial run, every encoded or decoded weight cache that survives an answer—including framework cross-invocation caches—counts. The MVP's ordinary in-process objects do not by themselves enforce perfect isolation.

`internal/efficient-crypto/p2-bounty-kit/isolation_harness.py` is the executable small-width reference. Preprocessing runs in one process and may emit only an S-capped state file. State files are byte-granular, so the harness conservatively permits at most `floor(S/8)` bytes. Every round runs in a fresh process with only W, pp, public setup, the prior state and challenge; only the response and next-state files may be written. The harness uses a fresh user/network namespace when available, a deny-network Python audit policy, a cleared environment, per-process address-space/CPU/wall-time limits, fresh temporary directories, an allowed-file scan, and state-size checks after preprocessing and every round.

This harness makes the file/process boundary executable for the included toy Python responders but is not a hostile-native-code sandbox, perfect-isolation implementation or attestation system. Its fallback without user namespaces is only a Python-level diagnostic. It does not isolate native syscalls or the mount/PID namespaces, mediate `/proc`, DMA or peer devices, measure remote state, count oracle depth or queries, enforce the audit wire deadline, or test SeqRoot. Its address-space, CPU and wall-time limits are diagnostic guards, not the Lean `(D,Q)` bound.

`test_isolation_harness.py` has finite scope: it checks only the built-in full-C, raw-cap, side-file, environment and Python-socket strategies. The raw responder stores 18 blocks exactly at the cap. Across 80 fixed-seed toy audits, the test checks that it succeeds exactly when every sampled index is among those 18; the probability `(18/19)^k` follows from the independent with-replacement challenge rule, not from that finite test.

### Audit wire test vectors

`internal/efficient-crypto/p2-bounty-kit/generate_audit_vectors.py` generates `audit-vectors.json`: a complete two-round w=64 setup/audit and one full-width 2,056-byte response. It includes W, setup sources, audit sources and counters, elapsed times and the intermediate values needed to recompute every field. Both small and full-width audit ids use the mode-0 `derive(source,"verity/pous/audit-id/v1",{"counter":counter,"epoch":epoch_id}).stream("id",32)` map above. `generate_audit_negative_vectors.py` generates and self-checks 31 complete negative transcripts in `audit-negative-vectors.json` against `p2_audit_verifier.py`; that file includes the setup source for each setup family. `expected_stop_round` is the failing round, k on success or on an extra post-k frame, and zero for a failure before round 0. The deployment value is k=105; k=2 exists only to keep the conformance vectors small. File and message hashes are listed in §7.

## 5. Audit

- B = 2^19 blocks, arranged as 8 segments of 65,536 blocks.
- k = 105 challenges, revealed and answered sequentially.
- Each answer has Δ = 0.5 ms plus a measured RTT allowance of at most 1 ms, with the verifier on-node.
- Q = 2^20 complete forward decodes per answer in the abstract model.
- The prover's retained state is at most `floor((18/19)·|C|)` bits, where `|C| = B·w`; it is not `(18/19)` of the payload. The state cap applies between answers.
- `P2SlackFamilyUncond` certifies that k = 105 absorbs 128 bits per block of bounded, reusable structural leakage for every B from 2^8 through 2^23.
- Partial, batched, cross-block and expander work is in scope. “No inverse” means no modular root, nor another computation with the same effect on the challenged target, finishes within the answer window.

These values are the frozen F2 and F6 defaults (default, Daniel deferred, 2026-09-29). The audit remains conditional on P2–M1-SGI, SeqRoot, perfect isolation, the exact `[0,p)` model and the allowed hardware.

### Normative error total

The frozen F3 error allocation is (default, Daniel deferred, 2026-09-29):

> A prover that retains at most ⌊(18/19)·|C|⌋ bits beyond W and the public setup between challenges passes an audit
> with probability at most 1% + 2^-128. The 1% is the audit's sampling term, exact in the model. The 2^-128 is a sum of
> four terms:
>
> - (a) **the ideal-model term** ε_ideal ≤ 2^-129, proved in Lean for P2's exact-domain model
>   (`P2ErrorSplitB19Uncond`; the proved bound is far smaller than 2^-129);
> - (b) **the instantiation term** ε_inst ≤ 2^-130, assumed: that square–mask–square behaves like independent ideal
>   permutations in this storage game (P2–M1-SGI);
> - (c) **the challenge-derivation term** ε_chal ≤ 2^-131, assumed: that `verity.randomness` outputs are
>   indistinguishable from uniform;
> - (d) **the expander term** ε_exp = 0 under the setup assumption P2-EXP-IO (F4).
>
> The terms combine additively by a reduction outside Lean, so the total is at most 2^-129 + 2^-130 + 2^-131 < 2^-128.

`P2ErrorSplitB19Uncond` proves this split at k = 104 for B = 2^19. The k = 105 deployment inherits it because one additional sequential challenge can only lower acceptance; this monotonicity step is a paper argument outside Lean.

### Trusted-layer pins

The frozen F5 decision pins `P2SlackB19Uncond`, `P2SlackFamilyUncond` and `P2ErrorSplitB19Uncond` in the store's `lean/pous` trusted layer (default, Daniel deferred, 2026-09-29), together with the exact-domain pins `P2MeetsM1pB19Uncond`, `P2MeetsM1pFamilyUncond` and `P2MeetsM1pW8192Uncond`. Repository synchronization follows PRs #162/#183.

## 6. Operating point and allowed hardware

The frozen operating point is B = 2^19 blocks, Q = 2^20, w = 16,448, Δ = 0.5 ms with an on-node verifier, and a measured RTT allowance of at most 1 ms (default, Daniel deferred, 2026-09-29). The adversary may use a CPU or GPU core with cooperation within one chiplet. ASICs and FPGAs are excluded. The verifier and responder are pinned on the same chiplet. The verifier records the CPU/GPU model, clocks, topology, cooperating cores and measured RTT.

SeqRoot evidence is artifact `art:b92b6d56fa12cc8e04b3f6843991c2e76f49366adc89140a96c33842f70b41ed`, run `r20260929-060834-0ec4`. The fastest measured 16,448-bit root took 12.8 ms with eight cooperating cores. The on-node RTT p99.9 was 10–22 µs. Against the conservative architectural floor, the estimated 2× margin holds through approximately `Δ + RTT = 1.9 ms`, covering the frozen at-most-1-ms RTT allowance. These estimates do not admit cross-chiplet, multi-GPU, FPGA or ASIC cooperation.

## 7. Test vectors

Canonical vectors are in `internal/efficient-crypto/p2-bounty-kit/vectors.json`, generated by `generate_vectors.py` and checked by `test_reference.py`.

For every map entry, its `sha256` is `SHA256(canonical_json_bytes(entry_without_sha256))`, where `canonical_json_bytes` is the function named in the setup section.

- File SHA-256: `781fec77f4fcadb45f10673457ecd9b63d26cf826a2ebaed5da795539d8a5fab`
- w=64 entry: `79897cffa9bdd17db3725d930291df7a85a89c28255e70c0d8c7de529d4458a0`
- w=96 entry: `b1ee454aecc169b1fe8ba80bec1c143f03b9161913abe8b01a0615584317e48f`
- w=128 entry: `7023a475b0c96775bb502cfaaad497cc6ff10c3c50371ae204487b1a537b9f44`
- w=16,448 entry: `9aa7e3893c762763f12f8ada129d03410b3b7a0733cec0174baa6db570f3f3e7`

The file includes explicit sigma rejection-branch cases at w=64 and w=16,448.

Audit wire vectors:

- `audit-vectors.json` SHA-256: `e0e97ddb8b5defaff9cf2e2afd34f543082a3e109b9bae1005e4a1ab74577ac0`
- `audit-negative-vectors.json` SHA-256: `4866941c0f3f866eb39cad1edfbb664569616942c655ba857c66a3e505fceec3`
- w=64 audit-open frame: `77051201e591c140cbefcebd06e797a61807b67783370d67a2525e1f2157a759`
- w=64 round-0 challenge: `d00834ba06ead70dfe74d81ac79905043a275dbb4eaca858e3acbd65459c094d`
- w=64 round-0 response: `490a09e1b8914070199105d63426406659028a6f0de1f93332b827bf28ac0324`
- w=64 final frame: `0196df55c207fa6d29f2642fab8511b2567d3f292a6e8eeb68f6ec4bcabafcf1`
- w=16,448 response frame: `d9cb4f51957a0a458327d8f89dfabd898bcb7b487c6e64881f6bb9a307c3240d`

## 8. Conformance against the fetched MVP branch

Compared with `origin/cursor/pous-mvp-interface-c934` at fetched revision `13b308fc6f9511788918be45ec92770b2307514f`:

| Topic | Frozen v1 | MVP branch | Result |
|---|---|---|---|
| Payload width | `p2-2054B`, 2,054 bytes = 16,432 bits | 2,054 bytes = 16,432 bits | Conforms |
| W packing | concatenated 2,054-byte big-endian payloads | concatenated 2,054-byte payloads | Conforms |
| Integer wire order | fixed-width big-endian | P2 v2 is fixed-width big-endian | Conforms |
| Expander | P2-EXP-IO; concrete SHAKE256 with v1 framing | SHAKE256 segment seed, then ChaCha8 stream | Deviation |
| Tweak sampling | rejection below p | rejection below p | Conforms |
| Derivation context | version, prime, model, setup salt, segment, block, purpose | P2 seed domain plus `salt || u64(segment)`; block is ChaCha nonce | Deviation |
| Mask | fresh full-width per block | fresh full-width per block | Conforms in shape |
| Rejection branch | return r when `r XOR K ≥ p` | same | Conforms |
| Maps | parity-signed square; one exponentiation per ρ | same outputs; MVP fallback performs a second exponentiation for nonresidues | Output conforms; implementation cost deviates |
| Setup order | W commitment, salt/source, encoding, vk, audit key | generic protocol commits W before `draw_salt`; audit key follows vk | Conforms |
| Exact domain | canonical `[0,p)` with b = 16,432; exact-domain pins are trusted in the store | code rejects `c ≥ p`; metadata says the `m1p` pin is proposed | Code conforms; MVP metadata awaits the PR #162/#183 repository sync |
| Certificate size | B=2^19 and pinned 2^8–2^23 family | P2 v2 exposes 8 × 2^16 = 2^19 and cites `P2MeetsM1pB19Uncond` as proposed | Geometry conforms; theorem status is stale |
| Challenge count | k = 105, with 128-bit-per-block structural-leakage margin | certificate and verifier use k = 88 | Deviation; migrate to `P2SlackFamilyUncond`/k = 105 |
| W commitment | tagged SHA-256 over canonical manifest and W | same `verity-pous/w-commitment/v1` | Conforms |
| Verification tree | RFC 6962 shape, SHA-256 0x00 leaves/0x01 nodes | same shape and hash tags | Structure conforms |
| Leaf framing | 32-byte P2 setup salt; u64be segment; u16be local index | 24-byte generic salt; concatenated tag uses little-endian; u16le local index | Deviation |
| Challenge derivation | audit/epoch-bound v2; audit counter; nonce; optional roundwise beacon | `verity/pous/audit-challenge/v1`, bound only to root and 24-byte salt; `uniform(B,j)` | Sampler conforms; replay/domain binding extended |
| Audit messages | canonical framed network messages; response always includes path | in-process Python calls; block alone by default, optional path for root-only verifier | New wire format; MVP has no serialization |
| Negative wire behavior | 31 byte-exact cases pin setup failures, parsing, k bounds, flag dependencies, sibling counts, replay, post-k frames, authentication, deadlines and transport failures | no serialized negative corpus or `FINAL` failure-code implementation | New executable conformance layer |
| Sequential timing | first challenge byte sent through last response byte received | in-process `challenge()` through `respond()` | Same strict sequencing; clock boundary is newly frozen |
| Hardware and deadline | Δ = 0.5 ms, RTT allowance ≤ 1 ms, cooperation within one chiplet allowed, same-chiplet pinning | Δ = 0.5 ms, `ROOT_CALL_NS=2.9 ms`, cooperating cores excluded | Deviation; migrate calibration and topology policy |

The branch names `p2-16448/v2`, uses `p2-2054B`, big-endian P2 values, exact tweak rejection and B = 2^19. It still uses ChaCha8, k = 88, stale pin status, the generic 24-byte salt/Merkle framing, an unnecessary second exponentiation in ρ's nonresidue branch, the old hardware calibration and in-process audit objects rather than the v1 network wire format.

## 9. Freeze checklist

Every item below is normative. A policy choice is not a substitute for the corresponding pinned artifact or executable check.

- [x] Archive and independently verify the ECPP certificate for the exact p: both certificate hashes and all three passing verification records are pinned in §1 and `docs/efficient-crypto/p2-prime-certificate.md`.
- [x] Freeze payload profile `p2-2054B` and the corresponding exact-domain `m1p` pins.
- [x] Freeze B, k, Q, Δ, round-trip accounting and the allowed hardware/cooperation class together; the SeqRoot run and margin pins are cited in §§5–6.
- [x] Allocate ideal-model, expander and concrete-instantiation errors with the normative `1% + 2^-128` total in §5.
- [x] Freeze P2-EXP-IO, the concrete SHAKE256/P2-EXP-IO assumption, v1 expander framing and vectors.
- [x] Specify challenge derivation after vk through `verity.randomness`, including versioned domains, audit/epoch binding, round indices and sequential beacon requirements (`p2-audit-wire/v1`).
- [x] Specify root authentication and RFC 9162 inclusion paths, reusing the MVP's tree structure with P2's canonical framing.
- [x] Specify complete setup, audit-open, challenge, response and final-record frames, including failure behavior.
- [x] Specify replay prevention and domain separation across models, epochs, audits, segments, blocks and rounds.
- [x] Specify and test state isolation: the normative subsection above maps the Lean state and boundaries to deployment, and `internal/efficient-crypto/p2-bounty-kit/isolation_harness.py` with `test_isolation_harness.py` passes its full-C, 18/19 raw-storage, over-cap, side-file, environment and network controls. Native-code/OS isolation, GPU/DMA and cache wiping, aggregate resource measurement, attestation and verifier evidence collection remain procedural deployment controls.
- [x] Specify deadline clock boundaries, strict failure behavior, RTT allowance input and transcript evidence, including the frozen numerical Δ/RTT/hardware choice and SeqRoot evidence.
- [x] Obtain byte-for-byte interoperability results from two independent implementations of `p2-audit-wire/v1`: `internal/efficient-crypto/p2-audit-wire-interop.md` reports zero mismatches for `vectors.json` SHA-256 `c40af08a1f125ee7acbef128230b4d0e073556d306bba45261b8fac07d74b297`, `audit-vectors.json` SHA-256 `2b74b1f19ffd875562ed39f08009150631f94d0dd1fdba660fbb411a01871c49`, and `audit-negative-vectors.json` SHA-256 `257c5666129ace01fd0fa1cc7ec286d130bee0d90897c13c6185c5fe1f5709dd`.
- [x] Add negative conformance cases for malformed encodings, setup failures, replayed challenges, wrong domains, failed authentication paths and late answers: 31 complete transcripts are generated and self-checked in `internal/efficient-crypto/p2-bounty-kit/audit-negative-vectors.json`; its hash is listed in §7.
- [ ] Migrate the MVP implementation and evidence path to every frozen-v1 requirement in the conformance table.

## 10. Decisions (frozen)

1. F1: `p2-2054B` is the sole deployment payload profile (default, Daniel deferred, 2026-09-29).
2. F2: B = 2^19, Q = 2^20, w = 16,448, Δ = 0.5 ms, RTT allowance at most 1 ms, and same-chiplet cooperation and pinning as §6 (default, Daniel deferred, 2026-09-29).
3. F3: the normative error total and allocation in §5 (default, Daniel deferred, 2026-09-29).
4. F4: accept P2-EXP-IO, realized by SHAKE256 with v1 framing; ChaCha8 is nonconforming (default, Daniel deferred, 2026-09-29).
5. F5: pin `P2SlackB19Uncond`, `P2SlackFamilyUncond` and `P2ErrorSplitB19Uncond` (default, Daniel deferred, 2026-09-29).
6. F6: k = 105, absorbing 128 bits per block of structural leakage over B = 2^8 through 2^23 (default, Daniel deferred, 2026-09-29).
7. Keep p = 2^16448 − 21065 under its ECPP certificate, without requiring a Lean-checked primality proof (default, Daniel deferred, 2026-09-29).
8. Do not accept P2–M1-SGI; P2 remains experimental despite this frozen specification (default, Daniel deferred, 2026-09-29).

## 11. Remaining before deployment

- Migrate the MVP to frozen v1 as listed in the conformance table.
- Measure SHAKE256 key derivation on the deployment device.
- Accept P2–M1-SGI.
- Synchronize the trusted-layer pins into the repository after PRs #162/#183.
