lane: flock-netlist · kind: handoff · from: salted-leaves · created: 2026-09-26T22:25Z

# SHA-512 data commitments: hm96-sha512/v1 needs a 192-byte salt and a 256-byte key, and the key is never a witness

Daniel decided on SHA-512 on every commitment path (re-baseline prerequisite E4). Core now has the SHA-512 forms in
[PR #93](https://github.com/danielreuter/verity/pull/93), stacked on #88, all opt-in:
- `hm96-sha512/v1`;
- the row digest `sha512/row/v1`, with a 128-byte constant prefix block;
- `frame-v3-sha512` and `vllm-v1-sha512`.

**For your serving row leaf and `flock-leaf/hm96-sha512`:**
- **Sizes.** The salt is 192 bytes (1,536 bits) and the key 256 bytes (2,047 bits). Your current reservations are 128 and 160.
- **Circuit cost.** The gadget computes the SHA-512 inner digest, then 2 SHA-512 compressions for c (116,240 ANDs at 58,120 per
  compression), then `b = x ⊕ M·y` over 512 × 1,536 (400,193 XORs for the pinned key). It publishes `b ‖ c`, 128 bytes.
- **The key.** It is fixed and public: SHA-512 counter mode over `verity/hm96-sha512/key/v1\0` (hm96 §2a). It must be a circuit
  constant or a public input checked against `scheme_digest`, never a witness (hm96 §5; red-team-hm96 finding 6).
- **Wording.** Correcting my 20:34Z note: salts from your ChaCha20 stream are modelled as uniform like the OS generator's. The hiding
  is "statistical given uniform salts"; only custody differs.
- **Vectors:** `hm96/vectors_sha512.json`, `frame_v3/vectors_sha512.json` and `vllm_v1/vectors_sha512.json`.
