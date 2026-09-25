#![cfg_attr(feature = "guest", no_std)]
//! jolt-scout VU guest: B VUs of `GemmCoordinate<1536>` (A100 BF16), each an x row then a W row of 384 u64 words.
//! mode 0: the relation-bare statement (every y[i] is VU i's output word).
//! mode 1: mode 0 plus the SHA-256 digest of every row (3072 bytes each, the frame-v3 SHA-256 row-leaf work the
//!         committed path does in-proof; tag bytes omitted), returned as public output for a native tree check.
extern crate alloc;
use alloc::vec::Vec;

pub mod kernel;
use kernel::ROW_WORDS;

fn row_bytes(r: &[u64]) -> &[u8] {
    // SAFETY: u64 -> u8 reinterpretation of an initialised slice; RISC-V is little-endian like the frame-v3 layout
    unsafe { core::slice::from_raw_parts(r.as_ptr() as *const u8, r.len() * 8) }
}

#[jolt::provable(
    heap_size = 16777216,
    stack_size = 65536,
    max_input_size = 4194304,
    max_output_size = 65536,
    max_trace_length = 16777216
)]
fn vu_batch(rows: Vec<u64>, y: Vec<u16>, mode: u8) -> (bool, Vec<[u8; 32]>) {
    let n = y.len();
    let mut ok = rows.len() == n * 2 * ROW_WORDS;
    let mut digests = Vec::new();
    if ok && mode == 1 {
        jolt::start_cycle_tracking("rowhash");
        for r in rows.chunks_exact(ROW_WORDS) {
            digests.push(jolt_inlines_sha2::Sha256::digest(row_bytes(r)));
        }
        jolt::end_cycle_tracking("rowhash");
    }
    jolt::start_cycle_tracking("kernel");
    for (i, vu) in rows.chunks_exact(2 * ROW_WORDS).enumerate() {
        if !ok {
            break;
        }
        ok = kernel::check_vu(&vu[..ROW_WORDS], &vu[ROW_WORDS..]) == Some(y[i]);
    }
    jolt::end_cycle_tracking("kernel");
    (ok, digests)
}
