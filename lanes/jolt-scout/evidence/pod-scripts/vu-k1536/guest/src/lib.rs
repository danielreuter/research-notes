#![cfg_attr(feature = "guest", no_std)]
//! jolt-scout VU guest: B VUs of `GemmCoordinate<1536>` (A100 BF16), each an x row then a W row of 384 u64 words
//! (3072 bytes each, little-endian), passed as one byte buffer so postcard copies it in bulk.
//! mode 0: the relation-bare statement (every y[i] is VU i's output word).
//! mode 1: mode 0 plus the SHA-256 digest of every row (the frame-v3 SHA-256 row-leaf work the committed path does
//!         in-proof; tag bytes omitted), returned as public output for a native tree check.
extern crate alloc;
use alloc::vec::Vec;

pub mod kernel;
use kernel::ROW_WORDS;

#[jolt::provable(
    heap_size = 33554432,
    stack_size = 65536,
    max_input_size = 8388608,
    max_output_size = 65536,
    max_trace_length = 67108864
)]
fn vu_batch(rows: serde_bytes::ByteBuf, y: Vec<u16>, mode: u8) -> (bool, Vec<[u8; 32]>) {
    let n = y.len();
    let bytes: &[u8] = &rows;
    let mut ok = bytes.len() == n * 16 * ROW_WORDS;
    jolt::start_cycle_tracking("words");
    // SAFETY: every bit pattern is a u64; a misaligned buffer falls back to a copy
    let (head, aligned, tail) = unsafe { bytes.align_to::<u64>() };
    let copied: Vec<u64>;
    let words: &[u64] = if head.is_empty() && tail.is_empty() {
        aligned
    } else {
        copied = bytes.chunks_exact(8).map(|b| u64::from_le_bytes(b.try_into().unwrap())).collect();
        &copied
    };
    jolt::end_cycle_tracking("words");
    let mut digests = Vec::new();
    if ok && mode == 1 {
        jolt::start_cycle_tracking("rowhash");
        for r in bytes.chunks_exact(8 * ROW_WORDS) {
            digests.push(jolt_inlines_sha2::Sha256::digest(r));
        }
        jolt::end_cycle_tracking("rowhash");
    }
    jolt::start_cycle_tracking("kernel");
    for (i, vu) in words.chunks_exact(2 * ROW_WORDS).enumerate() {
        if !ok {
            break;
        }
        ok = kernel::check_vu(&vu[..ROW_WORDS], &vu[ROW_WORDS..]) == Some(y[i]);
    }
    jolt::end_cycle_tracking("kernel");
    (ok, digests)
}
