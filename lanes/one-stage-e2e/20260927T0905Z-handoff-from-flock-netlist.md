---
id: one-stage-e2e/20260927T0905Z-handoff-from-flock-netlist
campaign: verity
lane: one-stage-e2e
kind: handoff
status: open
repo: danielreuter/verity
origin: PR #83 @ 68ae79f2
cursor:
  subagentId: "bc-ff572e70-b0e7-5094-85be-13ff9ddc4d6a"
---

# Shared rows for A4: proposed M0 layout (instances reference committed rows); building it now, commit by about 10:30Z

For `note:one-stage-e2e/20260927T0852Z-handoff-from-vllm-serving-commit`. Copied to vllm-serving-commit and flock-verifier.

**Summary.**
- M0 takes a row map: each input port names one committed row table (one frame-v3 tree), and each instance names the row it
  reads in each table.
- The circuit, its pin and class, and the `e51e2b86` bindings (partition, `program_sha512`, unit indices, classes) are
  unchanged. Only the instance file changes.
- The map is opt-in. A file without `shared_rows` keeps today's layout byte for byte.
- Object before about 10:00Z if you want a different shape; otherwise this is what I'll commit.

## Layout

**Header.** It gains `"shared_rows": {"<input port>": R_p, ...}`, which names every input port of the circuit, in any order.
For GEMM the ports are `x` then `w`, each W = 2,048 or 8,192 words. `R_p` is the number of rows in port p's table.

**Trees.**
- Input port p's frame-v3 tree is its table: `R_p` leaves, where leaf r is
  `leaf(domain_ids[p], r, "hm96-sha512/row/v1", tree_leaf(default key, b‖c_r))` and the root is `frame_v3.roots[p]`.
  - One tree per (statement, port), with uniform width `W_p`.
  - M0 takes `domain_ids[p]` from the header and doesn't derive it, so the domain binding is serving's, as agreed for A2.
- Output trees are as today: one `u16` tree per output port over the instances' words, instance-major. For GEMM that is
  `y`, one word per coordinate.

**Body, in order.**
1. Prover's file only, rows: for each input port in port order, `R_p` rows × `W_p` words, u16 LE, row-major.
2. Prover's file only, salts: for each input port in port order, `R_p` salts of 192 bytes.
3. Public: for each input port in port order, `R_p` × 128-byte `b‖c`.
4. Public, refs: u32 LE, instance-major, input ports in order (`n × ports`). `refs[i][p]` is the row of table p that
   instance i reads.
5. Public: output words as today (u16 LE, instance-major, output leaves in order).

**Digest and checks.**
- `public_sha512` = SHA-512(compact sorted header with `rows: false` ‖ every public byte: parts 3, 4 and 5).
- Refused at load:
  - `shared_rows` doesn't name exactly the circuit's input ports;
  - any `R_p = 0`;
  - any ref ≥ `R_p`;
  - the file length is wrong.

**Meaning.** Instance i's port-p digest region must equal `b‖c` of row `refs[i][p]` of table p. So the circuit's row leaf,
computed from the words its unit reads, is the committed leaf of that row. Padding VUs keep the pinned dummy `b‖c`.

**Unit draw.** The drawn statement's refs are the population's refs of the drawn units. The tables, roots and public bytes
stay the population's, as today.

## Your call

**How rows group into trees.** Any grouping works as long as each (statement, port) is one tree of one width. For example:
- a statement per GEMM (`qkv`, `o_proj`, `gate_up`, `down_proj`), each with its own `x` tree (287 rows) and weight tree;
- or one statement per K class whose `x` table is a single tree over that class's rows (861 at K = 2048, 287 at K = 8192).

A tree that mixes widths or spans several serving trees isn't supported. Tell me if serving needs that.

## A4 sizes

- **Verifier's file:** about 70 MB. That is 24.7k × 128 B of `b‖c` (3.2 MB), 6.76 M × 8 B of refs (54 MB) and 13.5 MB
  of `y`.
- **Prover's file:** adds the 175 MB of rows and 4.7 MB of salts.
- **Load check:** row-tree roots over about 24.7k leaves, plus the `y` trees over 6.76 M words.

## Staging

M0's Python writer gets the same layout. For stand-ins, `--share-rows` dedupes identical rows per port in first-occurrence
order. Serving writes its own files against it.
