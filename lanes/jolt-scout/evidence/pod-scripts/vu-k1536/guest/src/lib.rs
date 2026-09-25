#![cfg_attr(feature = "guest", no_std)]
//! jolt-scout VU guest: B VUs of `GemmCoordinate<1536>` (A100 BF16), each an x row then a W row of 384 u64 words
//! (3072 bytes each, little-endian), passed as one byte buffer so postcard copies it in bulk.
//! mode 0: the relation-bare statement (every y[i] is VU i's output word).
//! mode 1: mode 0 plus the SHA-256 digest of every row (the frame-v3 SHA-256 row-leaf work the committed path does
//!         in-proof; tag bytes omitted), returned as public output for a native tree check.
//! mode 2: mode 0 plus the keyed-BLAKE3 digest of every row (frame-v3's keyed-BLAKE3 row leaf; fixed key here),
//!         through the BLAKE3 compression inline (`compress_direct` made `pub` on the pod: the SDK hashes <= 64 B).
extern crate alloc;
use alloc::vec::Vec;

pub mod kernel;
use kernel::ROW_WORDS;

pub const ROW_KEY: [u8; 32] = *b"jolt-scout frame-v3 row key 0001";

fn words_le(b: &[u8; 32]) -> [u32; 8] {
    core::array::from_fn(|i| u32::from_le_bytes(b[4 * i..4 * i + 4].try_into().unwrap()))
}

fn parent(key: &[u32; 8], l: &[u32; 8], r: &[u32; 8], root: bool) -> [u32; 8] {
    use jolt_inlines_blake3::{compress_direct, FLAG_KEYED_HASH, FLAG_PARENT, FLAG_ROOT};
    let mut block = [0u8; 64];
    for i in 0..8 {
        block[4 * i..4 * i + 4].copy_from_slice(&l[i].to_le_bytes());
        block[32 + 4 * i..36 + 4 * i].copy_from_slice(&r[i].to_le_bytes());
    }
    let mut h = *key;
    compress_direct(&mut h, &block, 0, 64, FLAG_PARENT | FLAG_KEYED_HASH | if root { FLAG_ROOT } else { 0 });
    h
}

/// `blake3::keyed_hash(key, input)` for a non-empty input, one compression inline per 64-byte block and parent node.
pub fn blake3_keyed(key: &[u8; 32], input: &[u8]) -> [u8; 32] {
    use jolt_inlines_blake3::{compress_direct, FLAG_CHUNK_END, FLAG_CHUNK_START, FLAG_KEYED_HASH, FLAG_ROOT};
    let key = words_le(key);
    let n_chunks = input.len().div_ceil(1024);
    let mut stack: Vec<[u32; 8]> = Vec::new();
    let mut cv = key;
    for (ci, chunk) in input.chunks(1024).enumerate() {
        let last_chunk = ci + 1 == n_chunks;
        let n_blocks = chunk.len().div_ceil(64);
        let mut h = key;
        for (bi, block) in chunk.chunks(64).enumerate() {
            let mut f = FLAG_KEYED_HASH;
            if bi == 0 {
                f |= FLAG_CHUNK_START;
            }
            if bi + 1 == n_blocks {
                f |= FLAG_CHUNK_END;
                if n_chunks == 1 {
                    f |= FLAG_ROOT;
                }
            }
            compress_direct(&mut h, block, ci as u64, block.len() as u32, f);
        }
        if last_chunk {
            cv = h;
        } else {
            stack.push(h);
            let mut total = ci + 1;
            while total & 1 == 0 {
                let r = stack.pop().unwrap();
                let l = stack.pop().unwrap();
                stack.push(parent(&key, &l, &r, false));
                total >>= 1;
            }
        }
    }
    while let Some(l) = stack.pop() {
        cv = parent(&key, &l, &cv, stack.is_empty());
    }
    let mut out = [0u8; 32];
    for i in 0..8 {
        out[4 * i..4 * i + 4].copy_from_slice(&cv[i].to_le_bytes());
    }
    out
}

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
    if ok && mode == 2 {
        jolt::start_cycle_tracking("rowhash-blake3");
        for r in bytes.chunks_exact(8 * ROW_WORDS) {
            digests.push(blake3_keyed(&ROW_KEY, r));
        }
        jolt::end_cycle_tracking("rowhash-blake3");
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
